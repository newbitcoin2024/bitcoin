#!/bin/bash

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

cd "/Users/francisc/Library/Application Support/Bitcoin" || exit

if [[ -n $(git status --porcelain) ]]; then
    git add .
    git commit -m "Auto push $(date '+%Y-%m-%d %H:%M:%S')"
    git push
fi
