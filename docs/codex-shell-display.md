# Codex shows the shell runner

Checked on 28 October 2026 with Codex CLI 0.165.0.

Codex currently shows the rewritten shell command, including `hooks/run.sh --command`, in
its terminal. There is no documented, supported way to keep that runner transparent while
displaying a separate original command.

## Evidence

- The [official Hooks documentation](https://learn.chatgpt.com/docs/hooks#pretooluse)
  specifies `permissionDecision: "allow"` with `updatedInput.command` to rewrite a Bash
  command. It exposes no original-command or display-command field. `additionalContext`
  adds context; it does not change the terminal label. `suppressOutput` is unsupported.
- The [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
  documents shell environment policies and login-shell controls, but no shell runner prefix
  or independent shell-command display setting.
- The installed binary reports `codex-cli 0.165.0`. Its experimental app-server schema,
  generated with `codex app-server generate-json-schema --experimental --out <folder>`,
  defines `CommandExecutionThreadItem` with one `command` field and parsed
  `commandActions`. It has no separate original-command or display-command field.

The absence of a supported interface is the conclusion of these checks, not a claim that
future Codex releases cannot add one.

## Current integration

`src/journal/providers/codex.py` rewrites permitted Bash calls to
`sh <package>/journal/hooks/run.sh --command <original command>`. That runner preserves
automatic backgrounding, output capture and the existing command guards. The same provider
unwraps this shape when interpreting a command, so journal run cards retain the original
command.

Claude Code's shell-prefix integration is provider-specific. Codex's launcher deliberately
supplies no corresponding environment override. Adding an undocumented display argument,
moving execution into a shell startup file, or dropping the runner would not provide an
equivalent supported integration.

Keep the runner until Codex offers a documented execution-prefix or display API. Recheck
both the release documentation and installed protocol when that support is announced.
