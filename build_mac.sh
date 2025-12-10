#!/bin/bash
# Build script for MXToAAF macOS app bundle
# Usage: ./build_mac.sh

set -euo pipefail

echo "Building MXToAAF for macOS..."

# Check if PyInstaller is installed
if ! python3 -m pip show pyinstaller > /dev/null 2>&1; then
    echo "Installing PyInstaller..."
    python3 -m pip install --user pyinstaller
fi

# Check for icon file
ICON_FLAG=""
if [ -f "icons/mac/MXToAAF.icns" ]; then
    echo "Found macOS icon, including in build..."
    ICON_FLAG="--icon icons/mac/MXToAAF.icns"
else
    echo "No icon found at icons/mac/MXToAAF.icns, building without custom icon..."
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Build with PyInstaller
echo "Building application..."
python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --add-data "LICENSES.txt:." \
    --add-data "docs/README_mac.md:docs" \
    --windowed \
    --hidden-import=tkinter \
    --name "MXToAAF" \
    $ICON_FLAG \
    mxto_aaf_gui.py

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

# Copy license and documentation into the app bundle
echo "Adding license and documentation..."
cp LICENSES.txt dist/MXToAAF.app/Contents/MacOS/
cp docs/README_mac.md dist/MXToAAF.app/Contents/MacOS/README.md

# Update Info.plist version to match package __version__
VERSION=$(python3 - <<'PY'
from mxto_aaf.__version__ import __version__
print(__version__)
PY
)
INFO_PLIST="dist/MXToAAF.app/Contents/Info.plist"
if [ -f "$INFO_PLIST" ]; then
    /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$INFO_PLIST" || true
    /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $VERSION" "$INFO_PLIST" || true
fi

echo ""
echo "✓ Build complete!"
echo ""
echo "App bundle location: dist/MXToAAF.app"
echo ""
echo "To run the app:"
echo "  open dist/MXToAAF.app"
echo ""
echo "To create a DMG for distribution:"
echo "  hdiutil create -volname 'MXToAAF' -srcfolder dist/MXToAAF.app -ov -format UDZO MXToAAF.dmg"
