#!/bin/sh
begun=$(perl -MTime::HiRes=time -e 'printf("%d", time()*1000)' 2>/dev/null)
# The agent's hooks run this: the hook body on stdin goes to the running server, and the server's status decides.
#   200  go on; the body is JSON in the agent's own hook shape, printed for it to read
#   409  refused; a body that starts with the agent's own answer (a Claude tool call denied, a prompt blocked) is printed as it is,
#        so the agent shows only the journal's line; otherwise the body's error is the reason, and exit 2 tells the agent to stop
#   anything else, or no server  go on, silently; but a worker's hook waits for its journal, and ends its session when it stays gone
# Nothing is decided here, and a deferred handler never changes the status: the server replies before it runs.
# Who runs the hook: JOURNAL_ACTOR is agent, sub-agent, or a sent agent's actor, worker:12, verifier:3 or reviewer:4, with the token that proves it in JOURNAL_ACTOR_TOKEN;
# the agent's and a sent agent's own hooks reach the journal.
# A hook whose body carries a subagent's id is a sub-agent's, whatever the variable says, since a subagent inherits the agent's shell;
# only its start, its stop and its PreToolUse reach the server. The server records and judges none of a subagent's PreToolUse and answers it {};
# it only notes a Bash one's command, to pair with the journal command the shim posts, which then runs only a subagent's reading verbs.
[ "$AGENT_JOURNAL_ACTIVE" = 1 ] || exit 0
case "${JOURNAL_ACTOR:-agent}" in agent|worker:*|verifier:*|reviewer:*) ;; *) exit 0 ;; esac
agent=$1
root=$2
port=$(cat "$root/.journal/port" 2>/dev/null)
. "$(dirname "$0")/environment.sh"
body=$(mktemp)
sent=$(mktemp)
cat > "$sent"
started=$begun
# the id of this firing, the same on a resend, so the journal records a hook it already took once
firing="$$-$started"
if grep -q '"agent_id"' "$sent" && ! grep -q '"hook_event_name": *"\(Subagent\|PreToolUse\|PostToolUse\)' "$sent"; then rm -f "$body" "$sent"; exit 0; fi
# Every hook that goes to the server first writes its time, whether or not the server takes it: the server's health compares it with
# the last hook it took, and the supervisor warns an agent whose terminal moves while this file stands still.
mkdir -p "$root/.journal/runtime/hooks" && date +%s > "$root/.journal/runtime/hooks/$(journal_environment).fired"
# The agent's own session start writes the version it started on, read by the journal to close the restart notice.
if grep -q '"hook_event_name": *"SessionStart"' "$sent"; then
    version=$(sed -n 's/^VERSION = "\(.*\)"/\1/p' "$root/.journal/src/journal/version.py" 2>/dev/null)
    mkdir -p "$root/.journal/runtime" && printf 'SessionStart %s\n' "$version" > "$root/.journal/runtime/session-version"
fi
# A journal booting or restarting is waited for, and the hook sent once it is up, its time measured from then and its wait sent along;
# a hook that finds no server listening while one boots waits and is sent again.
post() {
    curl -sS --max-time 10 -o "$body" -w '%{http_code}' -X POST "http://127.0.0.1:$port/hooks/$agent" \
        -H "Content-Type: application/json" \
        -H "X-Journal-Env: $(journal_environment)" \
        -H "X-Journal-Launch: ${JOURNAL_LAUNCH:-}" \
        -H "X-Journal-Actor: ${JOURNAL_ACTOR:-agent}" \
        -H "X-Journal-Actor-Token: ${JOURNAL_ACTOR_TOKEN:-}" \
        -H "X-Journal-Request-At: $started" \
        -H "X-Journal-Hook-Id: $firing" \
        -H "X-Journal-Boot-Wait-Ms: $waited" \
        -H "X-Journal-Silence-Start: $silence" \
        --data-binary @"$sent"
}
# A worker whose journal does not answer holds its tool, asking again every second through the grace in JOURNAL_LOCKOUT_SECONDS,
# and goes on once it answers, sending when the silence started so the journal locks the worker out on its own record;
# past the grace the worker's session ends. Any other agent's hook goes on while the journal is down.
silence=""
held() {
    case "${JOURNAL_ACTOR:-agent}" in worker:*) ;; *) return 1 ;; esac
    silence=$(date +%s)
    deadline=$((silence + ${JOURNAL_LOCKOUT_SECONDS:-30}))
    while [ "$(date +%s)" -lt "$deadline" ]; do
        sleep 1
        port=$(cat "$root/.journal/port" 2>/dev/null)
        [ -n "$port" ] && curl -s -o /dev/null --connect-timeout 2 --max-time 2 "http://127.0.0.1:$port/journal/health" && return 0
    done
    printf '{"continue": false, "stopReason": "the journal did not answer for %s seconds, so this worker ends"}\n' "${JOURNAL_LOCKOUT_SECONDS:-30}"
    rm -f "$body" "$sent"
    exit 0
}
waited=$(journal_boot_wait "$root/.journal")
[ "$waited" = 0 ] || { port=$(cat "$root/.journal/port" 2>/dev/null); started=$(perl -MTime::HiRes=time -e 'printf("%d", time()*1000)' 2>/dev/null); }
[ -n "$port" ] || held || { rm -f "$body" "$sent"; exit 0; }
# a journal that does not answer its health in two seconds is gone around: the tool goes on, and the miss is noted for the journal to say
if [ "$waited" = 0 ] && ! curl -s -o /dev/null --connect-timeout 2 --max-time 2 "http://127.0.0.1:$port/journal/health" && ! held; then
    printf '%s hook %s\n' "$(date +%s)" "$agent" >> "$root/.journal/runtime/bypass.log"
    rm -f "$body" "$sent"
    exit 0
fi
status=$(post) || status=0
if [ "$status" = 000 ] || [ "$status" = 0 ]; then
    if [ -f "$root/.journal/runtime/journal.booting" ]; then
        more=$(journal_boot_wait "$root/.journal")
        waited=$((waited + more))
        port=$(cat "$root/.journal/port" 2>/dev/null)
        started=$(perl -MTime::HiRes=time -e 'printf("%d", time()*1000)' 2>/dev/null)
        status=$(post) || status=0
    fi
fi
if [ "$status" = 000 ] || [ "$status" = 0 ]; then
    held && { status=$(post) || status=0; }
fi
kind=$(sed -n 's/.*"hook_event_name": *"\([A-Za-z]*\)".*/\1/p' "$sent" | head -n 1)
rm -f "$sent"
# Claude shows a systemMessage to the user alone: each hook's answer carries how long the hook took, from this script's first line to
# the moment its answer is printed, added to the line the journal already shows the user or standing alone.
timed() {
    [ "$agent" = claude ] && [ -n "$begun" ] || { cat; return; }
    took="journal $kind hook: $(( $(perl -MTime::HiRes=time -e 'printf("%d", time()*1000)') - begun )) ms"
    sed -e "s/\"systemMessage\": \"/\"systemMessage\": \"$took. /;t" -e "s/^{}\$/{\"systemMessage\": \"$took\"}/;t" -e "s/^{/{\"systemMessage\": \"$took\", /"
}
case "$status" in
    200) timed < "$body" ;;
    409) if grep -q '^{"answer": ' "$body"; then sed -e 's/^{"answer": \(.*\), "error": ".*$/\1/' "$body" | timed; rm -f "$body"; exit 0; fi
         sed -e 's/^{"error": *"//' -e 's/"}$//' -e 's/\\n/\n/g' "$body" >&2; rm -f "$body"; exit 2 ;;
esac
rm -f "$body"
exit 0
