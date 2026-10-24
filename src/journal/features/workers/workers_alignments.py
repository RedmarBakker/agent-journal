from journal.features.workers.support.alignment import Alignment
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions


class WorkersAlignments:
    """The work modes' alignment rules: the builder that keeps handing work out or hands out far more than it writes, the orchestrator that keeps writing code itself or writes far more than it hands out, and the solo agent that sends subagents instead of researching."""

    BUILDER = Alignment("builder", lambda workers: workers.tool_uses.consecutive_handovers, WorkersOptions.BUILDER_HANDOVER_LIMIT, WorkersNudges.BUILDER_ALIGNMENT)
    BUILDER_SHARE = Alignment("builder", lambda workers: workers.tool_uses.handovers - workers.tool_uses.file_edits, WorkersOptions.BUILDER_HANDOVER_SURPLUS, WorkersNudges.BUILDER_SHARE)
    ORCHESTRATOR = Alignment("orchestrator", lambda workers: workers.code_lines, WorkersOptions.ORCHESTRATOR_LINE_LIMIT, WorkersNudges.ORCHESTRATOR_ALIGNMENT)
    ORCHESTRATOR_SHARE = Alignment("orchestrator", lambda workers: workers.tool_uses.file_edits - workers.tool_uses.handovers, WorkersOptions.ORCHESTRATOR_EDIT_SURPLUS, WorkersNudges.ORCHESTRATOR_SHARE)
    SOLO = Alignment("solo", lambda workers: workers.tool_uses.subagent_dispatches - workers.tool_uses.research_count, WorkersOptions.SOLO_DISPATCH_LIMIT, WorkersNudges.SOLO_ALIGNMENT)

    ALL = (BUILDER, BUILDER_SHARE, ORCHESTRATOR, ORCHESTRATOR_SHARE, SOLO)
