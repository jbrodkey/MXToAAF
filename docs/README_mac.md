# MXToAAF (macOS) - Readme

**Version 1.0.0**

## Overview

MXToAAF converts music files (MP3, M4A, WAV, AIF, AIFF) to professional AAF files for Avid Media Composer and other professional editing software. It extracts and preserves music metadata, supports batch processing, and optionally (by default) embeds audio directly in the AAF.

## Quick Start

1. Open **MXToAAF.app**
2. Choose a music file or folder
3. (Optional) Set output location; otherwise files go to `AAFs` folder next to your source
4. Click **Run**; AAF files appear in your output location
5. Click **Open AAF Location** to reveal the created files

## Features

- **Batch Processing**: Convert entire folders of music files
- **Single File Mode**: Process individual files
- **Embedded Audio**: Audio can be embedded directly in AAF files for easy import
- **Real-time Progress**: See processing status as files are converted
- **CSV Export** (optional): Export conversion results and metadata to CSV
- **Frame Rate Control**: Set custom frame rates (default 24fps)
- **Stereo Panning**: Full support for stereo pan automation in AAF

## Output Structure

### Default Output (Folder Processing)

When you select a folder like `Music/Rock/AC_DC/Back In Black/`:
- Output goes to: `Music/AAFs/AC_DC/Back In Black/`
- All AAF files are created with their directory structure mirrored

### Default Output (Single File)

When you select a single file like `Music/song.mp3`:
- Output goes to: `Music/AAFs/song.aaf`

### Manual Output

If you set a custom output folder, AAF files go to `{your_folder}/AAFs/`

## Troubleshooting

### App Won't Launch
- Ensure you're using macOS 10.14 or later
- Try the "Open Anyway" workaround below

### Opening MXToAAF on a Mac (macOS)

If you see a security warning:

> "App can't be opened because it is from an unidentified developer."

OR

> "Apple could not verify..."

You'll need to:

1. Open **System Settings** > **Privacy & Security**
2. Scroll down to **Security**
3. At the line for **MXToAAF** choose: **Open Anyway**

The warning appears on first run because the app isn't code-signed. It's safe to open.

## Support

Releases: https://editcandy.com  
Issues: jason@editcandy.com