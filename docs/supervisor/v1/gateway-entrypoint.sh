#!/bin/sh
set -eu

. /opt/journal-supervisor/bin/journal-supervisor-environment

exec node dist/index.js gateway run --port "${OPENCLAW_GATEWAY_PORT:-18789}"
