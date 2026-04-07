#!/bin/bash
# sync_push.sh — copie les fichiers bitcoin vers bitcoin_github et push
# Appelé par cron à 3H et 15H

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no"

BITCOIN_DIR="$HOME/.bitcoin"
REPO_DIR="$HOME/bitcoin_github"
LOG="/tmp/bitcoin_github_sync.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Début sync" >> "$LOG"

# Copier les fichiers de config
cp -f "$BITCOIN_DIR/bitcoin.conf"  "$REPO_DIR/bitcoin.conf"  2>/dev/null
cp -f "$BITCOIN_DIR/banlist.json"  "$REPO_DIR/banlist.json"  2>/dev/null

# Copier blocks/index (pas les .dat — exclus par .gitignore)
mkdir -p "$REPO_DIR/blocks/index"
rsync -a --delete "$BITCOIN_DIR/blocks/index/" "$REPO_DIR/blocks/index/" 2>/dev/null

# Git push si changements
cd "$REPO_DIR" || exit 1
if [[ -n $(git status --porcelain) ]]; then
    git add .
    git commit -m "Auto sync $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main 2>> "$LOG" &&         echo "[$(date '+%Y-%m-%d %H:%M:%S')] Push OK" >> "$LOG" ||         echo "[$(date '+%Y-%m-%d %H:%M:%S')] Push ERREUR" >> "$LOG"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Aucun changement" >> "$LOG"
fi
