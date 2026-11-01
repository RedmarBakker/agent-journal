#!/bin/sh
set -eu

: "${TENANT_PROJECT:?set the unique Compose project name}"
: "${PROJECT_EXPORT:?set the owner-approved project clone path}"
: "${PROJECT_REVISION:?set the owner-approved project commit}"
: "${PROFILE_REVISION:?set the reviewed source commit}"

if [ ! -d "$PROJECT_EXPORT/.git" ]; then
    echo "PROJECT_EXPORT must be the owner-approved project clone with its history" >&2
    exit 2
fi
if [ -n "$(git -C "$PROJECT_EXPORT" status --porcelain --untracked-files=all)" ]; then
    echo "PROJECT_EXPORT must be clean; refusing to copy untracked or modified files" >&2
    exit 2
fi
if [ "$(git -C "$PROJECT_EXPORT" rev-parse HEAD)" != "$PROJECT_REVISION" ]; then
    echo "PROJECT_EXPORT HEAD must equal PROJECT_REVISION" >&2
    exit 2
fi

tracked_paths=$(git -C "$PROJECT_EXPORT" ls-tree -r --name-only HEAD)
while IFS= read -r tracked_path; do
    case "$tracked_path" in
        .journal/*|.codex/*|.claude/*|.env|*/.env|secrets/*|*/secrets/*|*.pem|*.key)
            echo "PROJECT_EXPORT contains a runtime, private-settings, secret, or key path; refusing to seed" >&2
            exit 2
            ;;
    esac
done <<EOF
$tracked_paths
EOF

IMAGE="agent-journal-supervisor-writer:${PROFILE_REVISION}"
VOLUME="${TENANT_PROJECT}_writer_state"
ARCHIVE=$(mktemp)
chmod 0600 "$ARCHIVE"
trap 'rm -f "$ARCHIVE"' EXIT HUP INT TERM

git -C "$PROJECT_EXPORT" archive --format=tar HEAD -- \
    . \
    ':(exclude).journal/**' \
    ':(exclude).codex/**' \
    ':(exclude).claude/**' > "$ARCHIVE"

docker run --rm \
    --network none \
    --user 10001:10001 \
    --env "PROJECT_REVISION=$PROJECT_REVISION" \
    --entrypoint /bin/sh \
    --mount "type=bind,src=$ARCHIVE,dst=/seed.tar,readonly" \
    --mount "type=volume,src=$VOLUME,dst=/data" \
    "$IMAGE" -eu -c '
        mkdir -p /data/project
        if [ -n "$(ls -A /data/project)" ]; then
            echo "writer project folder is not empty; refusing to replace it" >&2
            exit 3
        fi
        tar -xf /seed.tar -C /data/project
        git -C /data/project init --initial-branch=main
        git -C /data/project add --all
        git -C /data/project \
            -c user.name="Journal project owner" \
            -c user.email="journal-project-owner@localhost" \
            commit --message "Seed project at $PROJECT_REVISION"
    '
