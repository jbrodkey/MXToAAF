# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_all

# Collect all aaf2 and mutagen package data/binaries via hook utility
_aaf2_datas, _aaf2_binaries, _aaf2_hidden = collect_all("aaf2")
_mutagen_datas, _mutagen_binaries, _mutagen_hidden = collect_all("mutagen")
_tkinterdnd2_datas, _tkinterdnd2_binaries, _tkinterdnd2_hidden = collect_all("tkinterdnd2")

hiddenimports = [
    "tkinter",
    "mutagen",
    "collections.abc",
    "mxto_aaf.aaf",
    "aaf2",
    "aaf2.auid",
    "aaf2.rational",
    "aaf2.misc",
    "tkinterdnd2",
]
hiddenimports += collect_submodules("aaf2")
hiddenimports += collect_submodules("mutagen")
hiddenimports += collect_submodules("tkinterdnd2")
hiddenimports += _aaf2_hidden
hiddenimports += _mutagen_hidden
hiddenimports += _tkinterdnd2_hidden

a = Analysis(
    ['mxto_aaf_gui.py'],
    pathex=[],
    binaries=_aaf2_binaries + _mutagen_binaries + _tkinterdnd2_binaries,
    datas=[('LICENSES.txt', '.'), ('docs/README_mac.md', 'docs'), ('binaries/macos/ffmpeg', 'binaries'), ('binaries/macos/ffprobe', 'binaries')] + _aaf2_datas + _mutagen_datas + _tkinterdnd2_datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MXToAAF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons/mac/MXToAAF.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MXToAAF',
)
app = BUNDLE(
    coll,
    name='MXToAAF.app',
    icon='icons/mac/MXToAAF.icns',
    bundle_identifier=None,
    codesign_identity=None,
)
