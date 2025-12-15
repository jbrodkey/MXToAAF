#!/bin/zsh
# Script to create WAVsToAAF DMG

create-dmg \
  --volname "MXToAAF v1.0.0" \
  --volicon "DMG_Icon/DMG.icns" \
  --background "dmg-background-light.png" \
  --window-pos 200 120 \
  --window-size 620 450 \
  --icon-size 120 \
  --text-size 14 \
  --icon "MXToAAF.app" 148 260 \
  --icon "README.md" 300 100 \
  --app-drop-link 460 260 \
  "MXToAAF_v1.0.0.dmg" \
  "DMG_Contents_STAGING"