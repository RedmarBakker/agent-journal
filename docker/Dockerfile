FROM python:3.14.10-slim-bookworm@sha256:9974e24551f9e7ca172cf284d85b8ab3e031d22d945f7026ede7a8279118c9f1

RUN apt-get update \
    && apt-get install -y --no-install-recommends acl ca-certificates curl findutils git nodejs npm procps \
    && npm install -g @anthropic-ai/claude-code@2.1.293 \
    && npm install -g @openai/codex@0.165.0 \
    && npm cache clean --force \
    && rm -rf /var/lib/apt/lists/*

# The journal server and the pinned Plan driver use separate identities.
RUN groupadd --gid 10001 journal \
    && groupadd --gid 10003 codex-driver \
    && useradd --uid 10001 --gid journal --home-dir /data/home --no-create-home --shell /bin/sh journal \
    && useradd --uid 10002 --gid journal --home-dir /data/gateway --no-create-home --shell /usr/sbin/nologin gateway \
    && useradd --uid 10003 --gid codex-driver --home-dir /var/lib/journal-codex --no-create-home --shell /usr/sbin/nologin codex-driver \
    && mkdir -p /data/home /data/project /data/secrets /data/gateway /data/vault /var/lib/journal-codex \
    && chown journal:journal /data/home /data/project /data/secrets \
    && chown gateway:journal /data/gateway /data/vault \
    && chown codex-driver:codex-driver /var/lib/journal-codex \
    && chmod 700 /data/home /data/secrets /data/gateway /data/vault /var/lib/journal-codex \
    && chmod 2770 /data/project

COPY --chown=root:root src /opt/agent-journal/src
COPY --chown=root:root install.sh update_steps.json /opt/agent-journal/
COPY --chown=root:root --chmod=755 docker/entrypoint.sh docker/hosted-journal /usr/local/bin/
COPY --chown=root:root --chmod=755 docker/supervisor-codex-login docker/supervisor-codex-ready /usr/local/bin/
COPY --chown=root:root --chmod=755 docker/supervisor-codex-plan-launcher.py /usr/local/bin/supervisor-codex-plan-launcher
COPY --chown=root:root --chmod=755 docs/supervisor/v1/live-smoke-setup.py /usr/local/bin/supervisor-live-setup

ENV JOURNAL_PROJECT=/data/project \
    JOURNAL_ROOT=/data/project \
    JOURNAL_PORT=8421 \
    AGENT_JOURNAL_VAULT=/data/vault \
    AGENT_JOURNAL_SECRETS=/data/secrets \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /
VOLUME /data
EXPOSE 8421

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8421/journal/health || exit 1

ENTRYPOINT ["entrypoint.sh"]
