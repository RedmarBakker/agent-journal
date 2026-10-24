#!/bin/sh
# Sets up a hosted team journal on this machine with Docker: asks for the project and the address, or reads them from
# TEAM_PROJECT and TEAM_ADDRESS without asking, as a GitHub Actions run does; starts the team server in a new volume and
# prints its URL and the one-time setup code that claims it: the first visit to that URL, or the first journal to join it,
# gives the code and makes the admin.
# Run it on the server with the copy each release carries, which pulls that release's team image:
#   curl -fsSL https://github.com/jessegall/agent-journal/releases/latest/download/install.sh | sh
# A second project on the same host needs ports of its own: TEAM_HTTPS_PORT and TEAM_HTTP_PORT, with the server's own
# certificate (give an IP address), since only one container can hold 80 and 443.
# Back up a running server with: docker exec agent-journal-<project> python -m sync_server backup --data /data/team
set -eu

IMAGE="${TEAM_IMAGE:-ghcr.io/jessegall/agent-journal-team:${TEAM_VERSION:-latest}}"
HTTPS_PORT="${TEAM_HTTPS_PORT:-443}"
HTTP_PORT="${TEAM_HTTP_PORT:-80}"

# Prompts come from the terminal even when the script itself arrives on standard input through a pipe; given the project
# and the address it asks nothing.
if [ -z "${TEAM_SETUP_STDIN:-}" ] && [ -z "${TEAM_PROJECT:-}" ] && [ -r /dev/tty ]; then
    exec < /dev/tty
fi

ask() {
    printf '%s: ' "$1" >&2
    IFS= read -r answer
    printf '%s' "$answer"
}

# Docker is installed first when the machine has none, by Docker's own install script, as root or through sudo.
if ! command -v docker >/dev/null; then
    echo "Docker is not installed here: installing it with Docker's own script (get.docker.com)." >&2
    if [ "$(id -u)" = "0" ]; then as_root=""; elif command -v sudo >/dev/null; then as_root="sudo"; else
        echo "Installing Docker needs root: run this as root or with sudo, or install Docker first." >&2
        exit 1
    fi
    curl -fsSL https://get.docker.com | $as_root sh >&2 || { echo "Docker could not be installed: install it by hand, then run this again." >&2; exit 1; }
    command -v docker >/dev/null || { echo "Docker was installed but is not on the path: open a new shell and run this again." >&2; exit 1; }
fi
# Docker's daemon is started, and kept starting at boot, when it is not running yet, as right after its install.
if ! docker info >/dev/null 2>&1; then
    if [ "$(id -u)" = "0" ]; then as_root=""; else as_root="sudo"; fi
    $as_root systemctl enable --now docker >/dev/null 2>&1 || $as_root service docker start >/dev/null 2>&1 || true
    tries=0
    until docker info >/dev/null 2>&1; do
        tries=$((tries + 1))
        [ "$tries" -lt 15 ] || { echo "Docker is installed but its daemon does not start: start it (systemctl start docker), then run this again." >&2; exit 1; }
        sleep 2
    done
fi

project="${TEAM_PROJECT:-}"
[ -n "$project" ] || project=$(ask "Project name, which names the server's volume and container")
address="${TEAM_ADDRESS:-}"
[ -n "$address" ] || address=$(ask "The address the team reaches this server at, a domain name or this machine's IP address")
# the one-time code that claims the server, in the letters the server itself uses, none that read alike
setup_code="${TEAM_SETUP_CODE:-$(LC_ALL=C tr -dc 'ABCDEFGHJKMNPQRSTUVWXYZ23456789' < /dev/urandom | head -c 8 | sed 's/^\(....\)/\1-/')}"

slug=$(printf '%s' "$project" | tr 'A-Z' 'a-z' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$//')
[ -n "$slug" ] || { echo "The project name needs at least one letter or digit." >&2; exit 1; }
name="agent-journal-$slug"
if docker volume inspect "$name" >/dev/null 2>&1; then
    echo "A team server for $project is set up here already, in the volume $name." >&2
    exit 1
fi

case "$address" in
    *[!0-9.]*) certificate="" ;;
    *) certificate="internal" ;;
esac

docker pull -q "$IMAGE" >/dev/null 2>&1 || docker image inspect "$IMAGE" >/dev/null || { echo "The image $IMAGE could not be found." >&2; exit 1; }
docker volume create "$name" >/dev/null
docker run -d --name "$name" --restart unless-stopped -p "$HTTPS_PORT:443" -p "$HTTP_PORT:80" -v "$name:/data" \
    -e TEAM_ADDRESS="$address" -e TEAM_CERTIFICATE="$certificate" -e TEAM_SETUP_CODE="$setup_code" "$IMAGE" >/dev/null

if [ "$HTTPS_PORT" = "443" ]; then url="https://$address"; else url="https://$address:$HTTPS_PORT"; fi
# The team server answers /team to a client that names the journal's protocol once Caddy holds a certificate the client
# accepts; the hosted journal behind the other paths starts only once the team holds a journal.
tries=0
until [ "$(curl -s ${certificate:+-k} --max-time 5 -o /dev/null -w '%{http_code}' -H 'X-Journal-Protocol: 1' "$url/team")" = "200" ]; do
    tries=$((tries + 1))
    if [ "$tries" -ge 30 ]; then
        echo "The server runs, but $url does not answer over HTTPS: the certificate for $address could not be got." >&2
        echo "Check that $address points at this machine and that ports 80 and 443 are open; what Caddy said:" >&2
        docker logs --tail 15 "$name" >&2
        exit 1
    fi
    sleep 2
done

echo
echo "The team server for $project runs at $url."
echo "Its setup code is $setup_code: claim it before anyone else by opening $url and giving the code, or from your journal:"
echo "Settings, Team tab, with $url, the code, your email and a password, or journal team join $url --setup-code $setup_code."
echo "Whoever claims it becomes the team's admin, and the code is no good after that."
echo
echo "Invite colleagues afterwards from the Team tab, or with journal team invite <email>: each gets a URL to join with."
