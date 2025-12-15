# MXToAAF AI Coding Agent Instructions

## Project Overview

**MXToAAF** converts music files (mp3, m4a, wav, aif) to Avid-compatible AAF files with embedded essence and metadata extraction from ID3/MP4 tags. The tool supports both single-file and batch directory processing, targeting professional audio post-production workflows.

## Architecture

### Module Structure
- **`mxto_aaf/metadata.py`**: Metadata extraction with mutagen (primary) → ffprobe (fallback)
- **`mxto_aaf/aaf.py`**: AAF file creation using pyaaf2 library, including stereo pan implementation
- **`mxto_aaf/batch.py`**: Batch directory processing with CSV reporting and resume capability
- **`mxto_aaf/utils.py`**: FFmpeg detection, WAV conversion utilities
- **`mxto_aaf/__main__.py`**: Unified CLI with auto-detection (file vs directory mode)

### Key Data Flow
1. **Extract** metadata from audio files (mutagen preferred, ffprobe fallback)
2. **Convert** non-WAV formats to PCM WAV using bundled FFmpeg binaries (`binaries/macos/`, `binaries/windows/`)
3. **Create** AAF with `aaf2` library, embedding PCM audio and metadata tags
4. **Name** output AAFs as `{Source}_{TrackName}.aaf` (e.g., "Flicka_Main Title.aaf")

### Critical External Dependencies
- **pyaaf2**: AAF file I/O (required for `--embed` mode)
- **mutagen**: Metadata extraction (primary method, handles ID3/MP4/AIFF tags)
- **FFmpeg**: Audio conversion via bundled binaries in `binaries/` (not system PATH)

## Development Conventions

### Metadata Field Mapping
The codebase uses a **dual naming convention**:
- **Internal Python names** (snake_case): `track_name`, `album_artist`, `total_tracks`
- **AAF tag names** (PascalCase): `TrackName`, `Artist`, `CatalogNumber`

Mapping defined in `aaf.py` via `DEFAULT_TAG_MAP` dictionary. Always use internal names in `MusicMetadata` dataclass.

### AAF Name Format
Output AAF names follow strict pattern: `{Source}_{TrackName}.aaf`
- Falls back to `{Album}_{TrackName}.aaf` if Source is missing
- Further falls back to `UnknownSource_{TrackName}.aaf`
- Implementation in `aaf.py::create_music_aaf()` - see `aaf_name` construction logic

### Stereo Pan Implementation
**Critical:** All stereo tracks require explicit L/R pan positioning using AAF OperationGroups:
- Left channel: pan = -1.0, Right channel: pan = +1.0
- Uses standard AAF AUIDs: `AAF_PARAMETERDEF_PAN`, `AAF_OPERATIONDEF_MONOAUDIOPAN`
- Implementation details in `docs/AAF_PAN_IMPLEMENTATION.md` and `aaf.py::_apply_pan_to_slot()`
- Without this, stereo imports as dual center-panned mono in Avid

### Path Sanitization
`__main__.py` includes drag-and-drop path sanitization:
- Removes surrounding quotes from copied paths
- Handles shell-escaped spaces (`\ ` → space) on POSIX systems only
- Expands user `~` paths
- See `_sanitize_path()` function

## Testing

Run tests with pytest from project root:
```bash
python3 -m pytest tests/
```

Test structure:
- `tests/test_sample_media_processing.py`: Integration tests using `Sample Media/wavTest_MX/`
- `tests/test_mutagen_extraction.py`: Metadata extraction validation
- `tests/test_ffprobe_fallback.py`: Fallback behavior when mutagen unavailable
- `tests/test_embed.py`: AAF embedding with pyaaf2
- Tests use **absolute paths** to sample media directory (update if moved)

## Building & Packaging

### Standalone Apps (PyInstaller)
```bash
# macOS
./build_mac.sh
# Output: dist/MXToAAF.app

# Windows (via GitHub Actions or locally)
pyinstaller mxtoaaf_windows.spec
# Output: dist/MXToAAF.exe
```

### DMG Creation (macOS)
```bash
cd packaging/DMG_
./create_dmg.sh
# Output: packaging/DMG_/MXToAAF_v{version}.dmg
```

**Important:** FFmpeg binaries must be present in `binaries/{macos,windows}/` before building. PyInstaller specs (`mxtoaaf.spec`, `mxtoaaf_windows.spec`) bundle these as data files.

## CLI Usage Patterns

### Auto-Detection Mode
CLI automatically detects file vs directory input:
```bash
python3 -m mxto_aaf "song.mp3" -o output.aaf --embed           # Single file
python3 -m mxto_aaf "Sample Media/wavTest_MX" -o ./out --embed # Batch
```

### Batch Options
- `--skip-existing`: Resume interrupted batch runs
- `--export-csv`: Per-file success/error report
- `--export-metadata-csv`: Extracted metadata fields per file
- `--max-files N`: Limit for testing (use in tests)

### Interactive Mode
If input/output not provided, CLI prompts interactively (when `sys.stdin.isatty()`).

## Common Pitfalls

1. **FFmpeg Detection**: Always check `utils.ffmpeg_available()` before calling `convert_to_wav()`. Bundled binaries location differs from system PATH.

2. **Genre Normalization**: ID3v1 numeric codes like `"(17)"` are auto-converted to text `"Rock"`. Handled in `metadata.py::_normalize_genre()`.

3. **Track Number Parsing**: Track format `"6/10"` splits into `track="6"` and `total_tracks=10`. See `metadata.py::_parse_track()`.

4. **Version Management**: Version is in `mxto_aaf/__version__.py`. Update here for releases, not in multiple files.

5. **Batch CSV Encoding**: Use `utf-8` encoding for CSV exports to handle international characters in metadata.

## Key Files Reference

- **Metadata extraction**: [`mxto_aaf/metadata.py`](mxto_aaf/metadata.py)
- **AAF creation**: [`mxto_aaf/aaf.py`](mxto_aaf/aaf.py)
- **CLI entry point**: [`mxto_aaf/__main__.py`](mxto_aaf/__main__.py)
- **Batch processing**: [`mxto_aaf/batch.py`](mxto_aaf/batch.py)
- **Build docs**: [`BUILD.md`](BUILD.md), [`PACKAGING.md`](PACKAGING.md)
- **Pan implementation**: [`docs/AAF_PAN_IMPLEMENTATION.md`](docs/AAF_PAN_IMPLEMENTATION.md)
