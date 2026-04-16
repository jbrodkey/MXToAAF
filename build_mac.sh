#!/bin/bash
# Build script for MXToAAF macOS app bundle
# Usage: ./build_mac.sh

set -euo pipefail

echo "Building MXToAAF for macOS..."

# Check for FFmpeg/FFprobe binaries
if [ ! -f "binaries/macos/ffmpeg" ]; then
    echo "FFmpeg binary not found at binaries/macos/ffmpeg"
    echo "Please run: ./build_minimal_ffmpeg_mac.sh"
    exit 1
fi
if [ ! -f "binaries/macos/ffprobe" ]; then
    echo "FFprobe binary not found at binaries/macos/ffprobe"
    echo "Please run: ./build_minimal_ffmpeg_mac.sh"
    exit 1
fi

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

# Build with PyInstaller spec to keep options in one place
echo "Building application with bundled FFmpeg/FFprobe via mxtoaaf.spec..."
python3 -m PyInstaller \
    --noconfirm \
    --clean \
    mxtoaaf.spec

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

# Copy license and documentation into the app bundle
echo "Adding license and documentation..."
if [ -d "dist/MXToAAF.app" ]; then
    APP_PATH="dist/MXToAAF.app"
else
    # Fallback if for some reason only COLLECT was created
    APP_PATH="dist/MXToAAF"
fi

cp LICENSES.txt "$APP_PATH/Contents/MacOS/"
cp docs/README_mac.md "$APP_PATH/Contents/MacOS/README.md"

# Update Info.plist version to match package __version__ BEFORE signing
VERSION=$(python3 - <<'PY'
from mxto_aaf.__version__ import __version__
print(__version__)
PY
)
INFO_PLIST="$APP_PATH/Contents/Info.plist"
if [ -f "$INFO_PLIST" ]; then
    /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$INFO_PLIST" || true
    /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $VERSION" "$INFO_PLIST" || true
fi

# Remove quarantine attributes that might cause "damaged app" errors
echo "Removing quarantine attributes..."
xattr -cr "$APP_PATH" 2>/dev/null || true

# Remove any signatures that PyInstaller may have added
echo "Removing any existing signatures..."
codesign --remove-signature "$APP_PATH" 2>/dev/null || true
# Create basic entitlements file for unsigned app
ENTITLEMENTS_FILE="$APP_PATH/Contents/entitlements.plist"
cat > "$ENTITLEMENTS_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
</dict>
</plist>
EOF

# Ad-hoc sign with entitlements to allow basic functionality
echo "Ad-hoc signing with basic entitlements..."
codesign --force --deep --sign - --entitlements "$ENTITLEMENTS_FILE" "$APP_PATH" 2>/dev/null || echo "Warning: codesign failed (continuing anyway)"
echo ""
echo "✓ Build complete!"
echo ""
echo "App bundle location: $APP_PATH"
echo "Includes bundled FFmpeg/FFprobe for self-contained operation"
echo ""
echo "To run the app:"
echo "  open $APP_PATH"
echo ""
echo "To create a DMG for distribution:"
echo "  hdiutil create -volname 'MXToAAF' -srcfolder $APP_PATH -ov -format UDZO MXToAAF.dmg"
