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
    src/supervisor_bridge \
    docs/supervisor/v1/Dockerfile.gateway \
    docs/supervisor/v1/journal-supervisor-bridge > "$BUILD_CONTEXT/runtime.tar"
tar -xf "$BUILD_CONTEXT/runtime.tar" -C "$BUILD_CONTEXT"
rm "$BUILD_CONTEXT/runtime.tar"

docker build \
    --pull \
    --label "org.opencontainers.image.revision=$PROFILE_REVISION" \
    --file "$BUILD_CONTEXT/docs/supervisor/v1/Dockerfile.gateway" \
    --tag "agent-journal-supervisor-gateway:$PROFILE_REVISION" \
    "$BUILD_CONTEXT"
