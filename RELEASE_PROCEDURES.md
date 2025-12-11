# MXToAAF Release Procedures

This document outlines the procedures for building and releasing MXToAAF for macOS and Windows, ensuring proper version numbers, About dialog display, and Help/License documentation.

## Version Management

### 1. Update Version Number

Before building, update the version in `mxto_aaf/__version__.py`:

```python
__version__ = "1.0.1"  # Update this to your release version
```

The build scripts will automatically:
- Use this version in the macOS app's Info.plist (Finder Get Info)
- Display this version in the About dialog on both platforms
- Include the version in the app footer

### 2. Verify Version Display

After building, verify the version appears in:
- **macOS**: Right-click app → Get Info → Version field
- **About Dialog**: Help → About MXToAAF (both platforms)
- **App Footer**: Bottom-right of the app window (both platforms)

## Building Releases

### macOS Build (Local)

**Prerequisites:**
- FFmpeg binaries must be available in `binaries/macos/` directory:
  - `binaries/macos/ffmpeg` (executable)
  - `binaries/macos/ffprobe` (executable)
- If FFmpeg is installed via Homebrew, the build script will automatically copy it to the correct location
- To manually prepare FFmpeg:
  ```bash
  brew install ffmpeg
  mkdir -p binaries/macos
  cp "$(which ffmpeg)" binaries/macos/
  cp "$(which ffprobe)" binaries/macos/
  chmod +x binaries/macos/ffmpeg binaries/macos/ffprobe
  ```

```bash
./build_mac.sh
```

**What this does:**
1. Checks for FFmpeg binaries in `binaries/macos/` (or uses system Homebrew installation as fallback)
2. Builds the app using PyInstaller
3. Bundles FFmpeg binaries into the self-contained app
4. Bundles `LICENSES.txt` into the app
5. Bundles `docs/README_mac.md` for the Help menu
6. Sets the Info.plist version to match `__version__`
7. Includes macOS icon (`icons/mac/MXToAAF.icns`)

**Result:** `dist/MXToAAF.app` (fully self-contained, no system FFmpeg needed)

**Important:** The bundled FFmpeg is included in the app bundle and doesn't require system-wide installation.

**Verify:**
- Right-click app → Get Info → confirm version
- App appears with icon in Finder
- Open app → Help → MXToAAF Help (shows README_mac.md)
- Open app → Help → License Info (shows LICENSES.txt)
- Open app → Help → About MXToAAF (shows correct version)

### Windows Build (Local)

**Prerequisites:**
- FFmpeg binaries must be available in `binaries\windows\` directory:
  - `binaries\windows\ffmpeg.exe` (executable)
  - `binaries\windows\ffprobe.exe` (executable)
- To download FFmpeg for Windows:
  1. Visit https://www.gyan.dev/ffmpeg/builds/
  2. Download the **full** version (includes both ffmpeg and ffprobe)
  3. Extract the zip file
  4. Copy `bin\ffmpeg.exe` to `binaries\windows\ffmpeg.exe`
  5. Copy `bin\ffprobe.exe` to `binaries\windows\ffprobe.exe`
- Or use automated download (Windows PowerShell):
  ```batch
  # Ensure binaries\windows\ directory exists
  mkdir binaries\windows
  # Download, extract, and copy files using PowerShell
  powershell -Command "
    Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/releases/ffmpeg-full.7z' -OutFile 'ffmpeg-full.7z'
    Expand-Archive 'ffmpeg-full.7z' -DestinationPath '.'
    Copy-Item 'ffmpeg-*\bin\ffmpeg.exe' -Destination 'binaries\windows\ffmpeg.exe'
    Copy-Item 'ffmpeg-*\bin\ffprobe.exe' -Destination 'binaries\windows\ffprobe.exe'
    Remove-Item 'ffmpeg-full.7z'
    Remove-Item 'ffmpeg-*' -Recurse
  "
  ```

```bash
build_windows.bat
```

**What this does:**
1. Validates FFmpeg binaries exist in `binaries\windows\` directory
2. Builds a single executable using PyInstaller with `--onefile` flag
3. Bundles FFmpeg binaries into the self-contained executable
4. Bundles `LICENSES.txt`
5. Bundles `docs/README_windows.md` for the Help menu
6. Bundles Windows icon (`icons/win/MXToAAF.ico`)
7. Sets window icon for the app at runtime
8. Creates `dist_package\MXToAAF\` distribution folder with all files

**Distribution Package Contents:**
- `MXToAAF.exe` - Single executable file (includes FFmpeg binaries)
- `README.md` - Copy of `docs/README_windows.md`
- `LICENSES.txt` - License documentation

**Result:** `dist_package\MXToAAF\` (entire folder ready to distribute, no system FFmpeg needed)

**Important:** The bundled FFmpeg is included in the executable and doesn't require system-wide installation.

**Verify:**
- Run the exe
- Window title bar shows app icon
- Help dropdown → MXToAAF Help (shows README_windows.md)
- Help dropdown → License Info (shows LICENSES.txt)
- Help dropdown → About MXToAAF (shows correct version)

### Windows Build (GitHub Actions)

**Prerequisites:**
- FFmpeg binaries must be committed to the repository in `binaries/windows/`:
  - `binaries/windows/ffmpeg.exe`
  - `binaries/windows/ffprobe.exe`
- This is necessary because GitHub Actions runners cannot execute system FFmpeg commands; the binaries must be in the repository

Pushes to `main` or tags starting with `v*` automatically trigger:

1. Checkout code (including FFmpeg binaries from `binaries/windows/`)
2. Build with PyInstaller (bundles FFmpeg from repository)
3. Create `dist_package\MXToAAF\` distribution folder
4. Upload as artifact named `MXToAAF` (automatically zipped as `MXToAAF.zip`)

**To download:** GitHub repo → Actions → latest Windows build → Artifacts → `MXToAAF`

**Important:** Ensure FFmpeg binaries are committed to `binaries/windows/` before pushing tags, or the GitHub Actions build will fail.

## App Icons

### Windows Icon
- **Location:** `icons/win/MXToAAF.ico`
- **Used for:**
  - Executable icon (set via `--icon` flag in PyInstaller)
  - Window title bar icon (set via `root.iconbitmap()` at runtime)
- **Bundled in build:** Yes, via `--add-data "icons/win/MXToAAF.ico;icons/win"`
- **Verify:** Run app, check window title bar for icon

### macOS Icon
- **Location:** `icons/mac/MXToAAF.icns`
- **Used for:**
  - App bundle icon (set via `--icon` flag in PyInstaller)
  - Finder display
- **Bundled in build:** Integrated into .app bundle automatically
- **Verify:** App icon appears in Finder and Dock

## Documentation in Menus

### macOS App Help Menu

Uses native macOS menubar. Accessible via:
- **Help → MXToAAF Help** → Shows `docs/README_mac.md`
- **Help → License Info** → Shows `LICENSES.txt`
- **MXToAAF menu → About MXToAAF** → Shows About dialog with version

### Windows App Help Menu

Help dropdown button in top-left. Accessible via:
- **Help → MXToAAF Help** → Shows `docs/README_windows.md`
- **Help → License Info** → Shows `LICENSES.txt`
- **Help → About MXToAAF** → Shows About dialog with version

## Key Files Involved

| File | Purpose |
|------|---------|
| `mxto_aaf/__version__.py` | Master version source |
| `mxto_aaf_gui.py` | Reads version, handles Help/License menus |
| `build_mac.sh` | macOS build script, updates Info.plist |
| `build_windows.bat` | Windows local build script |
| `.github/workflows/build-windows.yml` | Automated Windows CI build |
| `LICENSES.txt` | License documentation (bundled in app) |
| `docs/README_mac.md` | macOS-specific help (bundled in app) |
| `docs/README_windows.md` | Windows-specific help (bundled in app) |

## Build Requirements

### macOS
- Python 3.10+
- PyInstaller: `pip install pyinstaller`
- FFmpeg: `brew install ffmpeg` (or provide binaries in `binaries/macos/`)
- macOS command-line tools (for `PlistBuddy`)

### Windows
- Python 3.10+
- PyInstaller: `pip install pyinstaller`
- FFmpeg binaries in `binaries\windows\` directory:
  - Download from https://www.gyan.dev/ffmpeg/builds/
  - Extract `ffmpeg.exe` and `ffprobe.exe` to `binaries\windows\`
- All dependencies in `requirements.txt`

## Troubleshooting

### FFmpeg not found during build
- **macOS:** Ensure either `binaries/macos/ffmpeg` and `binaries/macos/ffprobe` exist, OR FFmpeg is installed via Homebrew
  - Install: `brew install ffmpeg`
  - Copy to build: `cp "$(which ffmpeg)" binaries/macos/ && cp "$(which ffprobe)" binaries/macos/`
- **Windows:** Ensure `binaries\windows\ffmpeg.exe` and `binaries\windows\ffprobe.exe` exist
  - Download from https://www.gyan.dev/ffmpeg/builds/
  - Extract to `binaries\windows\`

### Version shows as "0.0.0" or "unknown"
- Verify `mxto_aaf/__version__.py` exists and has `__version__` defined
- Rebuild the app after updating version
- macOS: Ensure `build_mac.sh` runs the version update step (check for PlistBuddy errors)

### Help/License docs don't appear
- Verify `LICENSES.txt` exists in project root
- Verify `docs/README_mac.md` (macOS) or `docs/README_windows.md` (Windows) exist
- Check that build script includes `--add-data` for bundling
- Rebuild the app

### macOS Info.plist version not updating
- Ensure `/usr/libexec/PlistBuddy` is available (standard on macOS)
- Check build script output for PlistBuddy errors
- Verify `dist/MXToAAF.app/Contents/Info.plist` exists after build

### Built app fails with "ffmpeg not available in PATH"
- **Cause:** FFmpeg binaries weren't properly bundled during build
- **macOS:** Re-run `./build_mac.sh` and verify FFmpeg is in `binaries/macos/`
- **Windows:** Re-run `build_windows.bat` and verify FFmpeg/ffprobe are in `binaries\windows\`

## Release Checklist

Before distributing:
- [ ] Update `__version__` in `mxto_aaf/__version__.py`
- [ ] **FFmpeg - macOS:** Verify `binaries/macos/ffmpeg` and `binaries/macos/ffprobe` exist (or FFmpeg installed via Homebrew)
- [ ] **FFmpeg - Windows:** Verify `binaries\windows\ffmpeg.exe` and `binaries\windows\ffprobe.exe` exist
- [ ] Test macOS build: `./build_mac.sh`
- [ ] Verify macOS version in Get Info
- [ ] Verify macOS icon appears in Finder
- [ ] Test FFmpeg in macOS app: Select audio file and verify conversion works
- [ ] Test all Help/License menus on macOS
- [ ] Test Windows build: `build_windows.bat`
- [ ] Verify Windows exe has icon in title bar
- [ ] Test FFmpeg in Windows app: Select audio file and verify conversion works
- [ ] Test all Help/License menus on Windows
- [ ] Commit version change and FFmpeg binaries (if using repository binaries), push to `main`
- [ ] Tag release: `git tag v1.0.1 && git push origin v1.0.1`
- [ ] Wait for GitHub Actions Windows build to complete
- [ ] Download Windows artifact from GitHub Actions
- [ ] Verify Windows version in About dialog
- [ ] Verify FFmpeg works in downloaded Windows artifact (test audio conversion)
- [ ] Package macOS: Zip `dist/MXToAAF.app` (or create DMG)
- [ ] Verify Windows artifact: `MXToAAF.zip` contains `MXToAAF/` folder with exe, README, and LICENSES
- [ ] Create GitHub Release with all artifacts
- [ ] Update distribution channels/websites with links to new versions
