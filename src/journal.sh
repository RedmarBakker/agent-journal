#!/bin/sh
# The journal command. With a server up it posts the argv there; without one it runs the package directly.
# A command is posted as the shell's environment, a double NUL and each word ended by a NUL; the server finds who runs it
# from the environment, as it does for a shell line, and answers what it printed with the exit code on its last line.
# A plugin names itself with JOURNAL_PLUGIN and JOURNAL_PLUGIN_TOKEN, and the server stamps the plugin.
here=$(cd "$(dirname "$0")" && pwd)
. "$here/journal/hooks/environment.sh"
root=${JOURNAL_ROOT:-$(journal_main_root)}
# The Python 3.14 the install found, kept beside the package; python3 only where an install from before it left none.
py=$(cat "$here/../python" 2>/dev/null)
[ -x "$py" ] || py=python3
case "$1" in
    claude|codex|serve|setup|remote) cd "$root" && exec "$py" "$here/journal.py" "$@" ;;
esac
# Who runs the command: JOURNAL_ACTOR is agent, sub-agent, or a sent agent's actor, worker:12, verifier:3 or reviewer:4, sent to the server as a header, with a Codex thread's id.
# A subagent of Claude Code inherits the agent's shell whole, so nothing in its environment tells it apart here; the server pairs the command with the Bash PreToolUse hook a subagent announced it in (the only subagent hook it keeps).
JOURNAL_ENV=$(journal_environment)
export JOURNAL_ENV
port=$(cat "$root/.journal/port" 2>/dev/null)
# Joining a team or logging in again asks the person's password here, unseen, and hands it to the server with the words,
# so it never stands on a command line; an agent's shell has no terminal, and the command then says to run it yourself.
if [ "$1" = "team" ] && { [ "$2" = "join" ] || [ "$2" = "login" ]; } && [ -t 0 ]; then
    case "$*" in *code=*) printf 'Choose your password: ' >&2 ;; *) printf 'Your team password: ' >&2 ;; esac
    stty -echo
    IFS= read -r password
    stty echo
    printf '\n' >&2
    set -- "$@" "--password=$password"
fi
# An alias is answered with __journal_exec and its line: awk hands the line out on fd 3, and the shim runs it in the project.
# Each line is printed as it arrives, so a command that streams shows its progress; no __journal_exit line at the end is the server's fault, an error with exit code 1.
# A command waits for its answer as long as it runs, since a merge waits out the plugins' window. Only a server that could not be
# reached (curl 7, or 28 on connecting) lets the package run the command here; one that took it and broke off may still be running
# it, and a second run beside it would write over what the first writes.
if [ -n "$port" ]; then
    request_at=$(perl -MTime::HiRes=time -e 'printf("%d", time()*1000)' 2>/dev/null)
    { line=$({ env -0; printf '\0\0'; for word in "$@"; do printf '%s\0' "$word"; done; } \
        | { curl -sN --connect-timeout 2 -X POST "http://127.0.0.1:$port/cli/run" -H "Content-Type: application/octet-stream" -H "X-Journal-Env: $JOURNAL_ENV" -H "X-Journal-Actor: ${JOURNAL_ACTOR:-agent}" -H "X-Journal-Thread: ${CODEX_THREAD_ID:-}" -H "X-Journal-Request-At: $request_at" --data-binary @- || echo "__journal_unanswered $?"; } \
        | awk '/^__journal_exec / { print substr($0, 16) | "cat >&3"; next } /^__journal_exit / { ended = $0; next } /^__journal_unanswered / { unanswered = substr($0, 22); next } /^\{"error": ?"/ { fault = $0; next } { print; fflush(); printed++; last = $0 } END { if (!printed && fault == "" && ended == "" && (unanswered == "" || unanswered ~ /^(7|28)$/)) exit 255; if (fault != "") { print fault > "/dev/stderr"; exit 1 } if (unanswered != "") { print "the journal server took the command and broke off before answering (curl " unanswered "); it may still be running it, so it was not run a second time: look at its outcome before running it again" > "/dev/stderr"; exit 1 } if (ended == "") { print (last == "" ? "the journal server stopped answering before the command ended" : last) > "/dev/stderr"; exit 1 } split(ended, exit_line, " "); exit exit_line[2] + 0 }' 3>&1 >&4); } 4>&1
    status=$?
    [ -n "$line" ] && cd "$root" && exec sh -c "$line"
    [ "$status" -ne 255 ] && exit "$status"
fi
# No server answered (none up, or a port file left by one that died): the package runs the command itself, unless a sub-agent
# or a worker runs it, whose commands only the server can check.
case "${JOURNAL_ACTOR:-agent}" in sub-agent|worker:*|verifier:*|reviewer:*) echo "the journal is restarting: run the command again in a moment" >&2; exit 1 ;; esac
# With no journal running, journal update installs the release here at once: an apply hands the install to a server, and there is none.
case "$#:$1:$2" in 1:update:|2:update:apply) set -- update install ;; esac
cd "$root" && exec "$py" "$here/journal.py" "$@"
