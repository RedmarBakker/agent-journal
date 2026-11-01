#!/bin/sh
# Builds the version 4 image and proves the hosted login boundary on this machine's Docker.
set -eu
cd "$(dirname "$0")"
WORK="$(mktemp -d)"
export COMPOSE_PROJECT_NAME=journal-proof
PASSWORD="$(openssl rand -hex 32)"
REVISION="$(git -C .. rev-parse HEAD)"
IMAGE=agent-journal:local
SITE=https://localhost:18443
printf 'JOURNAL_ADDRESS=localhost\nJOURNAL_HOSTED_PASSWORD=%s\nJOURNAL_IMAGE=%s\nHTTP_PORT=18080\nHTTPS_PORT=18443\nJOURNAL_ENV_FILE=%s/backup.env\nBACKUP_FOLDER=%s/backups\n' "$PASSWORD" "$IMAGE" "$WORK" "$WORK" > "$WORK/compose.env"
printf 'JOURNAL_ADDRESS=localhost\nJOURNAL_IMAGE=%s\nHTTP_PORT=18080\nHTTPS_PORT=18443\nJOURNAL_ENV_FILE=%s/backup.env\n' "$IMAGE" "$WORK" > "$WORK/no-password.env"
: > "$WORK/backup.env"
mkdir -p "$WORK/backups"
compose() { docker compose --env-file "$WORK/compose.env" "$@"; }
pass() { echo "ok   $1"; }
fail() { echo "FAIL $1"; compose --profile journal logs --tail 40 journal hosted-login caddy >&2 || true; exit 1; }
cleanup() { compose --profile journal --profile restore down -v --remove-orphans >/dev/null 2>&1 || true; rm -rf "$WORK"; }
trap cleanup EXIT

[ "${SKIP_BUILD:-}" = "1" ] || docker build -q --build-arg "JOURNAL_REVISION=$REVISION" -f Dockerfile -t "$IMAGE" .. >/dev/null
if docker compose --env-file "$WORK/no-password.env" --profile journal config >/dev/null 2>&1; then
    fail "Compose accepted a hosted deployment without its login password"
fi
pass "Compose refuses to configure the public front door without a password"

compose --profile journal up -d --no-deps journal hosted-login >/dev/null 2>&1
WRITER="$(compose --profile journal ps -q journal)"
for _ in $(seq 1 90); do
    [ "$(docker inspect --format '{{.State.Health.Status}}' "$WRITER" 2>/dev/null || true)" = healthy ] && break
    sleep 2
done
[ "$(docker inspect --format '{{.State.Health.Status}}' "$WRITER")" = healthy ] && pass "the version 4 journal answers its own health route" || fail "the version 4 journal did not become healthy"
LOGIN="$(compose --profile journal ps -q hosted-login)"
[ "$(docker inspect --format '{{.Config.User}}' "$LOGIN")" = "10002:10001" ] && pass "the login proxy runs as its separate uid" || fail "the login proxy runs with the wrong identity"
[ "$(docker inspect --format '{{json .Mounts}}' "$LOGIN")" = "[]" ] && pass "the login proxy has no journal or project mounts" || fail "the login proxy has a shared data mount"
case "$(docker inspect --format '{{json .Config.Env}}' "$WRITER")" in
    *JOURNAL_HOSTED_PASSWORD*) fail "the journal process received the hosted password" ;;
    *) pass "the journal container does not receive the hosted password" ;;
esac
[ "$(docker inspect --format '{{json .HostConfig.PortBindings}}' "$WRITER")" = "null" ] && pass "the journal server has no published host port" || fail "the journal server is published directly"

compose --profile journal up -d caddy >/dev/null 2>&1
for _ in $(seq 1 60); do
    curl -sk "$SITE/login" >/dev/null 2>&1 && break
    sleep 1
done
STATUS="$(curl -sk -D "$WORK/anonymous.headers" -o "$WORK/anonymous.body" -w '%{http_code}' "$SITE/journal/manifest")"
[ "$STATUS" = 303 ] && grep -qi '^Location: /login?next=' "$WORK/anonymous.headers" && [ ! -s "$WORK/anonymous.body" ] \
    && pass "an unauthenticated visitor is redirected before reaching the journal" || fail "an unauthenticated visitor reached the journal"
curl -sk "$SITE/login" | grep -q 'type="password"' && pass "the login form is available to a visitor" || fail "the login form did not load"
curl -sk -D "$WORK/login.headers" -c "$WORK/cookies" -o /dev/null --data-urlencode "password=$PASSWORD" --data-urlencode "next=/journal/health" "$SITE/login"
grep -qi '^Set-Cookie: journal_hosted_session=.*HttpOnly; Secure; SameSite=Lax' "$WORK/login.headers" \
    && pass "a successful login gets a private session cookie" || fail "the session cookie has unsafe flags"
[ "$(curl -sk -b "$WORK/cookies" -o /dev/null -w '%{http_code}' "$SITE/journal/health")" = 200 ] \
    && pass "an authenticated visitor reaches the version 4 journal" || fail "the authenticated visitor did not reach the journal"

compose --profile journal restart hosted-login >/dev/null
for _ in $(seq 1 30); do compose --profile journal exec -T hosted-login curl -fsS http://127.0.0.1:8440/login >/dev/null 2>&1 && break; sleep 1; done
[ "$(curl -sk -b "$WORK/cookies" -o /dev/null -w '%{http_code}' "$SITE/journal/health")" = 303 ] \
    && pass "restarting the private login process revokes its in-memory sessions" || fail "a session survived the login process restart"
echo "The hosted login boundary is proven on this machine."
