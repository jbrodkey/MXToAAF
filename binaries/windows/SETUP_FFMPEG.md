# Windows FFmpeg Setup

This directory should contain `ffmpeg.exe` and `ffprobe.exe` for Windows builds.

## Option 1: Download on macOS, Extract & Commit (Fastest)

You can download the Windows FFmpeg binaries on macOS and extract them locally:

1. **Download** - Visit one of these URLs in your browser and download the file:
   - **Recommended:** https://builds.ffmpeg.org/builds/win64/gpl/ffmpeg-latest-win64-gpl-shared.zip
   - **Alternative:** https://www.gyan.dev/ffmpeg/builds/ (click "full" under Latest Version)
   - **Alternative:** https://github.com/BtbN/FFmpeg-Builds/releases (look for `ffmpeg-master-latest-win64-gpl.7z`)

2. **Extract** - After downloading (e.g., `ffmpeg-latest-win64-gpl-shared.zip`):
   ```bash
   cd ~/Downloads
   unzip ffmpeg-latest-win64-gpl-shared.zip  # or 7z x file.7z if it's .7z
   cd ffmpeg-latest-win64-gpl-shared/bin
   ls -la  # You should see ffmpeg.exe and ffprobe.exe
   ```

3. **Copy to project**:
   ```bash
   cp ~/Downloads/ffmpeg-latest-win64-gpl-shared/bin/ffmpeg.exe /path/to/MXToAAF/binaries/windows/
   cp ~/Downloads/ffmpeg-latest-win64-gpl-shared/bin/ffprobe.exe /path/to/MXToAAF/binaries/windows/
   ```

4. **Verify**:
   ```bash
   ls -lh /path/to/MXToAAF/binaries/windows/
   # Should show ffmpeg.exe and ffprobe.exe
   ```

5. **Commit**:
   ```bash
   cd /path/to/MXToAAF
   git add binaries/windows/ffmpeg.exe binaries/windows/ffprobe.exe
   git commit -m "add: Windows FFmpeg binaries"
   git push origin main
   ```

## Option 2: Automatic Download & Setup on Windows (For Future Use)

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
