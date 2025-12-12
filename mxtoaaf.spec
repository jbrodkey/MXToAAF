# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mxto_aaf_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('LICENSES.txt', '.'), ('docs/README_mac.md', 'docs'), ('binaries/macos/ffmpeg', 'binaries')],
    hiddenimports=['tkinter'],
    hookspath=[],
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
)
