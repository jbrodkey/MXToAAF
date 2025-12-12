# -*- mode: python ; coding: utf-8 -*-

from glob import glob
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

project_root = Path(__file__).parent
binaries_dir = project_root / "binaries" / "windows"

# Bundle all Windows binaries (ffmpeg.exe, ffprobe.exe, and DLLs)
extra_binaries = [
    (str(binaries_dir / "ffmpeg.exe"), "binaries"),
    (str(binaries_dir / "ffprobe.exe"), "binaries"),
]
dll_binaries = [(str(path), "binaries") for path in binaries_dir.glob("*.dll")]

# Shared data files
common_datas = [
    ("LICENSES.txt", "."),
    ("docs/README_windows.md", "docs"),
    ("icons/win/MXToAAF.ico", "icons/win"),
]

hiddenimports = ["tkinter"] + collect_submodules("aaf2")

a = Analysis(
    ["mxto_aaf_gui.py"],
    pathex=[str(project_root)],
    binaries=extra_binaries + dll_binaries,
    datas=common_datas,
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
    [],
    exclude_binaries=True,
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MXToAAF",
)
