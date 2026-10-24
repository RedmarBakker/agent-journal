from journal.features.workers.support.fitness_measure import FitnessMeasure
from journal.features.workers.support.mode_profile import ModeProfile

FILE_EDIT_SHARE = FitnessMeasure("your own file edits among your edits and handovers", lambda counts: (counts.file_edits, counts.file_edits + counts.handovers), 0.6, 1.0, 3, "take the next task yourself and hand one out only when it is better done beside you")
RESEARCH_SHARE = FitnessMeasure("your own reads and searches among them and your subagents", lambda counts: (counts.research_count, counts.research_count + counts.subagent_dispatches), 0.5, 1.0, 1, "read and search yourself; a subagent is for a job too wide for your own turns")
HANDOVER_SHARE = FitnessMeasure("your handovers among your edits and handovers", lambda counts: (counts.handovers, counts.file_edits + counts.handovers), 0.4, 1.0, 3, "hand the work to a worker and review what comes back")
SOLO_RESEARCH_SHARE = FitnessMeasure("your own reads and searches among them and your subagents", lambda counts: (counts.research_count, counts.research_count + counts.subagent_dispatches), 0.8, 1.0, 2, "read and research this yourself; a subagent is for the rare job too wide to do in your own turns")
SOLO_FILE_EDIT_SHARE = FitnessMeasure("your own file edits among your edits and handovers", lambda counts: (counts.file_edits, counts.file_edits + counts.handovers), 1.0, 1.0, 2, "do the work yourself: solo hands nothing out")


class WorkersProfiles:
    """The ideal agent of each work mode: the builder writes most of its work and researches itself, the orchestrator hands most of the work out and still makes small fixes, the solo agent does all of it itself."""

    BUILDER = ModeProfile("builder", (FILE_EDIT_SHARE, RESEARCH_SHARE))
    ORCHESTRATOR = ModeProfile("orchestrator", (HANDOVER_SHARE,))
    SOLO = ModeProfile("solo", (SOLO_FILE_EDIT_SHARE, SOLO_RESEARCH_SHARE))

    ALL = (BUILDER, ORCHESTRATOR, SOLO)

    @classmethod
    def mode_profile(cls, mode: str) -> ModeProfile | None:
        return next((profile for profile in cls.ALL if profile.mode == mode), None)
