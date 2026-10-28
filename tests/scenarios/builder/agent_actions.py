import re


class AgentActions:
    """What the agent does in several steps, each written once here so a story calls it by name and a change to how it is done changes one place: a task filed or taken in hand, its number handed back, a message read and answered."""

    def agent_creates_task(self, title: str, brief: str = "") -> int:
        self.agent_runs(f"task create '{title}'" + (f" --brief '{brief}'" if brief else ""))
        return self.task_number()

    def agent_takes_a_task(self, title: str) -> int:
        self.agent_runs(f"task create '{title}' --start")
        return self.task_number()

    def agent_writes_a_document(self, title: str, text: str) -> int:
        source = self.app.config.root / f"{title}.md"
        source.write_text(text)
        self.agent_runs(f"doc create '{title}' --file '{source}' --abstract '{title}'")
        return int(re.search(r"doc (\d+)", self.command.text)[1])

    def agent_answers(self, message: int, text: str) -> None:
        self.agent_runs(f"message read {message}")
        self.agent_replies(message, text)

    def task_number(self) -> int:
        return int(re.search(r"task (\d+)", self.command.text)[1])
