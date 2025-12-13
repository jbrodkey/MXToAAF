#!/bin/bash
# Build minimal audio-only FFmpeg for Windows (cross-compiled from macOS/Linux)
# This creates much smaller binaries than the full FFmpeg distribution

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building minimal FFmpeg for Windows...${NC}"

# Configuration
FFMPEG_VERSION="7.1"
BUILD_DIR="ffmpeg_build_windows"
OUTPUT_DIR="binaries/windows"

# Check prerequisites
if ! command -v wget &> /dev/null && ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: wget or curl required. Install with: brew install wget${NC}"
    exit 1
fi

if ! command -v x86_64-w64-mingw32-gcc &> /dev/null; then
    echo -e "${RED}Error: MinGW-w64 cross-compiler not found.${NC}"
    echo -e "${YELLOW}Install with: brew install mingw-w64${NC}"
    exit 1
fi

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Download FFmpeg source if not already present
if [ ! -d "ffmpeg-$FFMPEG_VERSION" ]; then
    echo -e "${YELLOW}Downloading FFmpeg ${FFMPEG_VERSION}...${NC}"
    if command -v wget &> /dev/null; then
        wget "https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.xz"
    else
        curl -L -O "https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.xz"
    fi
    tar xf "ffmpeg-${FFMPEG_VERSION}.tar.xz"
fi

cd "ffmpeg-$FFMPEG_VERSION"

# Configure minimal audio-only build for Windows
echo -e "${YELLOW}Configuring FFmpeg (minimal audio-only for Windows)...${NC}"
./configure \
    --arch=x86_64 \
    --target-os=mingw32 \
    --cross-prefix=x86_64-w64-mingw32- \
    --enable-cross-compile \
    --prefix="$(pwd)/../install" \
    --disable-everything \
    --disable-doc \
    --disable-htmlpages \
    --disable-manpages \
    --disable-podpages \
    --disable-txtpages \
    --disable-network \
    --disable-autodetect \
    --disable-hwaccels \
    --disable-videotoolbox \
    --enable-small \
    --enable-static \
    --disable-shared \
    --enable-ffmpeg \
    --enable-ffprobe \
    --enable-protocol=file \
    --enable-decoder=aac,mp3,mp3float,pcm_s16le,pcm_s24le,pcm_s32le,flac,alac \
    --enable-encoder=pcm_s16le,pcm_s24le \
    --enable-demuxer=aac,mp3,mov,m4a,wav,flac \
    --enable-muxer=wav \
    --enable-parser=aac,mpegaudio \
    --enable-filter=aresample \
    --enable-swresample

# Build
echo -e "${YELLOW}Building FFmpeg (this may take 5-15 minutes)...${NC}"
make -j$(sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Install to local prefix
make install

# Copy binaries to project
echo -e "${YELLOW}Copying binaries to ${OUTPUT_DIR}...${NC}"
cd ../..
mkdir -p "$OUTPUT_DIR"

# Copy the executables (they should be statically linked)
if [ -f "$BUILD_DIR/install/bin/ffmpeg.exe" ]; then
    cp "$BUILD_DIR/install/bin/ffmpeg.exe" "$OUTPUT_DIR/"
    echo -e "${GREEN}✓ Copied ffmpeg.exe${NC}"
else
    echo -e "${RED}✗ ffmpeg.exe not found${NC}"
    exit 1
fi

if [ -f "$BUILD_DIR/install/bin/ffprobe.exe" ]; then
    cp "$BUILD_DIR/install/bin/ffprobe.exe" "$OUTPUT_DIR/"
    echo -e "${GREEN}✓ Copied ffprobe.exe${NC}"
else
    echo -e "${RED}✗ ffprobe.exe not found${NC}"
    exit 1
fi

# Check sizes
FFMPEG_SIZE=$(du -h "$OUTPUT_DIR/ffmpeg.exe" | cut -f1)
FFPROBE_SIZE=$(du -h "$OUTPUT_DIR/ffprobe.exe" | cut -f1)

echo -e "${GREEN}Build complete!${NC}"
echo -e "  ffmpeg.exe: ${FFMPEG_SIZE}"
echo -e "  ffprobe.exe: ${FFPROBE_SIZE}"
echo -e "${YELLOW}Note: These are statically linked executables (no DLLs required)${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Test the binaries: ./${OUTPUT_DIR}/ffmpeg.exe -version"
echo -e "  2. Update PyInstaller spec to bundle only ffmpeg.exe and ffprobe.exe (no DLLs)"
echo -e "  3. Commit the new binaries to git"
