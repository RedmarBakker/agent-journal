from journal.models.agent_role import AgentRole
from journal.features.edits.listeners.record_edit import RecordEdit
from journal.features.edits.listeners.script_start_recorder import ScriptStartRecorder
from journal.features.feature import Feature


class EditsFeature(Feature):
    """The files the agent changes, stored as rows: the file edits pane reads them, and shows the same after a reload."""

    name = "edits"
    helper_listeners = {AgentRole.WORKER: (RecordEdit,)}
    title = "File edits"
    help = "Every file the agent changes, by a tool or a shell command, is kept as an edit with its changed lines; the last five hundred stay."
    listeners = (ScriptStartRecorder, RecordEdit)
