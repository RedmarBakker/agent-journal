#!/bin/sh
set -eu

. /opt/journal-supervisor/bin/journal-supervisor-environment

/opt/journal-supervisor/bin/journal-supervisor-bridge proxy &
proxy_pid=$!
gateway_pid=
event_watcher_pid=

stop_children() {
    if [ -n "$gateway_pid" ]; then
        kill -TERM "$gateway_pid" 2>/dev/null || true
    fi
    if [ -n "$event_watcher_pid" ]; then
        kill -TERM "$event_watcher_pid" 2>/dev/null || true
    fi
    kill -TERM "$proxy_pid" 2>/dev/null || true
    if [ -n "$gateway_pid" ]; then
        wait "$gateway_pid" 2>/dev/null || true
    fi
    if [ -n "$event_watcher_pid" ]; then
        wait "$event_watcher_pid" 2>/dev/null || true
    fi
    wait "$proxy_pid" 2>/dev/null || true
}

trap stop_children EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

/opt/journal-supervisor/bin/journal-supervisor-bridge wait-for-proxy
case_wake_file="${JOURNAL_SUPERVISOR_STATE_DIR%/*}/journal-supervisor-case-wake"
if [ ! -r "$case_wake_file" ]; then
    /opt/journal-supervisor/bin/journal-supervisor-bridge watch-events &
    event_watcher_pid=$!
fi
node dist/index.js gateway run --port "${OPENCLAW_GATEWAY_PORT:-18789}" &
gateway_pid=$!
gateway_status=0
wait "$gateway_pid" || gateway_status=$?
exit "$gateway_status"
