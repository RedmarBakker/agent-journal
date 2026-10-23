#!/bin/bash
# The team's hosted journal in /data/journal: installed from the image's own copy at its first start, joined to the team
# once the team holds a journal, at the team's pinned version, as the service account the team server invites, then
# served on 127.0.0.1:8421 marked hosted (.journal/hosted), so every browser signs in with a team account and no agent ever starts.
# At its first start it turns the auto-update on and checks for a new release every minute, so it installs each release and
# pins the team to it.
set -euo pipefail
cd /data/journal
export JOURNAL_ROOT=/data/journal JOURNAL_PORT=8421
journal() { python .journal/src/journal.py "$@"; }
[ -f .journal/src/journal.py ] || AGENT_JOURNAL_YES=1 sh /app/install.sh >/dev/null
if [ ! -f .journal/hosted ]; then
    touch .journal/hosted
    journal settings set updates.auto on >/dev/null
    journal settings set updates.check_minutes 1 >/dev/null
fi
if [ ! -f .journal/team.json ]; then
    invitation=$(python -m sync_server hosted --data /data/team)
    field() { printf '%s' "$invitation" | python -c "import json, sys; print(json.load(sys.stdin)['$1'])"; }
    version=$(field version)
    installed=$(sed -n 's/^VERSION = "\(.*\)"$/\1/p' .journal/src/journal/version.py)
    if [ -n "$version" ] && [ "$version" != "$installed" ]; then
        cp /app/install.sh /tmp/install.sh
        AGENT_JOURNAL_YES=1 AGENT_JOURNAL_REF="v$version" sh /tmp/install.sh >/dev/null
    fi
    journal team join "http://127.0.0.1:8470/join?code=$(field code)" --email "$(field email)" --name "$(field name)" --password "$(field password)"
fi
exec python .journal/src/journal.py serve
