#!/bin/sh
set -eu

: "${RUNTIME_SOURCE:?set an absolute path to the reviewed journal runtime checkout}"
: "${PROFILE_REVISION:?set the reviewed runtime source commit}"

if [ "$(git -C "$RUNTIME_SOURCE" rev-parse HEAD)" != "$PROFILE_REVISION" ]; then
    echo "RUNTIME_SOURCE HEAD must equal PROFILE_REVISION" >&2
    exit 2
fi
if [ -n "$(git -C "$RUNTIME_SOURCE" status --porcelain --untracked-files=all)" ]; then
    echo "RUNTIME_SOURCE must be clean; refusing to build from modified or untracked files" >&2
    exit 2
fi

BUILD_CONTEXT=$(mktemp -d)
trap 'rm -rf "$BUILD_CONTEXT"' EXIT HUP INT TERM
git -C "$RUNTIME_SOURCE" archive --format=tar "$PROFILE_REVISION" -- \
    src/supervisor_bridge/codex_driver_secret_stage.c \
    src/supervisor_bridge/live_smoke_settings.h > "$BUILD_CONTEXT/source.tar"
tar -xf "$BUILD_CONTEXT/source.tar" -C "$BUILD_CONTEXT"
rm "$BUILD_CONTEXT/source.tar"
cc -std=c11 -Wall -Wextra -Werror -O2 \
    "$BUILD_CONTEXT/src/supervisor_bridge/codex_driver_secret_stage.c" \
    -o "$BUILD_CONTEXT/journal-supervisor-driver-secret-stage"
install -o root -g root -m 0755 "$BUILD_CONTEXT/journal-supervisor-driver-secret-stage" \
    /usr/local/bin/journal-supervisor-driver-secret-stage
