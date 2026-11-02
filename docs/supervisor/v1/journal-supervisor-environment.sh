#!/bin/sh
set -eu

ANTHROPIC_API_KEY=$(cat /run/secrets/supervisor_anthropic_api_key)
OPENCLAW_HOOK_TOKEN=$(cat /run/secrets/openclaw_hook_token)
JOURNAL_SUPERVISOR_ADMISSION_TOKEN=$(cat /run/secrets/journal_supervisor_credential)
OPENCLAW_GATEWAY_TOKEN=$(node -e 'process.stdout.write(require("node:crypto").randomBytes(32).toString("hex"))')
: "${JOURNAL_SUPERVISOR_ADMISSION_URL:?private journal admission URL is not configured}"
: "${JOURNAL_SUPERVISOR_TLS_CA_FILE:?private journal TLS CA file is not configured}"
JOURNAL_SUPERVISOR_STATE_DIR=/home/node/.openclaw/journal-supervisor-transport
OPENCLAW_CONFIG_PATH=/home/node/.openclaw/openclaw.json
export ANTHROPIC_API_KEY OPENCLAW_HOOK_TOKEN OPENCLAW_GATEWAY_TOKEN JOURNAL_SUPERVISOR_ADMISSION_URL JOURNAL_SUPERVISOR_ADMISSION_TOKEN JOURNAL_SUPERVISOR_TLS_CA_FILE JOURNAL_SUPERVISOR_STATE_DIR OPENCLAW_CONFIG_PATH
