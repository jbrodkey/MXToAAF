# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for MXToAAF packaging"""
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Determine platform-specific settings
if sys.platform == 'darwin':
    ffmpeg_binaries = [
        ('binaries/macos/ffmpeg', 'binaries'),
        ('binaries/macos/ffprobe', 'binaries'),
    ]
    icon_file = 'icons/mxtoaaf.icns' if os.path.exists('icons/mxtoaaf.icns') else None
elif sys.platform == 'win32':
    ffmpeg_binaries = [
        ('binaries/windows/ffmpeg.exe', 'binaries'),
        ('binaries/windows/ffprobe.exe', 'binaries'),
    ]
    icon_file = 'icons/mxtoaaf.ico' if os.path.exists('icons/mxtoaaf.ico') else None
else:  # Linux
    ffmpeg_binaries = [
        ('binaries/linux/ffmpeg', 'binaries'),
        ('binaries/linux/ffprobe', 'binaries'),
    ]
    icon_file = None

# Collect AAF2 data files
aaf2_datas = collect_data_files('aaf2')

# Collect all submodules
hiddenimports = collect_submodules('aaf2') + collect_submodules('mutagen')

a = Analysis(
    ['mxto_aaf/cli.py'],
    pathex=[],
    binaries=ffmpeg_binaries,
    datas=[
        ('mxto_aaf/__version__.py', 'mxto_aaf'),
        ('README.md', '.'),
        ('LICENSES.txt', '.'),
    ] + aaf2_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='mxtoaaf',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='MXToAAF.app',
        icon=icon_file,
        bundle_identifier='com.jasonbrodkey.mxtoaaf',
        info_plist={
            'CFBundleShortVersionString': '0.9.0',
            'CFBundleVersion': '0.9.0',
            'NSHighResolutionCapable': True,
        },
    )
