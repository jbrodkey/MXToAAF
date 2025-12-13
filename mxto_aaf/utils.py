"""Utilities for MXToAAF workspace package"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys


def _get_ffmpeg_path() -> str | None:
    """Get path to ffmpeg, checking bundled version first, then system PATH.
    
    When built with PyInstaller, ffmpeg is bundled in the 'binaries' directory
    relative to the executable. Fall back to system PATH if not found.
    """
    # Check for bundled FFmpeg (set by PyInstaller via --add-data)
    if getattr(sys, 'frozen', False):
        # App is running as PyInstaller bundle
        base_path = sys._MEIPASS
        
        # Check platform-specific bundled FFmpeg
        if os.name == 'nt':  # Windows
            bundled_ffmpeg = os.path.join(base_path, 'binaries', 'ffmpeg.exe')
        else:  # macOS, Linux
            bundled_ffmpeg = os.path.join(base_path, 'binaries', 'ffmpeg')
        
        # Debug: print what we're checking (will appear in console/logs)
        print(f"[DEBUG] Checking for bundled FFmpeg at: {bundled_ffmpeg}")
        print(f"[DEBUG] File exists: {os.path.isfile(bundled_ffmpeg)}")
        print(f"[DEBUG] Base path (_MEIPASS): {base_path}")
        
        # List what's actually in the binaries directory
        binaries_dir = os.path.join(base_path, 'binaries')
        if os.path.isdir(binaries_dir):
            print(f"[DEBUG] Contents of binaries directory:")
            for item in os.listdir(binaries_dir):
                print(f"[DEBUG]   - {item}")
        else:
            print(f"[DEBUG] Binaries directory does not exist: {binaries_dir}")
        
        if os.path.isfile(bundled_ffmpeg):
            print(f"[DEBUG] ✓ Using bundled FFmpeg: {bundled_ffmpeg}")
            return bundled_ffmpeg
        else:
            print(f"[DEBUG] ✗ Bundled FFmpeg not found, falling back to system PATH")
    
    # Fall back to system PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        print(f"[DEBUG] Using system FFmpeg: {system_ffmpeg}")
    else:
        print(f"[DEBUG] ✗ FFmpeg not found in system PATH either")
    return system_ffmpeg


def ffmpeg_available() -> bool:
    return _get_ffmpeg_path() is not None


def convert_to_wav(src_path: str, dst_path: str, samplerate: int = 48000, bits: int = 24, channels: int = 2) -> None:
    if not ffmpeg_available():
        raise FileNotFoundError("ffmpeg not available in PATH")

    ffmpeg_path = _get_ffmpeg_path()
    
    # Force standard PCM WAV format (not EXTENSIBLE)
    # -write_cue 0: Don't add cue points
    # The key is to use -acodec pcm_s16le for 16-bit or pcm_s24le for 24-bit
    # and avoid extensible format by using 16-bit as fallback if needed
    cmd = [
        ffmpeg_path,
        "-y",                    # Overwrite output file
        "-i", src_path,         # Input file (auto-detect format)
        "-f", "wav",            # Force output format to WAV
        "-acodec", "pcm_s16le",  # Use 16-bit PCM (more compatible, standard format)
        "-ar", "48000",          # 48kHz sample rate
        "-ac", "2",              # Stereo
        dst_path,               # Output file
    ]

    # On Windows, add the binaries directory to PATH so FFmpeg can find DLLs
    env = os.environ.copy()
    if os.name == 'nt' and getattr(sys, 'frozen', False):
        binaries_dir = os.path.dirname(ffmpeg_path)
        env['PATH'] = binaries_dir + os.pathsep + env.get('PATH', '')
        print(f"[DEBUG] Added to PATH for DLL loading: {binaries_dir}")

    print(f"[DEBUG] Running FFmpeg conversion: {' '.join(cmd)}")
    try:
        # On Windows, hide the console window to prevent flashing cmd.exe windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        # Don't suppress output initially - capture both stderr and stdout for debugging
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, env=env, startupinfo=startupinfo)
        
        if result.returncode != 0:
            # FFmpeg failed
            error_msg = result.stderr + result.stdout if (result.stderr or result.stdout) else f"FFmpeg exited with code {result.returncode}"
            print(f"[DEBUG] FFmpeg error output: {error_msg}")
            raise RuntimeError(f"FFmpeg failed to convert {src_path}: {error_msg}")
        
        print(f"[DEBUG] FFmpeg conversion completed successfully")
        
        # Verify output file was created
        if not os.path.exists(dst_path):
            raise RuntimeError(f"FFmpeg produced no output file at {dst_path}")
        
        file_size = os.path.getsize(dst_path)
        print(f"[DEBUG] Output file verified: {dst_path} ({file_size} bytes)")
        
        if file_size < 100:  # Sanity check - WAV file should be much larger
            raise RuntimeError(f"FFmpeg output file is suspiciously small ({file_size} bytes) - conversion likely failed")
        
        # Wait a moment for file system to flush the data (especially important on Windows)
        import time
        time.sleep(0.5)
        
        print(f"[DEBUG] WAV file ready for processing")
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or str(e)
        print(f"[DEBUG] FFmpeg error output: {error_msg}")
        raise RuntimeError(f"FFmpeg failed to convert {src_path}: {error_msg}") from e


__all__ = ["ffmpeg_available", "convert_to_wav"]
