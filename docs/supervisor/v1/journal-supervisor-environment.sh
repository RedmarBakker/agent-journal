#!/bin/sh
set -eu

. /opt/journal-supervisor/bin/journal-supervisor-bridge-environment

ANTHROPIC_API_KEY=$(cat /run/secrets/supervisor_anthropic_api_key)
OPENCLAW_HOOK_TOKEN=$(cat /run/secrets/openclaw_hook_token)
OPENCLAW_GATEWAY_TOKEN=$(node -e 'process.stdout.write(require("node:crypto").randomBytes(32).toString("hex"))')
OPENCLAW_CONFIG_PATH=/home/node/.openclaw/openclaw.json
export ANTHROPIC_API_KEY OPENCLAW_HOOK_TOKEN OPENCLAW_GATEWAY_TOKEN OPENCLAW_CONFIG_PATH
