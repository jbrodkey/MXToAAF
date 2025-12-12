# PyInstaller hook for aaf2
# Ensures aaf2 package and all its submodules are bundled

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('aaf2')
