# The journal on a server

One journal, its owner only, at a domain of its own. You log in there with one password, use the full
viewer, pair your phone, and start agents that run on the server and push their branches to GitHub.

## What the server needs

- Linux with Docker Engine and the compose plugin; 2 CPUs, 4 GB of memory and 20 GB of disk are enough for one agent.
- Ports 80 and 443 open, and a DNS record for the journal's domain pointing at the server.
- A GitHub repository for the project, and a fine-grained token that may push to it.
- A provider login for the agents: a token from `claude setup-token` on your own machine, or an API key.

## Install

```sh
git clone https://github.com/jessegall/agent-journal && cd agent-journal/docker
cp .env.example .env && chmod 600 .env    # fill in the domain, hosted password, repository, tokens and backup password
docker compose up -d                       # backups and the updater; the public front door stays off
docker compose logs -f updater             # until it says it deployed the journal
docker compose --profile journal up -d caddy # publishes only after the updater has started the login proxy
```

The journal is started only by the updater, on the exact digest it verified, so a later `docker compose up` never
rolls it back to an unchecked image. Set `JOURNAL_HOSTED_PASSWORD` in `.env` before running Compose; the public
front door refuses to start if it is empty. To make a password without shell punctuation, use
`printf 'JOURNAL_HOSTED_PASSWORD=%s\n' "$(openssl rand -hex 32)" >> .env` and keep `.env` mode 0600.

Open `https://<your domain>` and enter the hosted password from `.env`.

## What runs

- `journal`: the version 4 journal and its agents as uid 10001. It listens on port 8421 inside the private Docker
  network; that port is not published on the host. Docker health checks use `/journal/health` directly.
- `hosted-login`: a separate container running as uid 10002 with no project or journal-data mount. It fronts the
  journal on port 8440, hashes the password in memory and keeps expiring sessions in its own memory. It receives
  `JOURNAL_HOSTED_PASSWORD`; the journal process does not. Restarting it ends every hosted session. Its cookie is
  HttpOnly, Secure and SameSite=Lax, and the proxy removes it before forwarding requests to the journal.
- `caddy`: the only service publishing host ports 80 and 443. It sends HTTPS requests to `hosted-login`, adds
  HSTS, and redirects plain HTTP to HTTPS. Caddy proxies only to `hosted-login`; it never points at port 8421.
- `backup`: a restic snapshot of the journal's volume every day, kept 7 days and 4 weeks. It holds the
  project checkout, the journal record and the server's home;
  it leaves out the journal's runtime folder and the secrets' values in /data/secrets. Set `RESTIC_REPOSITORY`
  to keep it off the server.
- `updater`: once an hour, checks with cosign that `ghcr.io/jessegall/agent-journal:latest` was signed by this
  repository's release workflow, and only then restarts the journal on exactly that digest; the journal upgrades its
  record on start. An image without that signature is never deployed. To check one by hand:
  `cosign verify --certificate-identity-regexp '^https://github.com/jessegall/agent-journal/' --certificate-oidc-issuer https://token.actions.githubusercontent.com ghcr.io/jessegall/agent-journal:latest`.
- `watchtower`: watches only containers that ask for it, and none does while Caddy, restic and watchtower are pinned by digest; to take a newer Caddy, put its digest in `compose.yaml` (`docker buildx imagetools inspect caddy:<version>`).

Version 4 has no built-in hosted login page or `/ready` endpoint. The public Caddy deployment uses `hosted-login`
because it publishes the full journal viewer. The supervisor staging profile does not use that login service: its
writer is reached through private networks and the owner-only loopback tunnel, while Gateway calls use a scoped
supervisor credential.

## What the two users protect, and what they do not

The hosted login runs as uid 10002 in a container with no shared process or data volume with the journal. The
journal and every agent run as uid 10001. An agent, or anyone who takes one over, cannot:

- read the password or session table, which exist only in the login process;
- change the login code, which is root-owned in the image, or take its port from the separate container;
- get the server to run, upgrade, stop or update the journal from outside.

An agent can still do everything its journal identity permits, including changing the project and the journal
runtime. The hosted login protects visitors reaching the public Caddy address; it does not restrict an agent that
already runs inside the journal container.

## Secrets on the server

The server keeps its own secrets file in /data/secrets, one per project, readable by `journal` alone. You fill in
the values in the viewer behind your login, as on your own machine. No backup and no copy of the project or the
record holds them, and a restore leaves them where they are; a new server starts with none. A local agent working
on this journal uses the secrets file of its own machine, never the server's. The agents on the server get a value
only through `journal secret run`, and the file is refused to their tools; since they run as `journal` too, that
refusal stops a mistake, not an agent taken over on purpose.

## Logs, health and alerts

- Logs: `docker compose logs journal` is the journal's output; `docker compose logs hosted-login caddy` has front-door and request logs. Passwords and sessions are not written to disk.
- Health: Docker checks `http://127.0.0.1:8421/journal/health` inside the journal container. The public address remains behind the hosted login.
- Alerts: when free space on the volume drops to 128 MB, the journal puts a message in the viewer, once, and again after the space has come back and gone again. The tunnel's watchdog keeps the same kind of alert for its own address.

## Limits

- Memory: the journal container stops at 4 GB (`JOURNAL_MEMORY` in `.env`), Caddy at 256 MB, the backup at 512 MB.
- Logs: Docker keeps five files of 10 MB per container, and the journal cuts each of its own logs to its last megabyte every hour.
- Disk: once the volume has less than 64 MB free, the journal refuses every write with the answer "the server's disk is nearly full", so no file is left half written. Free some space and writes work again at once.

## Day to day

- `docker compose --profile journal logs hosted-login` — the login proxy's log; it never logs submitted passwords.
- Change `JOURNAL_HOSTED_PASSWORD` in `.env`, then run `docker compose --profile journal up -d --no-deps hosted-login` — this replaces the login process and ends its in-memory sessions.
- Upgrading and taking down are done by the owner in the viewer. The updater checks the signed image every hour and says in the viewer when a newer one is out; it deploys that digest only when the owner presses Upgrade. Taking down logs out every browser and phone at once, then stops the journal and makes a final backup, kept past the usual pruning (`docker compose run --rm --entrypoint restic backup snapshots --tag final`). The data stays in the volume. `./restore.sh` of that backup, or removing the folder with `docker compose exec updater rm -rf /data/updater`, lets the updater start the journal again.
- `./restore.sh [snapshot]` — put a backup back, unpacked beside the journal first so a bad snapshot changes nothing; `docker compose run --rm --entrypoint restic backup snapshots` lists them.
- `./prove.sh` — build the image and prove the health and hosted login boundary on this machine's Docker, then remove what it made.
