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

REM Build with PyInstaller
echo.
echo Building application...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --icon "icons/win/MXToAAF.ico" ^
    --add-data "LICENSES.txt;." ^
    --onefile ^
    --windowed ^
    --hidden-import=tkinter ^
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
mkdir dist_package 2>nul
copy dist\MXToAAF.exe dist_package\
copy LICENSES.txt dist_package\
copy docs\README_windows.md dist_package\README.md

echo.
echo Build complete!
echo.
echo Distribution package: dist_package\
echo   - MXToAAF.exe
echo   - README.md
echo   - LICENSES.txt
echo.
echo To run the app:
echo   dist_package\MXToAAF.exe
echo.
echo To distribute, zip the entire dist_package folder.
echo.
pause
