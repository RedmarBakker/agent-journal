from journal.features.workers.support.fitness_measure import FitnessMeasure
from journal.features.workers.support.interruption_measure import InterruptionMeasure
from journal.features.workers.support.load_level_measure import LoadLevelMeasure
from journal.features.workers.support.load_measure import LoadMeasure
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.support.mode_profile import ModeProfile
from journal.features.workers.support.queue_measure import QueueMeasure
from journal.models.support.model_fit import RIGHT

HANDOVER_SHARE = FitnessMeasure("your handovers among your edits and handovers", lambda counts: (counts.handovers, counts.file_edits + counts.handovers), 0.4, 1.0, 3, "hand the work to a worker and review what comes back")
SOLO_RESEARCH_SHARE = FitnessMeasure("your own reads and searches among them and your subagents", lambda counts: (counts.research_count, counts.research_count + counts.subagent_dispatches), 0.8, 1.0, 2, "read and research this yourself; a subagent is for the rare job too wide to do in your own turns")
SOLO_FILE_EDIT_SHARE = FitnessMeasure("your own file edits among your edits and handovers", lambda counts: (counts.file_edits, counts.file_edits + counts.handovers), 1.0, 1.0, 2, "do the work yourself: solo hands nothing out")
WORKER_WAIT_SHARE = FitnessMeasure("your tool uses made while a clocked-out worker waited over 5 minutes for its check, merge or send back among your tool uses", lambda counts: (counts.late_workers, counts.window_uses), 0.0, 0.1, 3, "answer a worker that clocked out within a few minutes: check it, merge it or send it back")
TASK_WAIT_SHARE = FitnessMeasure("your tool uses made while an open task waited over 5 minutes for a worker with a place free among your tool uses", lambda counts: (counts.late_tasks, counts.window_uses), 0.0, 0.1, 2, "hand each open task to a worker while a place is free")
REUSE_SHARE = FitnessMeasure("your sends to idle workers among your sends and your fresh dispatches made while one sat idle", lambda counts: (counts.reuses, counts.reuses + counts.fresh_idle), 0.7, 1.0, 2, "send the next job to an idle worker with journal worker send before dispatching a fresh one")
BRIEF_SHARE = FitnessMeasure("your handovers whose brief names a done-when and the files to change among your handovers", lambda counts: (counts.briefed, counts.handovers), 0.8, 1.0, 2, "end each brief with what it is done when and the files it changes")
PREPARED_MERGE_SHARE = FitnessMeasure("your merges that followed a read of the proofs and a test run among your merges", lambda counts: (counts.prepared_merges, counts.merges), 0.9, 1.0, 3, "read the proofs with journal task show and run the tests before journal worker merge")
ORCHESTRATOR_EDIT_SHARE = FitnessMeasure("your own file edits among your tool uses", lambda counts: (counts.file_edits, counts.window_uses), 0.0, 0.2, 2, "hand the work to a worker and keep to reviewing it")
ORCHESTRATOR_WORKLOAD = LoadLevelMeasure("your load", 5, "clear what waits and hand the work out to workers until your load is back under half of what you can clear", 0.5, 1.0)
BUSY_MINUTES = LoadMeasure("the minutes your load stayed over the add-a-place level", 3, "clear what waits, oldest first, and ease the load before it holds over the level: turn the reviewer on or queue instead of dispatching")
OLDEST_FIRST_SHARE = FitnessMeasure("your clearings that took the oldest waiting item first among your clearings", lambda counts: (counts.load.oldest_first, counts.load.clearings_counted), 0.8, 1.0, 2, "clear the worker or message that has waited longest first")
CALM_DISPATCH_SHARE = FitnessMeasure("your dispatches into idle places while the load was low among them and the dispatches made while the queue grew under a high load", lambda counts: (counts.load.dispatches_for, counts.load.dispatches_for + counts.load.dispatches_against), 0.8, 1.0, 2, "while the queue grows under a high load, clear it before you dispatch more")
MODEL_FIT_SHARE = FitnessMeasure("your merged jobs whose model fit the work among your newest merged jobs", lambda counts: (sum(1 for entry in counts.model_fits if entry.split(":", 1)[1] == RIGHT), len(counts.model_fits)), 0.7, 1.0, 2, "send small work on the fast model and keep the strongest for large work; work sent back again and again needs a stronger one")

WAIT_SHARE = FitnessMeasure("your started plans' blocked tasks that wait with --on or --until among them, the tasks that name another they do not wait on and the plans with no waits", lambda counts: counts.waits.scored(), 0.8, 1.0, 2, "block a task on what it waits for, --on task:<n> or --until '<command>', so it opens by itself", least=1)
INTERRUPTIONS = InterruptionMeasure("the reports an hour your workers filed while plenty of work was open", 3, "queue each worker several tasks with journal worker queue <n> <task>... --report queue, so it reports once for all of them")
STEADY_QUEUES = QueueMeasure("your workers with merges whose queue neither stood empty while tasks were open nor piled up past what they drain", 3)


class WorkersProfiles:
    """The ideal agent of the orchestrator and the solo modes, scored on tool uses until the measures of plan 1034 replace them (the builder is judged by those already): the orchestrator hands most of the work out and still makes small fixes, the solo agent does all of it itself; the orchestrator is also scored on its handling of its load, the minutes it stays over the add-a-place level, clearing the oldest first and not dispatching while the queue grows, on whether the models of its merged jobs fit them, and on how its plans' tasks wait; with the reviewer on, reading the proofs and running the tests before a merge are the reviewer's, so the orchestrator is not measured on them; a share of events counts only once it has three of them, save the waits, which are the plans as they stand and count from one task."""

    ORCHESTRATOR = ModeProfile("orchestrator", (ORCHESTRATOR_WORKLOAD, INTERRUPTIONS, STEADY_QUEUES, WORKER_WAIT_SHARE, TASK_WAIT_SHARE, REUSE_SHARE, BRIEF_SHARE, PREPARED_MERGE_SHARE, ORCHESTRATOR_EDIT_SHARE, BUSY_MINUTES, OLDEST_FIRST_SHARE, CALM_DISPATCH_SHARE, MODEL_FIT_SHARE, WAIT_SHARE))
    ORCHESTRATOR_REVIEWER_PROFILE = ModeProfile("orchestrator", (ORCHESTRATOR_WORKLOAD, INTERRUPTIONS, STEADY_QUEUES, WORKER_WAIT_SHARE, TASK_WAIT_SHARE, REUSE_SHARE, BRIEF_SHARE, ORCHESTRATOR_EDIT_SHARE, BUSY_MINUTES, OLDEST_FIRST_SHARE, CALM_DISPATCH_SHARE, MODEL_FIT_SHARE, WAIT_SHARE))
    SOLO_PROFILE = ModeProfile("solo", (SOLO_FILE_EDIT_SHARE, SOLO_RESEARCH_SHARE))

    ALL = (ORCHESTRATOR, SOLO_PROFILE)

    @classmethod
    def mode_profile(cls, mode: str) -> ModeProfile | None:
        return next((profile for profile in cls.ALL if profile.mode == mode), None)

    @classmethod
    def reviewed_mode_profile(cls, mode: str) -> ModeProfile | None:
        return cls.ORCHESTRATOR_REVIEWER_PROFILE if mode == cls.ORCHESTRATOR.mode else cls.mode_profile(mode)
