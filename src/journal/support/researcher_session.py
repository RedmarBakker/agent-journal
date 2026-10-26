SEPARATOR = ":"


class ResearcherSession:
    """The session a subagent's own row has: its main agent's session and its agent id, joined by a colon."""

    @staticmethod
    def joined(session: str, subagent: str) -> str:
        return f"{session}{SEPARATOR}{subagent}"

    @staticmethod
    def parts(session: str) -> tuple[str, str]:
        main, _, subagent = session.rpartition(SEPARATOR)
        return (main, subagent) if main else (session, "")
