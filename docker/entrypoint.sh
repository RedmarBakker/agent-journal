#!/bin/sh
# Installs the local version 4 package and starts its project-owned server command.
set -eu
umask 007

: "${JOURNAL_PLAN_DRIVER_SOCKET:?set the private Plan driver launcher socket}"
PROJECT="${JOURNAL_PROJECT:-/data/project}"
ROOT="$PROJECT/.journal"
cd /

setpriv --reuid journal --regid journal --init-groups env -C "$PROJECT" HOME=/data/home JOURNAL_PROJECT="$PROJECT" sh -eu <<'SETUP'
umask 007
git config --global user.name "${GIT_NAME:-Journal on a server}"
git config --global user.email "${GIT_EMAIL:-journal@localhost}"
if [ -n "${GITHUB_TOKEN:-}" ]; then
    # Set before the clone, so a private repository's token stays in the environment and never in .git/config.
    git config --global credential.https://github.com.helper '!f() { echo username=x-access-token; echo "password=$GITHUB_TOKEN"; }; f'
fi
if [ -n "${GIT_REPOSITORY:-}" ] && [ ! -d "$JOURNAL_PROJECT/.git" ] && [ -z "$(ls -A "$JOURNAL_PROJECT")" ]; then
    git clone --quiet "$GIT_REPOSITORY" "$JOURNAL_PROJECT"
fi
mkdir -p "$JOURNAL_PROJECT/.claude"
AGENT_JOURNAL_YES=1 sh /opt/agent-journal/install.sh
SETUP

if ! setpriv --reuid 10003 --regid 10003 --clear-groups supervisor-codex-ready; then
    echo "Codex device login is missing; complete supervisor-codex-login before starting the writer" >&2
    exit 2
fi
setpriv --regid 10001 --clear-groups sh -eu -c 'printf "%s\n" "$1" > /run/journal-plan-driver-server.pid; chmod 0440 /run/journal-plan-driver-server.pid' sh "$$"
python3 -P /usr/local/bin/supervisor-codex-plan-launcher &
PLAN_LAUNCHER_PID=$!
attempt=0
while [ ! -S "$JOURNAL_PLAN_DRIVER_SOCKET" ]; do
    if ! kill -0 "$PLAN_LAUNCHER_PID" 2>/dev/null || [ "$attempt" -ge 50 ]; then
        echo "the restricted Codex Plan launcher did not become ready" >&2
        exit 2
    fi
    attempt=$((attempt + 1))
    sleep 0.1
done
exec setpriv --reuid journal --regid journal --init-groups env -C "$PROJECT" HOME=/data/home JOURNAL_ROOT="$PROJECT" JOURNAL_PORT=8421 "$ROOT/bin/journal" serve
