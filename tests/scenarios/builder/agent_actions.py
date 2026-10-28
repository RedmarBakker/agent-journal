class AgentActions:
    """What the agent does in several steps, each written once here so a story calls it by name and a change to how it is done changes one place: a task taken in hand, a message read and answered."""

    def agent_takes_a_task(self, title: str) -> None:
        self.agent_runs(f"task create '{title}' --start")

    def agent_answers(self, message: int, text: str) -> None:
        self.agent_runs(f"message read {message}")
        self.agent_replies(message, text)
