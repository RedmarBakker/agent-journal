from journal.support.option import Option


class ProfilesOptions:
    """The options of the profiles feature."""

    CLAUDE_MODEL = Option("profiles.model.claude", "Model on Claude", "The model the journal's subagent profiles run on under Claude Code", "sonnet", kind="model", provider="claude")
    CODEX_MODEL = Option("profiles.model.codex", "Model on Codex", "The model the journal's subagent profiles run on under Codex", "gpt-6.1-sol", kind="model", provider="codex")
