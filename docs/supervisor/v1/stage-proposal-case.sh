#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
ENV_FILE="$ROOT/docs/supervisor/v1/live-smoke.env"
COMPOSE_FILE="$ROOT/docs/supervisor/v1/compose.json"
CASE_ID=${1:-}
VOLUME=journal-supervisor-smoke_writer_state
IMAGE="agent-journal-supervisor-writer:${PROFILE_REVISION:-}"

if [ "${STAGING_AUTHORIZED:-}" != "1" ] || [ "$(id -u)" -ne 0 ]; then
    echo "run only as root after owner/operator authorization with STAGING_AUTHORIZED=1" >&2
    exit 2
fi
case "$CASE_ID" in
    PSU-[0-9][0-9]) ;;
    *) echo "name one frozen case, for example PSU-01" >&2; exit 2 ;;
esac
: "${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed writer image revision}"
: "${PROJECT_EXPORT:?set PROJECT_EXPORT to the owner-approved clean project clone}"
: "${PROJECT_REVISION:?set PROJECT_REVISION to that clone's reviewed commit}"

if [ ! -f "$ENV_FILE" ]; then
    echo "the owner-local docs/supervisor/v1/live-smoke.env is required" >&2
    exit 2
fi
if [ ! -d "$PROJECT_EXPORT/.git" ]; then
    echo "PROJECT_EXPORT must be the owner-approved project clone" >&2
    exit 2
fi
SEED_DIR=$(mktemp -d)
chmod 0700 "$SEED_DIR"
trap 'rm -rf "$SEED_DIR"' EXIT HUP INT TERM
PYTHONPATH="$ROOT/src" python3 - "$ROOT/docs/supervisor/v1/proposal-evaluation-cases-v1.json" "$CASE_ID" > "$SEED_DIR/case-seed.json" <<'PY'
import json
import sys
from supervisor_bridge.proposal_evaluation import load_case, seed_case

print(json.dumps(seed_case(load_case(sys.argv[1], sys.argv[2])), separators=(",", ":")))
PY
chmod 0444 "$SEED_DIR/case-seed.json"

SECRET_SOURCE_DIR=$(python3 - "$ENV_FILE" <<'PY'
import sys
from pathlib import Path

values = {}
for line in Path(sys.argv[1]).read_text().splitlines():
    if line.startswith("TENANT_SECRET_SOURCE_DIR="):
        values["secret"] = line.split("=", 1)[1]
if len(values) != 1 or not values["secret"].startswith("/") or any(c.isspace() or c in "$`\\'\"" for c in values["secret"]):
    raise SystemExit("live-smoke.env has an invalid tenant secret source directory")
print(values["secret"])
PY
)
GATEWAY_STATE_PATH=$(python3 - "$ENV_FILE" <<'PY'
import sys
from pathlib import Path

values = [line.split("=", 1)[1] for line in Path(sys.argv[1]).read_text().splitlines() if line.startswith("GATEWAY_STATE_PATH=")]
if len(values) != 1 or not values[0].startswith("/") or values[0] == "/" or any(c.isspace() or c in "$`\\'\"" for c in values[0]):
    raise SystemExit("live-smoke.env has an invalid Gateway state directory")
print(values[0])
PY
)
if [ ! -d "$SECRET_SOURCE_DIR" ] || [ "$(stat -c %u "$SECRET_SOURCE_DIR")" != "0" ] || [ "$(stat -c %a "$SECRET_SOURCE_DIR")" != "700" ]; then
    echo "the tenant secret source directory must be root-owned mode 0700" >&2
    exit 2
fi
if [ ! -d "$GATEWAY_STATE_PATH" ] || [ -L "$GATEWAY_STATE_PATH" ] || [ "$(stat -c '%u:%g:%a' "$GATEWAY_STATE_PATH")" != "1000:10030:750" ]; then
    echo "the Gateway state directory must be a real uid 1000:gid 10030 directory with mode 0750" >&2
    exit 2
fi

compose() {
    docker compose --project-name journal-supervisor-smoke --env-file "$ENV_FILE" \
        -f "$COMPOSE_FILE" --profile authorized-staging "$@"
}

compose down
rm -f "$SECRET_SOURCE_DIR/journal_supervisor_credential"
rm -rf "$GATEWAY_STATE_PATH/journal-supervisor-transport"
docker run --rm --network none --user 0:0 --entrypoint /bin/sh \
    --mount type=volume,src=journal-supervisor-smoke_supervisor_hints,dst=/hints \
    "$IMAGE" -eu -c 'find /hints -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +'
docker run --rm --network none --user 0:0 --entrypoint /bin/sh \
    --mount "type=volume,src=$VOLUME,dst=/data" "$IMAGE" -eu -c \
    'rm -rf /data/project && mkdir -p /data/project'
TENANT_PROJECT=journal-supervisor-smoke PROJECT_EXPORT="$PROJECT_EXPORT" \
    PROJECT_REVISION="$PROJECT_REVISION" PROFILE_REVISION="$PROFILE_REVISION" \
    "$ROOT/docs/supervisor/v1/seed-project.sh"

compose up -d writer
compose exec -T --user journal writer sh -c 'umask 077; cat > /run/journal-proposal-case-seed.json' < "$SEED_DIR/case-seed.json"
compose exec --detach --user 10001:10001 --env JOURNAL_ROOT=/data/project \
    --env JOURNAL_PORT=8421 --env CODEX_HOME=/data/home/.codex -T writer \
    /data/project/.journal/bin/journal codex --env main --yes --no-open
STAGING_AUTHORIZED=1 JOURNAL_SUPERVISOR_CASE_ID="$CASE_ID" \
    "$ROOT/docs/supervisor/v1/setup-live-smoke.sh"
echo "case $CASE_ID is staged; run journal secret run 1 -- journal-supervisor-smoke"
