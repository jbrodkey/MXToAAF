#!/bin/bash
# Build minimal audio-only FFmpeg for macOS (Universal Binary)
# This creates a significantly smaller FFmpeg binary with only audio capabilities

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FFMPEG_VERSION="8.0.1"
FFMPEG_URL="https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.xz"
BUILD_DIR="${SCRIPT_DIR}/ffmpeg_build"
OUTPUT_DIR="${SCRIPT_DIR}/binaries/macos"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building minimal audio-only FFmpeg for macOS (Universal Binary)${NC}"
echo "This will take 10-30 minutes depending on your machine..."

# Check for required tools
if ! command -v make &> /dev/null; then
    echo -e "${RED}Error: make not found. Install Xcode Command Line Tools.${NC}"
    exit 1
fi

# Create build directory
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Download FFmpeg source
echo -e "${YELLOW}Downloading FFmpeg ${FFMPEG_VERSION}...${NC}"
curl -L "${FFMPEG_URL}" -o ffmpeg.tar.xz
tar xf ffmpeg.tar.xz
cd ffmpeg-${FFMPEG_VERSION}

# Configure options for minimal audio-only build
COMMON_CONFIG=(
    --disable-everything
    --disable-programs
    --enable-ffmpeg
    --disable-doc
    --disable-htmlpages
    --disable-manpages
    --disable-podpages
    --disable-txtpages
    
    # Protocols
    --enable-protocol=file
    --enable-protocol=pipe
    
    # Demuxers (input formats)
    --enable-demuxer=aac
    --enable-demuxer=ac3
    --enable-demuxer=aiff
    --enable-demuxer=flac
    --enable-demuxer=m4v
    --enable-demuxer=matroska
    --enable-demuxer=mov
    --enable-demuxer=mp3
    --enable-demuxer=ogg
    --enable-demuxer=wav
    
    # Decoders (input codecs)
    --enable-decoder=aac
    --enable-decoder=aac_latm
    --enable-decoder=ac3
    --enable-decoder=alac
    --enable-decoder=flac
    --enable-decoder=mp3
    --enable-decoder=mp3float
    --enable-decoder=opus
    --enable-decoder=pcm_alaw
    --enable-decoder=pcm_f32be
    --enable-decoder=pcm_f32le
    --enable-decoder=pcm_f64be
    --enable-decoder=pcm_f64le
    --enable-decoder=pcm_mulaw
    --enable-decoder=pcm_s16be
    --enable-decoder=pcm_s16le
    --enable-decoder=pcm_s24be
    --enable-decoder=pcm_s24le
    --enable-decoder=pcm_s32be
    --enable-decoder=pcm_s32le
    --enable-decoder=pcm_s8
    --enable-decoder=pcm_u16be
    --enable-decoder=pcm_u16le
    --enable-decoder=pcm_u24be
    --enable-decoder=pcm_u24le
    --enable-decoder=pcm_u32be
    --enable-decoder=pcm_u32le
    --enable-decoder=pcm_u8
    --enable-decoder=vorbis
    
    # Encoders (output codecs)
    --enable-encoder=pcm_f32be
    --enable-encoder=pcm_f32le
    --enable-encoder=pcm_f64be
    --enable-encoder=pcm_f64le
    --enable-encoder=pcm_s16be
    --enable-encoder=pcm_s16le
    --enable-encoder=pcm_s24be
    --enable-encoder=pcm_s24le
    --enable-encoder=pcm_s32be
    --enable-encoder=pcm_s32le
    
    # Muxers (output formats)
    --enable-muxer=wav
    
    # Parsers
    --enable-parser=aac
    --enable-parser=aac_latm
    --enable-parser=ac3
    --enable-parser=flac
    --enable-parser=mpegaudio
    --enable-parser=opus
    --enable-parser=vorbis
    
    # Filters (keep minimal set for audio processing)
    --enable-filter=aformat
    --enable-filter=aresample
    --enable-filter=asetnsamples
    --enable-filter=asetrate
    
    # Build settings
    --enable-static
    --disable-shared
    --enable-small
    --disable-debug
    --disable-runtime-cpudetect
)

# Build for ARM64 (Apple Silicon)
echo -e "${YELLOW}Building for ARM64 (Apple Silicon)...${NC}"
./configure \
    "${COMMON_CONFIG[@]}" \
    --arch=arm64 \
    --enable-cross-compile \
    --target-os=darwin \
    --prefix="${BUILD_DIR}/install-arm64"

make clean
make -j$(sysctl -n hw.ncpu)
make install
cp "${BUILD_DIR}/install-arm64/bin/ffmpeg" "${BUILD_DIR}/ffmpeg-arm64"

# Build for x86_64 (Intel)
echo -e "${YELLOW}Building for x86_64 (Intel)...${NC}"
./configure \
    "${COMMON_CONFIG[@]}" \
    --arch=x86_64 \
    --enable-cross-compile \
    --target-os=darwin \
    --cc="clang -arch x86_64" \
    --disable-x86asm \
    --disable-inline-asm \
    --prefix="${BUILD_DIR}/install-x86_64"

make clean
make -j$(sysctl -n hw.ncpu)
make install
cp "${BUILD_DIR}/install-x86_64/bin/ffmpeg" "${BUILD_DIR}/ffmpeg-x86_64"

# Create universal binary
echo -e "${YELLOW}Creating universal binary...${NC}"
mkdir -p "${OUTPUT_DIR}"
lipo -create \
    "${BUILD_DIR}/ffmpeg-arm64" \
    "${BUILD_DIR}/ffmpeg-x86_64" \
    -output "${OUTPUT_DIR}/ffmpeg"

chmod +x "${OUTPUT_DIR}/ffmpeg"

# Display results
echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "Binary location: ${OUTPUT_DIR}/ffmpeg"
echo ""

# Show size comparison
if [ -f "${OUTPUT_DIR}/ffmpeg" ]; then
    SIZE=$(du -h "${OUTPUT_DIR}/ffmpeg" | cut -f1)
    echo -e "${GREEN}Universal binary size: ${SIZE}${NC}"
    
    # Show architectures
    echo ""
    echo "Supported architectures:"
    lipo -info "${OUTPUT_DIR}/ffmpeg"
    
    # Verify it works
    echo ""
    echo "Testing binary..."
    if "${OUTPUT_DIR}/ffmpeg" -version | head -n 1; then
        echo -e "${GREEN}✓ Binary works!${NC}"
    else
        echo -e "${RED}✗ Binary test failed${NC}"
        exit 1
    fi
fi

# Cleanup
echo ""
read -p "Remove build directory to save space? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleaning up..."
    cd "${SCRIPT_DIR}"
    rm -rf "${BUILD_DIR}"
    echo -e "${GREEN}Build directory removed.${NC}"
fi

echo ""
echo -e "${GREEN}Done! Your minimal FFmpeg is ready at:${NC}"
echo "${OUTPUT_DIR}/ffmpeg"
