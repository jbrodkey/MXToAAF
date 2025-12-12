@echo off
REM Build script for MXToAAF Windows executable
REM Usage: build_windows.bat

setlocal enabledelayedexpansion

echo Building MXToAAF for Windows...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check for FFmpeg binaries
if not exist "binaries\windows\ffmpeg.exe" (
    echo Error: FFmpeg binaries not found in binaries\windows\
    echo Please download ffmpeg.exe and ffprobe.exe from:
    echo   https://www.gyan.dev/ffmpeg/builds/
    echo And place them in: binaries\windows\
    pause
    exit /b 1
)
if not exist "binaries\windows\ffprobe.exe" (
    echo Error: ffprobe.exe not found in binaries\windows\
    echo Please download from https://www.gyan.dev/ffmpeg/builds/
    echo And place in: binaries\windows\
    pause
    exit /b 1
)
echo ✓ Found FFmpeg binaries

REM Check if PyInstaller is installed
python -m pip show pyinstaller > nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if requirements are installed
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some dependencies may not have installed correctly
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist build (
    rmdir /s /q build
)
if exist dist (
    rmdir /s /q dist
)

REM Build with PyInstaller, bundling FFmpeg
echo.
echo Building application with bundled FFmpeg...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --icon "icons/win/MXToAAF.ico" ^
    --add-data "LICENSES.txt;." ^
    --add-data "docs/README_windows.md;docs" ^
    --add-data "icons/win/MXToAAF.ico;icons/win" ^
    --add-binary "binaries/windows/ffmpeg.exe;binaries" ^
    --add-binary "binaries/windows/*.dll;binaries" ^
    --onefile ^
    --windowed ^
    --hidden-import=tkinter ^
    --hidden-import=aaf2 ^
    --hidden-import=aaf2.auid ^
    --hidden-import=aaf2.rational ^
    --hidden-import=aaf2.misc ^
    --name "MXToAAF" ^
    mxto_aaf_gui.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

REM Create distribution folder with exe and documentation
echo.
echo Creating distribution package...
mkdir dist_package\MXToAAF 2>nul
copy dist\MXToAAF.exe dist_package\MXToAAF\
copy LICENSES.txt dist_package\MXToAAF\
copy docs\README_windows.md dist_package\MXToAAF\README.md

echo.
echo Build complete!
echo.
echo Distribution package: dist_package\MXToAAF\
echo   - MXToAAF.exe (includes bundled FFmpeg)
echo   - README.md
echo   - LICENSES.txt
echo.
echo To run the app:
echo   dist_package\MXToAAF\MXToAAF.exe
echo.
echo To distribute, zip the entire dist_package\MXToAAF folder.
echo.
pause


echo.
echo Build complete!
echo.
echo Distribution package: dist_package\MXToAAF\
echo   - MXToAAF.exe
echo   - README.md
echo   - LICENSES.txt
echo.
echo To run the app:
echo   dist_package\MXToAAF\MXToAAF.exe
echo.
echo To distribute, zip the entire dist_package\MXToAAF folder.
echo.
pause
