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
        
        if os.path.isfile(bundled_ffmpeg):
            return bundled_ffmpeg
    
    # Fall back to system PATH
    return shutil.which("ffmpeg")


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

    subprocess.run(cmd, check=True)


__all__ = ["ffmpeg_available", "convert_to_wav"]
