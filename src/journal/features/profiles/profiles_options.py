from journal.support.option import Option


class ProfilesOptions:
    """The options of the profiles feature."""

    CLAUDE_MODEL = Option("profiles.model.claude", "Model on Claude", "The model the journal's subagent profiles run on under Claude Code", "sonnet", option_type="model", provider="claude")
    CODEX_MODEL = Option("profiles.model.codex", "Model on Codex", "The model the journal's subagent profiles run on under Codex", "gpt-6.1-sol", option_type="model", provider="codex")
