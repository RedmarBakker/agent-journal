from journal.features.workers.support.fitness_measure import FitnessMeasure
from journal.features.workers.support.interruption_measure import InterruptionMeasure
from journal.features.workers.support.load_level_measure import LoadLevelMeasure
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.support.mode_profile import ModeProfile
from journal.models.support.model_fit import RIGHT

SOLO_RESEARCH_SHARE = FitnessMeasure("your own reads and searches among them and your subagents", lambda counts: (counts.research_count, counts.research_count + counts.subagent_dispatches), 0.8, 1.0, 2, "read and research this yourself; a subagent is for the rare job too wide to do in your own turns")
SOLO_FILE_EDIT_SHARE = FitnessMeasure("your own file edits among your edits and handovers", lambda counts: (counts.file_edits, counts.file_edits + counts.handovers), 1.0, 1.0, 2, "do the work yourself: solo hands nothing out")
BRIEF_SHARE = FitnessMeasure("your handovers whose brief names a done-when and the files to change among your handovers", lambda counts: (counts.briefed, counts.handovers), 0.8, 1.0, 2, "end each brief with what it is done when and the files it changes")
ORCHESTRATOR_WORKLOAD = LoadLevelMeasure("your load", 5, "clear what waits and hand the work out to workers until your load is back under half of what you can clear", 0.5, 1.0)
OLDEST_FIRST_SHARE = FitnessMeasure("your clearings that took the oldest waiting item first among your clearings", lambda counts: (counts.load.oldest_first, counts.load.clearings_counted), 0.8, 1.0, 2, "clear the worker or message that has waited longest first")
MODEL_FIT_SHARE = FitnessMeasure("your merged jobs whose model fit the work among your newest merged jobs", lambda counts: (sum(1 for entry in counts.model_fits if entry.split(":", 1)[1] == RIGHT), len(counts.model_fits)), 0.7, 1.0, 2, "send small work on the fast model and keep the strongest for large work; work sent back again and again needs a stronger one")

WAIT_SHARE = FitnessMeasure("your started plans' blocked tasks that wait with --on or --until among them, the tasks that name another they do not wait on and the plans with no waits", lambda counts: counts.waits.scored(), 0.8, 1.0, 2, "block a task on what it waits for, --on task:<n> or --until '<command>', so it opens by itself", least=1)
INTERRUPTIONS = InterruptionMeasure("the reports an hour your workers filed while plenty of work was open", 3, "queue each worker several tasks with journal worker queue <n> <task>... --report queue, so it reports once for all of them")


class WorkersProfiles:
    """The ideal agent of the orchestrator and the solo modes, scored on tool uses until the measures of plan 1034 replace them (the builder is judged by those already): the orchestrator hands most of the work out and still makes small fixes, the solo agent does all of it itself; the orchestrator is also scored on its handling of its load, the minutes it stays over the add-a-place level, clearing the oldest first and not dispatching while the queue grows, on whether the models of its merged jobs fit them, and on how its plans' tasks wait; a share of events counts only once it has three of them, save the waits, which are the plans as they stand and count from one task."""

    ORCHESTRATOR = ModeProfile("orchestrator", (ORCHESTRATOR_WORKLOAD, INTERRUPTIONS, BRIEF_SHARE, OLDEST_FIRST_SHARE, MODEL_FIT_SHARE, WAIT_SHARE))
    SOLO_PROFILE = ModeProfile("solo", (SOLO_FILE_EDIT_SHARE, SOLO_RESEARCH_SHARE))

    ALL = (ORCHESTRATOR, SOLO_PROFILE)

    @classmethod
    def mode_profile(cls, mode: str) -> ModeProfile | None:
        return next((profile for profile in cls.ALL if profile.mode == mode), None)
