#!/bin/sh
set -eu

: "${TENANT_ID:?set TENANT_ID}"
: "${RESTIC_PASSWORD_FILE:?set RESTIC_PASSWORD_FILE}"
: "${RESTIC_REPOSITORY_FILE:?set RESTIC_REPOSITORY_FILE}"

RESTIC_PASSWORD=$(cat "$RESTIC_PASSWORD_FILE")
RESTIC_REPOSITORY=$(cat "$RESTIC_REPOSITORY_FILE")
export RESTIC_PASSWORD RESTIC_REPOSITORY
export RESTIC_CACHE_DIR=/tmp/restic-cache
mkdir -p "$RESTIC_CACHE_DIR"

if [ -r "${AWS_SHARED_CREDENTIALS_FILE:-}" ]; then
    export AWS_SHARED_CREDENTIALS_FILE
fi

if [ -n "${RESTORE_SNAPSHOT:-}" ]; then
    restic restore "$RESTORE_SNAPSHOT" --target /restore-candidate --host "$TENANT_ID"
    exit 0
fi

restic cat config >/dev/null 2>&1 || restic init
while true; do
    restic backup /data /gateway \
        --exclude /data/secrets \
        --exclude /data/home/.codex \
        --exclude /data/home/.claude \
        --exclude /data/project/.journal/runtime \
        --host "$TENANT_ID" \
        --tag supervisor-v1
    restic forget --host "$TENANT_ID" --keep-daily 7 --keep-weekly 4 --keep-tag final --prune
    [ "${BACKUP_ONCE:-}" = "1" ] && exit 0
    sleep "${BACKUP_EVERY:-3600}"
done
