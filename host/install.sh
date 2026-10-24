#!/bin/sh
# Sets up a hosted team journal on this machine with Docker: asks for the project and the address, or reads them from
# TEAM_PROJECT and TEAM_ADDRESS without asking, as a GitHub Actions run does; starts the team server in a new volume and
# prints its URL: the first journal to claim it there becomes its admin.
# Run it on the server with the copy each release carries, which pulls that release's team image:
#   curl -fsSL https://github.com/jessegall/agent-journal/releases/latest/download/install.sh | sh
# It listens on 8443 and 8080 unless TEAM_HTTPS_PORT and TEAM_HTTP_PORT say otherwise; a second project on the same host needs ports of its own, with the server's own
# certificate (give an IP address), since only one container can hold 80 and 443.
# Back up a running server with: docker exec agent-journal-<project> python -m sync_server backup --data /data/team
set -eu

# The whole script is one function, read to its end before any line of it runs, so a script that arrives through a pipe
# is never cut short by a prompt that reads from the terminal.
main() {

    # the release's team image, tagged as the release is (v4.55.3); a version given without its v is read the same
version="${TEAM_VERSION:-latest}"
case "$version" in latest|v*) ;; *) version="v$version" ;; esac
IMAGE="${TEAM_IMAGE:-ghcr.io/jessegall/agent-journal-team:$version}"
    # ports of its own by default, so a web server already on 80 and 443 keeps them; 443 is asked for by name
    HTTPS_PORT="${TEAM_HTTPS_PORT:-8443}"
    HTTP_PORT="${TEAM_HTTP_PORT:-8080}"

    # Prompts are read from the terminal, never by switching the script's own input, which may still be arriving through
    # the pipe it was run from; with no terminal, or TEAM_SETUP_STDIN set, they are read from standard input. Given the
    # project and the address it asks nothing.
    ask() {
        printf '%s: ' "$1" >&2
        if [ -z "${TEAM_SETUP_STDIN:-}" ] && [ -r /dev/tty ]; then IFS= read -r answer < /dev/tty; else IFS= read -r answer; fi
        printf '%s' "$answer"
    }

    step() {
        echo "$1" >&2
    }

    # whether something on this machine already listens on the port, as ss reports it; with no ss the port is taken as free
    port_taken() {
        command -v ss >/dev/null 2>&1 || return 1
        ss -ltnH 2>/dev/null | awk '{print $4}' | grep -Eq "[:.]$1\$"
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
    # A rescue system, booted from memory to repair a machine, has no kernel support for Docker's network: say so before waiting on a daemon that cannot start.
    if [ "$(hostname 2>/dev/null)" = "rescue" ] || [ -d /root/.oldroot ]; then
        echo "This machine runs a rescue system, which cannot run Docker: install an operating system and boot into it (installimage on a Hetzner machine), then run this again." >&2
        exit 1
    fi
    # Docker's daemon is started, and kept starting at boot, when it is not running yet, as right after its install.
    if ! docker info >/dev/null 2>&1; then
        if [ "$(id -u)" = "0" ]; then as_root=""; else as_root="sudo"; fi
        step "Starting Docker's daemon."
        $as_root systemctl enable --now docker >/dev/null 2>&1 || $as_root service docker start >/dev/null 2>&1 || true
        tries=0
        until docker info >/dev/null 2>&1; do
            tries=$((tries + 1))
            if [ "$tries" -ge 15 ]; then
                echo "Docker is installed but its daemon does not start. Its last lines:" >&2
                if command -v journalctl >/dev/null 2>&1; then journalctl -u docker -n 5 --no-pager 2>/dev/null | sed 's/^/  /' >&2; fi
                echo "Fix what they name, start it (systemctl start docker), then run this again." >&2
                exit 1
            fi
            sleep 2
        done
    fi

    project="${TEAM_PROJECT:-}"
    [ -n "$project" ] || project=$(ask "Project name, which names the server's volume and container")
    address="${TEAM_ADDRESS:-}"
    [ -n "$address" ] || address=$(ask "The address the team reaches this server at, a domain name or this machine's IP address")

    slug=$(printf '%s' "$project" | tr 'A-Z' 'a-z' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$//')
    [ -n "$slug" ] || { echo "The project name needs at least one letter or digit." >&2; exit 1; }
    name="agent-journal-$slug"
    if docker volume inspect "$name" >/dev/null 2>&1; then
        echo "A team server for $project is set up here already, in the volume $name." >&2
        exit 1
    fi

    # a public certificate is got only for a domain on port 443; on any other port, or for an IP, the server makes its own
    case "$address:$HTTPS_PORT" in
        *[!0-9.]*:443) certificate="" ;;
        *) certificate="internal" ;;
    esac

    for port in "$HTTPS_PORT" "$HTTP_PORT"; do
        if port_taken "$port"; then
            echo "Port $port is taken on this machine by another service. Choose free ports for the team server: from your journal," >&2
            echo "journal remote install <target> --https-port 8444 --http-port 8081, or set TEAM_HTTPS_PORT and TEAM_HTTP_PORT when you run this yourself." >&2
            exit 1
        fi
    done
    step "Pulling the team server's image, $IMAGE: a few hundred megabytes, which can take a minute."
    docker pull -q "$IMAGE" >/dev/null 2>&1 || docker image inspect "$IMAGE" >/dev/null || { echo "The image $IMAGE could not be found." >&2; exit 1; }
    step "Starting the team server in the container $name."
    docker volume create "$name" >/dev/null
    docker run -d --name "$name" --restart unless-stopped -p "$HTTPS_PORT:443" -p "$HTTP_PORT:80" -v "$name:/data" \
        -e TEAM_ADDRESS="$address" -e TEAM_CERTIFICATE="$certificate" "$IMAGE" >/dev/null

    if [ "$HTTPS_PORT" = "443" ]; then url="https://$address"; else url="https://$address:$HTTPS_PORT"; fi
    # The team server answers /team to a client that names the journal's protocol once Caddy holds a certificate the client
    # accepts; the hosted journal behind the other paths starts only once the team holds a journal.
    if [ -n "$certificate" ]; then
        step "Waiting for $url to answer over HTTPS with the server's own certificate, which an IP address gets: up to a minute."
    else
        step "Waiting for $url to answer over HTTPS, while the server gets a certificate for $address: up to a minute."
    fi
    tries=0
    # any answer of the team server counts, an older protocol's "upgrade first" (426) as much as a welcome (200)
    until case "$(curl -s ${certificate:+-k} --max-time 5 -o /dev/null -w '%{http_code}' -H 'X-Journal-Protocol: 1' "$url/team")" in 200|426) true ;; *) false ;; esac; do
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
    echo "Claim it now from your journal, before anyone else reaches it: Settings, Team tab, Claim a server, with $url;"
    echo "or journal team join $url. Whoever claims it first becomes the team's admin."
    echo
    echo "Invite colleagues afterwards from the Team tab, or with journal team invite <email>: each gets a URL to join with."
}

main "$@"
