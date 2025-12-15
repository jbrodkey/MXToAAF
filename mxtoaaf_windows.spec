# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_all

block_cipher = None

try:
    project_root = Path(__file__).resolve().parent
except NameError:
    # __file__ may be undefined in some build invocations; fall back to CWD
    project_root = Path(os.getcwd()).resolve()

binaries_dir = project_root / "binaries" / "windows"

# Bundle Windows binaries (ffmpeg.exe and ffprobe.exe - essentials build is self-contained)
extra_binaries = [
    (str(binaries_dir / "ffmpeg.exe"), "binaries"),
    (str(binaries_dir / "ffprobe.exe"), "binaries"),
]

# Shared data files
common_datas = [
    ("docs/README_windows.md", "docs"),
    ("icons/win/MXToAAF.ico", "icons/win"),
]

hiddenimports = [
    "tkinter",
    "mxto_aaf.aaf",
    "aaf2",
    "aaf2.auid",
    "aaf2.rational",
    "aaf2.misc",
]
hiddenimports += collect_submodules("aaf2")

# Also collect all aaf2 package data/binaries via hook utility
_aaf2_datas, _aaf2_binaries, _aaf2_hidden = collect_all("aaf2")
hiddenimports += _aaf2_hidden

a = Analysis(
    ["mxto_aaf_gui.py"],
    pathex=[str(project_root)],
        binaries=extra_binaries + _aaf2_binaries,
    datas=common_datas + _aaf2_datas,
    hiddenimports=hiddenimports,
    hookspath=["hooks"],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MXToAAF",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icons/win/MXToAAF.ico",
)
