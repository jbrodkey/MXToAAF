# Building MXToAAF

This document explains how to build standalone applications for MXToAAF on macOS and Windows.

## Quick Start

### macOS (Local Build)

```bash
cd /path/to/MXToAAF
./build_mac.sh
```

The built app will be at `dist/MXToAAF.app`. To create a DMG for distribution:

```bash
hdiutil create -volname 'MXToAAF' -srcfolder dist/MXToAAF.app -ov -format UDZO MXToAAF.dmg
```

### Windows (GitHub Actions)

Windows builds are handled automatically by GitHub Actions on tag pushes. See [Automated Builds](#automated-builds) below.

---

## Local Build Instructions

### Prerequisites

- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- All dependencies: `pip install -r requirements.txt`

### macOS Build

1. **From project root**, run:
   ```bash
   ./build_mac.sh
   ```

2. The app bundle will be created at `dist/MXToAAF.app`

3. **Optional**: Create a DMG for distribution:
   ```bash
   hdiutil create -volname 'MXToAAF' -srcfolder dist/MXToAAF.app -ov -format UDZO MXToAAF.dmg
   ```

### Windows Build (Local)

1. **From project root**, run:
   ```cmd
   python -m PyInstaller ^
     --noconfirm ^
     --clean ^
     --windowed ^
     --hidden-import=tkinter ^
     --name "MXToAAF" ^
     mxto_aaf_gui.py
   ```

2. The executable will be at `dist\MXToAAF\MXToAAF.exe`

---

## Automated Builds (GitHub Actions)

Builds are automatically triggered when you push a git tag:

### Create a Release Build

```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers:
- **macOS workflow** (`build-macos.yml`): Creates `MXToAAF.app` and `MXToAAF.dmg`
- **Windows workflow** (`build-windows.yml`): Creates `MXToAAF.exe` and dependencies

### Download Built Artifacts

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select the completed workflow run
4. Download the artifacts:
   - `MXToAAF-macOS` (`.app` and `.dmg`)
   - `MXToAAF-Windows` (`.exe` folder)

---

## Build Output

### macOS

- **App Bundle**: `dist/MXToAAF.app` (can be run by double-clicking)
- **DMG**: `MXToAAF.dmg` (can be distributed to users)

Users can:
- Mount the DMG and drag the app to Applications
- Or run the `.app` directly from any location

### Windows

- **Executable Folder**: `dist\MXToAAF\` (contains `MXToAAF.exe` and all dependencies)
- **Single EXE** (optional): Use `--onefile` flag for single executable (slower startup)

Users can:
- Copy the entire folder to any location and run `MXToAAF.exe`
- Or distribute the single `.exe` if built with `--onefile`

---

## Troubleshooting

### macOS

- **"MXToAAF cannot be opened"**: Right-click the app and select "Open" to bypass Gatekeeper on first run
- **Icon not appearing**: Ensure `icons/mac/MXToAAF.icns` exists (optional)
- **Tkinter missing**: Use official Python from python.org, not Homebrew

### Windows

- **"Tkinter not found"**: Ensure Python was installed with the tcl/tk option
- **DLL errors**: Install Microsoft Visual C++ Redistributable
- **SmartScreen warnings**: Code-sign the executable (optional), or users can click "Run anyway"

---

## PyInstaller Options

The builds use:
- `--windowed`: No console window on startup
- `--hidden-import=tkinter`: Explicitly include tkinter
- `--noconfirm`: Don't ask before overwriting
- `--clean`: Remove previous build artifacts

For a single-file executable on Windows, add `--onefile` (slower startup but easier distribution).

---

## Version Management

The app displays the version from `mxto_aaf/__version__.py`. Update this file before tagging a release:

```python
__version__ = "1.0.0"
```

Then commit and tag:

```bash
git add mxto_aaf/__version__.py
git commit -m "Bump version to 1.0.0"
git tag v1.0.0
git push origin main v1.0.0
```

---

## Next Steps

1. **Icon Creation** (optional):
   - Create `icons/mac/MXToAAF.icns` for macOS
   - Create `icons/win/MXToAAF.ico` for Windows

2. **Code Signing** (optional, recommended for distribution):
   - macOS: Use `codesign` to sign the app bundle
   - Windows: Sign with certificate for SmartScreen

3. **Release Notes**:
   - Create `RELEASE_NOTES.md` documenting each version
