from journal.features.workers.support.alignment import Alignment
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions


class WorkersAlignments:
    """The work modes' alignment rules: the orchestrator that keeps writing code itself, and the solo agent that sends subagents instead of researching."""

    ORCHESTRATOR = Alignment("orchestrator", lambda workers: workers.code_lines, WorkersOptions.ORCHESTRATOR_LINE_LIMIT, WorkersNudges.ORCHESTRATOR_ALIGNMENT)
    SOLO = Alignment("solo", lambda workers: workers.tool_uses.subagent_dispatches - workers.tool_uses.research_count, WorkersOptions.SOLO_DISPATCH_LIMIT, WorkersNudges.SOLO_ALIGNMENT)

    ALL = (ORCHESTRATOR, SOLO)
