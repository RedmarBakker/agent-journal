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
    src \
    docker/Dockerfile \
    docker/entrypoint.sh \
    docker/hosted-journal \
    docker/supervisor-codex-login \
    docker/supervisor-codex-ready \
    docker/supervisor-codex-plan-launcher.py \
    docs/supervisor/v1/live-smoke-setup.py > "$BUILD_CONTEXT/runtime.tar"
tar -xf "$BUILD_CONTEXT/runtime.tar" -C "$BUILD_CONTEXT"
rm "$BUILD_CONTEXT/runtime.tar"

docker build \
    --label "org.opencontainers.image.revision=$PROFILE_REVISION" \
    --file "$BUILD_CONTEXT/docker/Dockerfile" \
    --tag "agent-journal-supervisor-writer:$PROFILE_REVISION" \
    "$BUILD_CONTEXT"
