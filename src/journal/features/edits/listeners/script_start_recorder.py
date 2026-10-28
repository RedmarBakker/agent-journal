from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.features.edits.support.file_modification_tracker import FileModificationTracker
from journal.events.blocking import Blocking


class ScriptStartRecorder(AgentListener[ToolStarting]):
    """Before an interpreter runs a script that writes, the modification time of every project file is stored, so its edits are found from what changed on disk."""

    blocking = Blocking.NEXT_DECISION

    def __init__(self, modified_at: FileModificationTracker) -> None:
        self.modified_at = modified_at

    def handle(self, event: ToolStarting) -> None:
        if event.call.is_script():
            self.modified_at.record(event.tool_use)
