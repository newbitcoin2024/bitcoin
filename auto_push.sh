#!/bin/bash

cd "/Users/francisc/Library/Application Support/Bitcoin"

git add .
git commit -m "Auto update $(date '+%Y-%m-%d %H:%M:%S')" || exit 0
git push
