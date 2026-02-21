#!/bin/bash
cd "$(dirname "$0")"
git add .
git commit -m "${1:-Mise à jour}"
git push origin main

