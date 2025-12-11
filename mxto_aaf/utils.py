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

    # prefer explicit codec for 24-bit
    codec = "pcm_s24le" if bits == 24 else "pcm_s16le"
    cmd = [
        _get_ffmpeg_path(),
        "-y",
        "-v",
        "error",
        "-i",
        src_path,
        "-ar",
        str(samplerate),
        "-ac",
        str(channels),
        "-acodec",
        codec,
        dst_path,
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or str(e)
        raise RuntimeError(f"FFmpeg failed to convert {src_path}: {error_msg}") from e


__all__ = ["ffmpeg_available", "convert_to_wav"]
