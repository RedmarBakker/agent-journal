# The team server of a library: the stdlib-only sync_server behind Caddy, which gets and renews the HTTPS certificate
# for TEAM_ADDRESS, serves its own certificate with TEAM_CERTIFICATE=internal for a bare address, whose authority it
# serves at /root.crt, or serves plain HTTP on port 80 when TEAM_PLAIN_HTTP=1 on a private network. It holds the team's
# accounts and the library's items; everything it keeps, the team's database, the items' files and Caddy's
# certificates, lives in the /data volume.
# Built from the repository root: docker build -f docker/team-server/Dockerfile -t agent-journal-team .
FROM caddy:2.8.4 AS caddy

FROM python:3.14.7-slim
COPY --from=caddy /usr/bin/caddy /usr/bin/caddy
COPY src/sync_server /app/src/sync_server
COPY docker/team-server/Caddyfile.https docker/team-server/Caddyfile.plain docker/team-server/Caddyfile.internal docker/team-server/routes.caddy /etc/caddy/
COPY docker/team-server/run.sh /app/
ENV PYTHONPATH=/app/src PYTHONDONTWRITEBYTECODE=1 XDG_DATA_HOME=/data XDG_CONFIG_HOME=/data/config
VOLUME /data
EXPOSE 80 443
CMD ["bash", "/app/run.sh"]
