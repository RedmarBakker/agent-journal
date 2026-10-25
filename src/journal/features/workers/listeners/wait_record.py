from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.wait_reading import WaitReading
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor

# the journal commands after which the waits of the started plans may have changed
WAIT_NOUNS = ("task", "plan", "worker")


class WaitRecord(AgentListener[ToolFinished]):
    """After a task, plan or worker command of the orchestrator, how the started plans' tasks wait is measured and kept on its row, which its fitness scores; a task newly found naming another open task it does not wait on is told."""

    def __init__(self, agents: Agents, reading: WaitReading, settings: SettingRows) -> None:
        self.agents, self.reading, self.settings = agents, reading, settings

    def handle(self, event: ToolFinished) -> None:
        if event.subagent or self.settings.option(WorkersOptions.MODE) != "orchestrator" or not any(part.journal_noun in WAIT_NOUNS for part in event.call.parts):
            return
        rows = self.agents.session_rows(event.session)
        if rows and rows[0].role == AgentRole.MAIN:
            self.agents.save(rows[0].waits_measured(self.reading.measured(), event.time), Actor.system())
