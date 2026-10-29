#!/bin/sh
set -eu

OPENAI_API_KEY=$(cat /run/secrets/supervisor_openai_api_key)
OPENCLAW_HOOK_TOKEN=$(cat /run/secrets/openclaw_hook_token)
JOURNAL_SUPERVISOR_CREDENTIAL=$(cat /run/secrets/journal_supervisor_credential)
export OPENAI_API_KEY OPENCLAW_HOOK_TOKEN JOURNAL_SUPERVISOR_CREDENTIAL

exec node dist/index.js gateway run --port "${OPENCLAW_GATEWAY_PORT:-18789}"
