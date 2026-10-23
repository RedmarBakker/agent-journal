INJECTED_STARTS = ("[journal]", "[plugin ", "<", "[Cross-session ", "# AGENTS.md instructions")


class PromptOrigin:
    """Whether a prompt an agent program received was typed by its user, or is a line the journal or a plugin typed, a notice, or a block of instructions or context the program put in itself."""

    @staticmethod
    def is_users(prompt: str) -> bool:
        return not prompt.lstrip().startswith(INJECTED_STARTS)
