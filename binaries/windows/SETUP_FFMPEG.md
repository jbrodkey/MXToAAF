# Windows FFmpeg Setup

This directory should contain `ffmpeg.exe` and `ffprobe.exe` for Windows builds.

**IMPORTANT:** You must use a **static build** that includes all dependencies in the executable, or include all required DLL files.

## Option 1: Download Static Build on macOS (Recommended)

The easiest approach is to download a static build that doesn't require separate DLLs:

1. **Download static build** - Visit in your browser:
   - **BtbN Builds:** https://github.com/BtbN/FFmpeg-Builds/releases
   - Look for: `ffmpeg-master-latest-win64-gpl-shared.zip` or `ffmpeg-master-latest-win64-lgpl-shared.zip`
   - Download the `.zip` file (NOT .7z for easier extraction on Mac)

2. **Extract** on your Mac:
   ```bash
   cd ~/Downloads
   unzip ffmpeg-master-latest-win64-gpl-shared.zip
   cd ffmpeg-master-latest-win64-gpl-shared/bin
   ls -la  # You should see ffmpeg.exe, ffprobe.exe, and multiple .dll files
   ```

3. **Copy ALL files to project** (executables AND DLLs):
   ```bash
   cp ~/Downloads/ffmpeg-master-latest-win64-gpl-shared/bin/*.exe /path/to/MXToAAF/binaries/windows/
   cp ~/Downloads/ffmpeg-master-latest-win64-gpl-shared/bin/*.dll /path/to/MXToAAF/binaries/windows/
   ```

4. **Verify** (should see ffmpeg.exe, ffprobe.exe, and DLL files):
   ```bash
   ls -lh /path/to/MXToAAF/binaries/windows/
   ```

5. **Commit**:
   ```bash
   cd /path/to/MXToAAF
   git add binaries/windows/*.exe binaries/windows/*.dll
   git commit -m "add: Windows FFmpeg binaries with DLL dependencies"
   git push origin main
   ```

## Option 2: Download on macOS, Extract & Commit (Alternative)

On a Windows machine with PowerShell, run this from the project root:

```powershell
# Download FFmpeg
$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-full-release.7z"
$output = "ffmpeg-full-release.7z"

Write-Host "Downloading FFmpeg..."
(New-Object System.Net.WebClient).DownloadFile($url, $output)

# Extract (requires 7-Zip or similar)
Write-Host "Extracting FFmpeg..."
7z x $output -o"."

# Copy binaries
$ffmpegPath = (Get-ChildItem -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1).DirectoryName
Copy-Item "$ffmpegPath\ffmpeg.exe" -Destination "binaries\windows\"
Copy-Item "$ffmpegPath\ffprobe.exe" -Destination "binaries\windows\"

# Cleanup
Remove-Item "ffmpeg-full-release.7z"
Remove-Item "ffmpeg-*" -Recurse

Write-Host "✓ FFmpeg binaries are ready in binaries\windows\"
```

## Option 3: Manual Download on Windows

1. Visit: https://www.gyan.dev/ffmpeg/builds/
2. Download the **full** release (includes both ffmpeg and ffprobe)
3. Extract the archive
4. Copy `bin/ffmpeg.exe` to `binaries/windows/ffmpeg.exe`
5. Copy `bin/ffprobe.exe` to `binaries/windows/ffprobe.exe`

## Option 4: GitHub Releases (Alternative Source)

Alternative source: https://github.com/BtbN/FFmpeg-Builds/releases
- Download `ffmpeg-master-latest-win64-gpl.7z`
- Extract and copy binaries as above

## Verify

After setup, you should have:
- `binaries/windows/ffmpeg.exe` (~60 MB)
- `binaries/windows/ffprobe.exe` (~50 MB)

Then run the build:
```bash
build_windows.bat
```

And commit the binaries:
```bash
git add binaries/windows/ffmpeg.exe binaries/windows/ffprobe.exe
git commit -m "add: Windows FFmpeg binaries"
git push origin main
```
