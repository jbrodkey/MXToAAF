# MXToAAF (Windows) - Readme

**Version 1.0.0**

## Overview

MXToAAF converts music files (MP3, M4A, WAV, AIF, AIFF) to professional AAF files for Avid Media Composer and other professional editing software. It extracts and preserves music metadata, supports batch processing, and optionally (by default) embeds audio directly in the AAF.

## Quick Start

1. Run **MXToAAF.exe**
2. Choose a music file or folder
3. (Optional) Set output location; otherwise files go to `AAFs` folder next to your source
4. Click **Run**; AAF files appear in your output location
5. Click **Open AAF Location** to reveal the created files

## Features

- **Batch Processing**: Convert entire folders of music files
- **Single File Mode**: Process individual files
- **Embedded Audio**: Audio is embedded in AAF files by default; can be toggled off
- **Real-time Progress**: See processing status as files are converted
- **CSV Export** (optional): Export conversion results and metadata to CSV
- **Frame Rate Control**: Set custom frame rates (default 24fps)
- **Stereo Panning**: Full support for stereo pan automation in AAF

## Output Structure

### Default Output (Folder Processing)

When you select a folder like `C:\Music\Rock\AC_DC\Back In Black\`:
- Output goes to: `C:\Music\AAFs\AC_DC\Back In Black\`
- All AAF files are created with their directory structure mirrored

### Default Output (Single File)

When you select a single file like `C:\Music\song.mp3`:
- Output goes to: `C:\Music\AAFs\song.aaf`

### Manual Output

If you set a custom output folder, AAF files go to `{your_folder}\AAFs\`

## System Requirements

- Windows 10 or later
- No additional software required (all dependencies are bundled)

## Troubleshooting

### App Won't Launch
- Ensure you're running Windows 10 or later
- Try right-clicking the `.exe` and choosing "Run as Administrator"
- Check that your system has read/write permissions in the output folder

### Windows Defender / SmartScreen Warning
- This warning appears because the app isn't code-signed
- Click **More info** then **Run anyway** to proceed
- It's safe to open; the app is unsigned only because it's community-built

## Support

Releases: https://editcandy.com  
Issues: jason@editcandy.com