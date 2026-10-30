#!/bin/sh
begun=$(perl -MTime::HiRes=time -e 'printf("%d", time()*1000)' 2>/dev/null)
# The agent's hooks run this: the hook body on stdin goes to the running server, and the server's status decides.
#   200  go on; the body is JSON in the agent's own hook shape, printed for it to read
#   409  refused; a body that starts with the agent's own answer (a Claude tool call denied, a prompt blocked) is printed as it is,
#        so the agent shows only the journal's line; otherwise the body's error is the reason, and exit 2 tells the agent to stop
#   anything else, no server, or no answer within two seconds  go on, silently, noted in bypass.log
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
# the id of this firing, the same on a resend, so the journal records a hook it already took once
firing="$$-$begun"
if grep -q '"agent_id"' "$sent" && ! grep -q '"hook_event_name": *"\(Subagent\|PreToolUse\|PostToolUse\)' "$sent"; then rm -f "$body" "$sent"; exit 0; fi
# Every hook that goes to the server first writes its time, whether or not the server takes it: the server's health compares it with
# the last hook it took, and the supervisor warns an agent whose terminal moves while this file stands still.
mkdir -p "$root/.journal/runtime/hooks" && date +%s > "$root/.journal/runtime/hooks/$(journal_environment).fired"
# The agent's own session start writes the version it started on, read by the journal to close the restart notice.
if grep -q '"hook_event_name": *"SessionStart"' "$sent"; then
    version=$(sed -n 's/^VERSION = "\(.*\)"/\1/p' "$root/.journal/src/journal/version.py" 2>/dev/null)
    mkdir -p "$root/.journal/runtime" && printf 'SessionStart %s\n' "$version" > "$root/.journal/runtime/session-version"
fi
# Every hook gets its answer within its own time or goes on without the journal: a tool waits 5 seconds, the user's prompt 8,
# a stop 10, a session start 15, which may wait on a boot; the miss is noted in bypass.log for the journal to say once it is back.
# A journal that hangs never holds the agent longer than that.
event=$(sed -n 's/.*"hook_event_name": *"\([A-Za-z]*\)".*/\1/p' "$sent" | head -1)
case "$event" in
    UserPromptSubmit) ANSWER_SECONDS=8 ;;
    Stop|SubagentStop) ANSWER_SECONDS=10 ;;
    SessionStart) ANSWER_SECONDS=15 ;;
    *) ANSWER_SECONDS=5 ;;
esac
post() {
    curl -s --connect-timeout 1 --max-time "$ANSWER_SECONDS" -o "$body" -w '%{http_code}' -X POST "http://127.0.0.1:$port/hooks/$agent" \
        -H "Content-Type: application/json" \
        -H "X-Journal-Env: $(journal_environment)" \
        -H "X-Journal-Project: $root" \
        -H "X-Journal-Launch: ${JOURNAL_LAUNCH:-}" \
        -H "X-Journal-Actor: ${JOURNAL_ACTOR:-agent}" \
        -H "X-Journal-Actor-Token: ${JOURNAL_ACTOR_TOKEN:-}" \
        -H "X-Journal-Request-At: $begun" \
        -H "X-Journal-Hook-Id: $firing" \
        --data-binary @"$sent"
}
if [ -n "$port" ]; then status=$(post) || status=0; else status=0; fi
# A hook that went around is said to a Claude agent at once in its hook's answer, where its hook takes one, so it stops to look;
# in the journal's own repository it is told to start the panic watch as well. A stop takes no line: it would only stop again.
went_around() {
    printf '%s hook %s\n' "$(date +%s)" "$agent" >> "$root/.journal/runtime/bypass.log"
    [ "$agent" = claude ] || return 0
    case "$event" in PreToolUse|PostToolUse|UserPromptSubmit|SessionStart) ;; *) return 0 ;; esac
    line="[journal] The journal did not answer within $ANSWER_SECONDS seconds, so this went through unchecked. Investigate now: curl -s http://127.0.0.1:$port/journal/health should answer 200, and runtime/server.log in .journal says why it does not."
    if [ -f "$root/src/journal/hooks/hook.sh" ]; then
        line="$line This is the journal's own repository: start the panic watch, a CronCreate job every 15 minutes that checks the health, restarts the journal with journal setup restart when it does not answer, and tells the user in one line."
    fi
    printf '{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": "%s"}}\n' "$event" "$line"
}
case "$status" in
    200|409) ;;
    *) went_around ;;
esac
rm -f "$sent"
case "$status" in
    200) cat "$body" ;;
    409) if grep -q '^{"answer": ' "$body"; then sed -e 's/^{"answer": \(.*\), "error": ".*$/\1/' "$body"; rm -f "$body"; exit 0; fi
         sed -e 's/^{"error": *"//' -e 's/"}$//' -e 's/\\n/\n/g' "$body" >&2; rm -f "$body"; exit 2 ;;
esac
rm -f "$body"
exit 0
