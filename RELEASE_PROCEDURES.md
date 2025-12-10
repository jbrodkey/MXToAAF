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

```bash
./build_mac.sh
```

**What this does:**
1. Builds the app using PyInstaller
2. Bundles `LICENSES.txt` into the app
3. Bundles `docs/README_mac.md` for the Help menu
4. Sets the Info.plist version to match `__version__`

**Result:** `dist/MXToAAF.app`

**Verify:**
- Right-click app → Get Info → confirm version
- Open app → Help → MXToAAF Help (shows README_mac.md)
- Open app → Help → License Info (shows LICENSES.txt)
- Open app → Help → About MXToAAF (shows correct version)

### Windows Build (Local)

```bash
build_windows.bat
```

**What this does:**
1. Builds a single executable using PyInstaller with `--onefile`
2. Bundles `LICENSES.txt`
3. Bundles `docs/README_windows.md` for the Help menu
4. Sets window icon for the app
5. Creates `dist_package\MXToAAF\` folder with all files

**Result:** `dist_package\MXToAAF\MXToAAF.exe` (plus README.md and LICENSES.txt)

**Verify:**
- Run the exe
- Help dropdown → MXToAAF Help (shows README_windows.md)
- Help dropdown → License Info (shows LICENSES.txt)
- Help dropdown → About MXToAAF (shows correct version)
- Window title bar shows app icon

### Windows Build (GitHub Actions)

Pushes to `main` or tags starting with `v*` automatically trigger:

1. Checkout code
2. Build with PyInstaller (same bundling as local)
3. Create `dist_package\MXToAAF\` distribution folder
4. Upload as artifact named `MXToAAF` (automatically zipped as `MXToAAF.zip`)

**To download:** GitHub repo → Actions → latest Windows build → Artifacts → `MXToAAF`

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
- macOS command-line tools (for `PlistBuddy`)

### Windows
- Python 3.10+
- PyInstaller: `pip install pyinstaller`
- All dependencies in `requirements.txt`

## Troubleshooting

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

## Release Checklist

Before distributing:
- [ ] Update `__version__` in `mxto_aaf/__version__.py`
- [ ] Test macOS build: `./build_mac.sh`
- [ ] Verify macOS version in Get Info
- [ ] Test all Help/License menus on macOS
- [ ] Test Windows build: `build_windows.bat`
- [ ] Test all Help/License menus on Windows
- [ ] Commit version change and push to `main`
- [ ] Tag release: `git tag v1.0.1 && git push origin v1.0.1`
- [ ] Download Windows artifact from GitHub Actions (or build locally)
- [ ] Verify Windows version in About dialog
- [ ] Package macOS: `dist/MXToAAF.app` (or create DMG)
- [ ] Package Windows: `dist_package/MXToAAF/` folder
- [ ] Create GitHub Release with both artifacts
