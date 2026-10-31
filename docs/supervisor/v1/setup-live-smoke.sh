#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
ENV_FILE="$ROOT/docs/supervisor/v1/live-smoke.env"
COMPOSE_FILE="$ROOT/docs/supervisor/v1/compose.json"

if [ "${STAGING_AUTHORIZED:-}" != "1" ] || [ "$(id -u)" -ne 0 ]; then
    echo "run only as root after owner/operator authorization with STAGING_AUTHORIZED=1" >&2
    exit 2
fi

SECRET_SOURCE_DIR=$(python3 - "$ENV_FILE" <<'PY'
import sys
from pathlib import Path

settings = {}
for line in Path(sys.argv[1]).read_text().splitlines():
    if line.startswith(("TENANT_SECRET_SOURCE_DIR=", "TENANT_SECRET_DIR=")):
        name, value = line.split("=", 1)
        if name in settings or not value.startswith("/") or any(char.isspace() or char in "$`\\'\"" for char in value):
            raise SystemExit("live-smoke.env has an invalid tenant secret directory")
        settings[name] = value
if len(settings) != 2 or settings["TENANT_SECRET_SOURCE_DIR"] != settings["TENANT_SECRET_DIR"]:
    raise SystemExit("TENANT_SECRET_SOURCE_DIR and TENANT_SECRET_DIR must name the same private directory")
print(settings["TENANT_SECRET_SOURCE_DIR"])
PY
)

if [ ! -d "$SECRET_SOURCE_DIR" ] || [ "$(stat -c %u "$SECRET_SOURCE_DIR")" != "0" ] || [ "$(stat -c %a "$SECRET_SOURCE_DIR")" != "700" ]; then
    echo "the tenant secret source directory must be root-owned mode 0700" >&2
    exit 2
fi
if [ -e "$SECRET_SOURCE_DIR/journal_supervisor_credential" ]; then
    echo "journal_supervisor_credential already exists; refusing to replace it" >&2
    exit 2
fi

compose() {
    docker compose --project-name journal-supervisor-smoke --env-file "$ENV_FILE" \
        -f "$COMPOSE_FILE" --profile authorized-staging "$@"
}

STAGING_DIR=$(mktemp -d "$SECRET_SOURCE_DIR/.supervisor-setup.XXXXXX")
chmod 0700 "$STAGING_DIR"
trap 'rm -rf "$STAGING_DIR"' EXIT HUP INT TERM
compose exec --user 10001:10001 -T writer /usr/local/bin/supervisor-live-setup
compose cp writer:/run/journal_supervisor_credential "$STAGING_DIR/journal_supervisor_credential"
python3 - "$STAGING_DIR/journal_supervisor_credential" <<'PY'
import re
import sys
from pathlib import Path

token = Path(sys.argv[1]).read_bytes()
if not re.fullmatch(rb"[A-Za-z0-9_-]{32,128}", token):
    raise SystemExit("the staged writer returned no valid enrollment credential")
PY
install -o root -g 1000 -m 0440 "$STAGING_DIR/journal_supervisor_credential" "$STAGING_DIR/credential"
ln "$STAGING_DIR/credential" "$SECRET_SOURCE_DIR/journal_supervisor_credential"
echo "the staged writer's owner grant credential is ready for the Gateway secret mount"
