#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export GIT_SSH_COMMAND="ssh -i /home/papa/.ssh/id_ed25519_github -o StrictHostKeyChecking=no"

BITCOIN_DIR="/home/papa/.bitcoin"
REPO_DIR="/home/papa/bitcoin_github"
LOG="/tmp/bitcoin_github_sync.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Début sync" >> "$LOG"

cp -f "$BITCOIN_DIR/banlist.json" "$REPO_DIR/banlist.json" 2>/dev/null

mkdir -p "$REPO_DIR/blocks/index"
rsync -a --delete "$BITCOIN_DIR/blocks/index/" "$REPO_DIR/blocks/index/" 2>/dev/null

cd "$REPO_DIR" || exit 1
if [[ -n $(git status --porcelain) ]]; then
    git add .
    git commit -m "Auto sync $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main 2>> "$LOG" &&         echo "[$(date '+%Y-%m-%d %H:%M:%S')] Push OK" >> "$LOG" ||         echo "[$(date '+%Y-%m-%d %H:%M:%S')] Push ERREUR" >> "$LOG"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Aucun changement" >> "$LOG"
fi
