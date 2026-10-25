from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import AGENT
from journal.support.card_kind import CardKind
from journal.support.card_colouring import CardColouring
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.features.feature import Feature
from journal.features.workers.clock_conduct import ClockConduct
from journal.features.workers.listeners.shortfall_return import ShortfallReturn
from journal.features.workers.listeners.test_run_record import TestRunRecord
from journal.features.workers.listeners.fitness_record import FitnessRecord
from journal.features.workers.listeners.load_record import LoadRecord
from journal.features.workers.listeners.wait_record import WaitRecord
from journal.features.workers.listeners.model_fit_record import ModelFitRecord
from journal.features.workers.listeners.task_touch import TaskTouch
from journal.features.workers.listeners.pool_job_intake import PoolJobIntake
from journal.features.workers.support.pool_worker_writes import PoolWorkerWrites
from journal.features.workers.support.pool_runner_writes import PoolRunnerWrites
from journal.features.workers.listeners.worker_task_changes import WorkerTaskChanges
from journal.features.workers.listeners.test_turn_release import TestTurnRelease
from journal.features.workers.listeners.test_turn_task_release import TestTurnTaskRelease
from journal.features.workers.seeds.test_turns_resume import TestTurnsResume
from journal.features.workers.commands.tests_command import TestsCommand
from journal.features.workers.commands.arrival_command import ArrivalCommand
from journal.features.workers.commands.todo_command import TodoCommand
from journal.features.workers.commands.proof_command import ProofCommand
from journal.features.workers.commands.departure_command import DepartureCommand
from journal.features.workers.workers_conduct import WorkersConduct
from journal.features.workers.support.workers_data_reader import WorkersDataReader
from journal.features.workers.support.workers_data import WorkersData
from journal.features.workers.seeds.subagents_seed import SubagentsSeed
from journal.features.workers.seeds.workers_seed import WorkersSeed
from journal.features.workers.jobs.worker_watch import WorkerWatch
from journal.features.workers.jobs.worktree_cleanup import WorktreeCleanup
from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope
from journal.support.skill import Skill
from journal.features.workers.commands.subagent_command import SubagentCommand
from journal.features.workers.commands.worker_command import WorkerCommand
from journal.features.workers.listeners.subagent_cards import SubagentCards
from journal.features.workers.listeners.subagent_record import SubagentRecord
from journal.features.workers.listeners.subagent_message_record import SubagentMessageRecord
from journal.features.workers.listeners.subagent_turn_record import SubagentTurnRecord
from journal.features.workers.listeners.worker_brief_record import WorkerBriefRecord
from journal.features.workers.listeners.worker_note_record import WorkerNoteRecord
from journal.features.workers.listeners.worker_turn_record import WorkerTurnRecord
from journal.features.workers.listeners.worker_cards import WorkerCards
from journal.features.workers.support.subagent_process_card import SubagentProcessCard
from journal.features.workers.support.worker_process_card import WorkerProcessCard
from journal.engine.support.modes import Modes
from journal.features.plans.states.plans_ready import PlansReady
from journal.features.workers.listeners.worker_moment_cards import WorkerMomentCards
from journal.features.workers.listeners.limit_resumes import LimitResumes
from journal.features.workers.listeners.queue_turn_resumes import QueueTurnResumes
from journal.features.workers.listeners.queue_use_record import QueueUseRecord
from journal.features.workers.listeners.report_use_measure import ReportUseMeasure
from journal.features.workers.listeners.report_use_record import ReportUseRecord
from journal.features.workers.listeners.landed_lines_record import LandedLinesRecord
from journal.features.workers.listeners.quick_report_drop_card import QuickReportDropCard
from journal.features.workers.listeners.tiny_job_drop_card import TinyJobDropCard
from journal.features.workers.listeners.worker_merge_card import WorkerMergeCard
from journal.features.workers.listeners.worker_merge_refusal_card import WorkerMergeRefusalCard
from journal.features.workers.listeners.dispatch_refusal_cards import DispatchRefusalCards
from journal.features.workers.listeners.silent_worker_record import SilentWorkerRecord
from journal.features.workers.listeners.unfinished_clock_out import UnfinishedClockOut
from journal.features.workers.states.delegating import Delegating
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.states.soloing import Soloing
from journal.features.workers.workers_part import WorkersPart
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.listeners.test_run_card import TestRunCard
from journal.features.workers.support.test_run_process_card import TestRunProcessCard


class Workers(Feature[WorkersData]):
    """A worker is an agent sent to write: code in a worktree of its own, a document, a change. A subagent only reads; a worker is the one that writes."""

    name = WorkersPart.name
    card_families = (CardFamily("helpers", "Workers and subagents", "agents", AGENT, CardColouring.OUTCOME), CardFamily("fitness", "Fitness", "activity", AGENT),)
    card_kinds = (MarkKind("agents", "Agents talking to each other", "helpers", covers=(CardKind.SUBAGENTS, CardKind.WORKERS)), MarkKind(CardKind.SUBAGENTS, "Subagents", "helpers"), MarkKind(CardKind.WORKERS, "Workers", "helpers", messages=("report",)), MarkKind(CardKind.FITNESS, "Drops in the fitness", "fitness"),)
    title = "Workers"
    help = "Agents sent to write one bounded job; the agent waits for their reports. How workers test is one of three: the agent that merges runs the tests, a worker runs the tests it wrote, or a worker tests within a budget through journal tests turn, the agent reading the machine's load and the turns with journal tests load and setting the budget with journal tests budget; its own suite is never queued."
    modes = Modes(WorkersOptions.MODE, {"builder": PlansReady, "orchestrator": Orchestrating, "solo": Soloing})
    options = (WorkersOptions.IDLE_HOURS, WorkersOptions.MERGE_WINDOW_SECONDS, WorkersOptions.MERGE_LIMIT, WorkersOptions.BUILDER_HANDOVER_LIMIT, WorkersOptions.ORCHESTRATOR_LINE_LIMIT, WorkersOptions.ORCHESTRATOR_WRITES_PLANS, WorkersOptions.ORCHESTRATOR_APPROVES_PLANS, WorkersOptions.ORCHESTRATOR_PLAN_APPROVAL, WorkersOptions.ORCHESTRATOR_RELEASES, WorkersOptions.PLAN_STALL_MINUTES, WorkersOptions.FITNESS_THRESHOLD, WorkersOptions.LOAD_WINDOW, WorkersOptions.LOAD_HALF_LIFE, WorkersOptions.LOAD_WARN, WorkersOptions.BUILDER_CEILING, WorkersOptions.OWN_SHARE_FULL, WorkersOptions.OWN_SHARE_ZERO, WorkersOptions.OWN_SHARE_WEIGHT, WorkersOptions.REVIEWERS_MOST, WorkersOptions.VERIFIERS_MOST, WorkersOptions.BUILDER_LINES_PER_HANDOVER, WorkersOptions.BUILDER_MAY_DISPATCH, WorkersOptions.BUILDER_MAY_QUEUE, WorkersOptions.BUILDER_MAY_SUBAGENTS, WorkersOptions.SOLO_MAY_SUBAGENTS, WorkersOptions.LOAD_CRITICAL, WorkersOptions.SCALE_UP_AT, WorkersOptions.SCALE_DOWN_AT, WorkersOptions.SCALE_UP_DWELL, WorkersOptions.SCALE_DOWN_DWELL, WorkersOptions.PLACE_FLOOR, WorkersOptions.PLACE_CEILING, WorkersOptions.WEIGHT_USER_MESSAGE, WorkersOptions.WEIGHT_REPEAT_SEND_BACK, WorkersOptions.WEIGHT_IDLE_PLACE, WorkersOptions.RECOVERY_FULL, WorkersOptions.RECOVERY_ZERO, WorkersOptions.INTERRUPTION_WINDOW, WorkersOptions.INTERRUPTIONS_FULL, WorkersOptions.INTERRUPTIONS_ZERO, WorkersOptions.PLENTY_OPEN, WorkersOptions.QUICK_REPORT_MINUTES, WorkersOptions.QUICK_REPORT_DROP, WorkersOptions.TINY_JOB_DROP, WorkersOptions.DROP_RECOVERY_MINUTES, WorkersOptions.SMALL_TASK_POINTS, WorkersOptions.LARGE_TASK_POINTS, WorkersOptions.LONG_QUEUE_TASKS, WorkersOptions.MISFIT_DROP, WorkersOptions.QUEUE_WINDOW, WorkersOptions.QUEUE_DRAIN_HOURS, WorkersOptions.HELD_STILL_MINUTES, WorkersOptions.HELD_SHARE, WorkersOptions.UNORDERED_PLAN_TASKS, WorkersOptions.PRIORITIES_MINUTES, WorkersOptions.MODEL_FIT_SAMPLE, WorkersOptions.COSTLY_SHAPED_WORK, WorkersOptions.SOLO_DISPATCH_LIMIT, WorkersOptions.TIMEOUT, WorkersOptions.MODE, WorkersOptions.TESTING, WorkersOptions.TEST_RUNS, WorkersOptions.TEST_WAITING, WorkersOptions.TESTS_PER_RUN, WorkersOptions.TEST_RUN_MINUTES, WorkersOptions.FAILING_RUNS, WorkersOptions.TEST_COMMAND, WorkersOptions.TEST_COMMAND_PROOF, WorkersOptions.TEST_RUN_LINES, WorkersOptions.CHECK_REMINDER_USES, WorkersOptions.WORKER_LIMIT, WorkersOptions.SUBAGENT_LIMIT, WorkersOptions.PROFILE_LIMIT, WorkersOptions.WORKTREE_STEP, WorkersOptions.PREPARATION_COMMANDS, WorkersOptions.COMPLETION_COMMANDS, WorkersOptions.BUILT_PATHS, WorkersOptions.BUILD_COMMAND, WorkersOptions.POOL_SLOTS, WorkersOptions.POOL_MINUTES, WorkersOptions.POOL_PROFILES, WorkersOptions.REVIEWER_MODEL)
    states = (Orchestrating, Soloing, OrchestratingPlan, Delegating)
    commands = (WorkerCommand, SubagentCommand, ArrivalCommand, TodoCommand, ProofCommand, DepartureCommand, TestsCommand)
    seeds = (WorkersSeed, SubagentsSeed, TestTurnsResume)
    jobs = (WorkerWatch, WorktreeCleanup)
    process_cards = (WorkerProcessCard, SubagentProcessCard, TestRunProcessCard)
    host_writers = (PoolWorkerWrites, PoolRunnerWrites)
    listeners = (SubagentRecord, SubagentCards, WorkerCards, TestRunCard, WorkerMomentCards, WorkerMergeCard, LimitResumes, QueueTurnResumes, ReportUseRecord, LandedLinesRecord, QuickReportDropCard, TinyJobDropCard, ReportUseMeasure, QueueUseRecord, WorkerMergeRefusalCard, DispatchRefusalCards, SilentWorkerRecord, UnfinishedClockOut, WorkerTaskChanges, ShortfallReturn, TaskTouch, WorkerBriefRecord, WorkerNoteRecord, WorkerTurnRecord, SubagentTurnRecord, SubagentMessageRecord, PoolJobIntake, TestRunRecord, TestTurnRelease, TestTurnTaskRelease, LoadRecord, ModelFitRecord, WaitRecord, FitnessRecord)
    data = (WorkersDataReader,)
    conduct = (WorkersConduct,)
    worker_conduct = (ClockConduct,)

    nudges = (WorkersNudges.WAIT_MISSING, WorkersNudges.WAIT_TEXT, WorkersNudges.UNMOVED_TASKS, WorkersNudges.UNLINKED_TASKS, WorkersNudges.PRIORITIES, WorkersNudges.UNBLOCKER_QUEUED, WorkersNudges.MODEL_OVERPOWERED, WorkersNudges.MODEL_UNDERPOWERED, WorkersNudges.TEST_RUN_FAILED, WorkersNudges.WORKER_KEEPS_FAILING, WorkersNudges.CROWDED_RISING, WorkersNudges.CROWDED_CRITICAL, WorkersNudges.BUILDER_CROWDED, WorkersNudges.MODE_MAY_NOT, WorkersNudges.BUILDER_BUDGET, WorkersNudges.PLACE_OPENED, WorkersNudges.PLACE_CLOSED, WorkersNudges.BUILDER_ALIGNMENT, WorkersNudges.ORCHESTRATOR_ALIGNMENT, WorkersNudges.FITNESS_LOW, WorkersNudges.SOLO_ALIGNMENT, WorkersNudges.READINESS, WorkersNudges.TEST_HANDOVER, WorkersNudges.TEST_BUDGET_REFUSAL, WorkersNudges.JOURNAL_TESTS_REFUSAL, WorkersNudges.WORK_READY, WorkersNudges.RUN_UNFINISHED, WorkersNudges.USER_CLOSURE, WorkersNudges.OUTPUT_UNFINISHED, WorkersNudges.OUTPUT_END, WorkersNudges.OPEN_TODOS, WorkersNudges.WORKER_REPORTED, WorkersNudges.WORKER_STOPPED_UNREPORTED, WorkersNudges.UNREAD_WORKER_REPORTS, WorkersNudges.SUBAGENT_OVERFLOW, WorkersNudges.PLACES_FULL, WorkersNudges.WORKER_OVERFLOW, WorkersNudges.WORKER_FILE, WorkersNudges.SUBAGENT_REUSE, WorkersNudges.WORKER_KNOWS_FILES, WorkersNudges.IDLE_CAP, WorkersNudges.REUSE_QUESTION, WorkersNudges.SILENT_WORKER, WorkersNudges.SPLIT_ADVICE, WorkersNudges.PROOF_REJECTED, WorkersNudges.PROOF_REJECTED_REPEAT, WorkersNudges.PROOF_REJECTED_OFTEN, WorkersNudges.COSTLY_SHAPED_WORK, WorkersNudges.ORCHESTRATE, WorkersNudges.STARTED_PLANS, WorkersNudges.PLAN_STALLED, WorkersNudges.SUITE_BROKEN, WorkersNudges.WORKER_LIMITED, WorkersNudges.QUICK_REPORT, WorkersNudges.TINY_JOB, WorkersNudges.DELIVERED_WAITING, WorkersNudges.ACTIVE_WORKERS, WorkersNudges.TASK_DELEGATION, WorkersNudges.SOLO_DISPATCH, WorkersNudges.ORCHESTRATOR_MODE, WorkersNudges.SOLO_MODE, WorkersNudges.BLOCKED_CHECK, WorkersNudges.CREW_REMINDER, WorkersNudges.PLACE_FREE, WorkersNudges.IDLE_WORKER, WorkersNudges.RELEASE_REFUSED, WorkersNudges.CHECK_REMINDER)

    skill = Skill("workers", 'Send a worker to write a bounded job and wait for its report; load it before dispatching one', """
# Workers

A subagent only reads. A worker writes: code in a worktree of its own, a document, a change.

- `journal worker dispatch "<Name>" --task <n> --changes "<the files or document it changes>" --profile journal-senior|journal-medior ["<more to tell it>"] [--provider claude|codex] [--worktree --libraries <a,b> | --copies <a,b> | --no-libraries]`:
  name it after a distinguished figure with a twist on their trade. A worker writes: `--changes` names what it changes,
  and a job that only reads, searches, researches or reviews is always a subagent's, never a worker's. How it tests is the setting How workers test: with The journal runs them, the default, it runs none and names its tests when it clocks out, `journal clock-out "<report>" --tests "<arguments>"`; the journal runs the project's test command with them in its worktree, a card in your chat shows the run, and only a passing run lets the clock-out stand, a failing one going straight back to the worker; no worker is sent until you set the command with `journal tests command "<command>" --proof "<the arguments of one test that passes>"`. With Hand the tests over it runs none and its proofs name them for you to run; with Run the tests it wrote, `--tests` names the
  test template that says how, Scoped tests when not named and Full suite seldom, since the full suite is yours to run once its work is back; the project's own
  test templates are listed with `journal template list`. A worker is started only on a task: an open one with a
  brief, which is its job, or the one you own, which it then takes over. The task is the worker's from then on, never
  offered to you as next, until its work is merged or released. The profile sets its model and its instructions:
  medior, on Sonnet, for a job whose shape is defined; senior, on Opus, only for one that needs judgement. `--model` overrides it.
  In a project that contains repositories of its own, a worktree contains a worktree of each one the task's brief names
  (all of them when it names none), so name the repositories the job touches in the brief; each merges into its own.
  A worktree has no installed libraries of its own, so a worktree dispatch names them: `--libraries node_modules,.venv`
  links the main checkout's folders, `--copies vendor` gives the worker copies of its own (always copy composer's vendor:
  its autoloader loads classes from where vendor really is, so through a link the tests would run the main checkout's
  code), and `--no-libraries` gives none, for a job that changes the libraries. Each applies in every inner repository too.
  The project's own commands around the creation of a worktree are settings: `journal settings show workers.preparation_commands`,
  `workers.completion_commands` and `workers.worktree_step`, which you may set with `journal settings set`.
- The work mode is the bottom state of your stack. Builder, the default: you build it yourself and send a worker when a job
  is better done beside you. Orchestrator: you plan, give every task you can to a worker and review what comes back;
  a stop or a long idle time with open tasks tells you to check the plans and dispatch, and a current task is one to hand
  over, never to do yourself. The orchestrator decides on its own and keeps the work moving; it waits for the user only
  before a step that cannot be undone or reaches outside the project. A task that waits on something blocks that task
  alone: it blocks it and continues with every other open task. A task that waits on another task is blocked with
  `journal task block <n> --on task:<m>`, one that waits on anything else with `--until '<command>'`, so it opens by
  itself; a wait written only in words, in a log line or a reply, is one the journal cannot see, and you are told to make
  it a block. Blocked or paused tasks that stand still for workers.held_still_minutes, or that pass workers.held_share
  of the tasks not done, are named as a plan to restructure; a started plan with workers.unordered_plan_tasks open tasks
  and none blocked on another is asked which depend on which. Solo: you do everything yourself and a worker's dispatch is refused. The user sets it
  with the plan bar's buttons. When you drift from your mode you are told once: the builder that hands work out twice
  in a row with no code of its own between, the orchestrator past 200 lines of code of its own since its last handover,
  the solo agent sending subagents instead of reading itself; the limits are settings (workers.builder_handovers,
  workers.orchestrator_lines, workers.solo_dispatches).
  The orchestrator is asked at each phase start of a started plan, and every workers.priorities_minutes after its last
  answer, which open task unblocks the most others or itself, and whether the queues are in that order; it answers with
  `journal plan priorities '<the order and why>'`, kept on the plan. A task that says it unblocks the orchestrator (a
  permission, access, a credential) is named at once when it is queued behind others.
- A worker works a turn on its task: it clocks in with `journal clock-in`, maintains its own list with `journal todo`,
  proves each point of the brief with `journal proof <point> "<file:line, and the test>"` or says why not with
  `--not-done`, commits its work, and clocks out with `journal clock-out "<report>"`, its one report. You are informed when
  it clocks in, and once when its work is ready to check; your stops name the work still waiting.
- `journal worker wait <n> [<n>...]` waits until they have clocked out; stopping is fine while you wait.
- Check each proof: read them with `journal task show <task>`, then `journal worker check <n> <point>`, or
  `journal worker check <n> <point> --short "<what is missing>"`, which sends it back to the same worker on the same task.
  Once every point is checked, `journal worker merge <n>` takes its branch in and closes the task; nothing else adds a
  worker's work, not the end of its run, a hand merge or a commit's tasks-done line. A merge goes to the background at
  once with its card, step 1/5 to 5/5, while the plugins judge it; wait on its output as on any command.
- A worker whose run ends without clocking out still owns its task: send it again with `journal worker send <n>`, or
  release the task with `journal worker release <n>`, refused while tasks it completed wait for the merge unless
  `--drop`, which opens them again. `journal worker list` shows every worker, and the subagents you
  started with their state and task.
- A worker that runs past 60 minutes is stopped and its report says so (setting workers.timeout_minutes, 0 for no limit).
- On a shared journal, `journal worker dispatch ... --pool` sends the worker to the team's pool: a teammate's machine
  with a free worker slot runs it in a worktree cut from your environment's head, which is pushed to origin first, and
  pushes its branch back at clock-out; its clock-in, report and end reach you as from any worker, and you check and
  merge it the same way. It needs --worktree, a profile the team allows its pool (workers.pool_profiles), no --model,
  and a job that uses no secrets stored on your machine (--needs-secrets refuses it); one nobody takes in ten minutes,
  or whose machine goes offline, ends unfinished with the reason, to dispatch again. Your own machine gives the pool
  workers.pool_slots slots, 0 by default, which the user sets.
- Related work goes back to the worker that knows it: `journal worker send <n> "<next job>"` gives a worker that
  reported, or was stopped, its next job in its last session, with its memory of the last job, in the same worktree.
  Never dispatch a new worker for work one already out has done part of.
  `--model <model>` or `--profile <profile>` sends it the job on another model, in the same session and worktree: a stronger
  one for a worker sent back three times on one task, a cheaper one for one spending much on work of a settled shape.
  `journal worker list` names each worker's model, its spend so far and its send-backs on its task.
- Open tasks a busy worker is to take after its current one go in its queue: `journal worker queue <n> <task> [<task>...]`.
  Each is delegated to that worker at once, so it is never offered to you, nor blocked or paused; when its work is merged
  you are given the next in its queue with the line that sends it. Releasing the worker opens its queued tasks again.
- When a worker reports is its report choice, `--report each` (the default), `queue` or `every <n>`, on dispatch or
  queue: with queue or every n it clocks out of each task, which waits for the merge, and goes straight on to the next
  in its queue in the same session, telling you nothing until it reports. Give a worker several small tasks with
  `--report queue`, so it interrupts you once; you are told when a choice does not fit the work queued. Check a finished
  task's points with `journal worker check <n> <point> --task <task>` (`--short` puts the worker back on it), and one
  merge takes every completed task in, refused while any point is unchecked. Each report you get while plenty of work is
  open costs fitness, and a worker reporting within a minute of its job's start costs more at once.
- A worker still running takes a word in its live session: `journal worker notify <n> "<text>"`. Only a Claude
  worker has a session inbox; a Codex worker, and one that reported or was stopped, are refused with what to use instead.
- A dispatch whose brief names files an idle worker touched is refused, naming that worker and its send line; add
  `--fresh` only when the job needs a new worker. Once a profile has as many workers out or idle as the setting
  workers.idle_kept (8, 0 for no limit), a dispatch of that profile is refused while one of them is idle. A reviewer
  always starts new.
- `journal worker complete <n>` or `journal worker stop <n>` of an idle worker first asks whether it could be reused;
  repeat it with `--why "<reason>"` to retire it. A worker out silent for 20 minutes is named to you once.
- A worker lists the other workers of the agent that dispatched it with `journal worker peers` and reaches one with
  notify when it is out or send when it is idle; never itself, a retired one or another agent's workers.
- A subagent job on files an idle subagent of the same kind read is refused, naming its SendMessage line, so the
  subagent that knows the files takes it. `journal subagent retire <n>` releases a subagent: it is no longer offered
  and no longer counts among the subagents running at once (workers.most_subagents).
""", keywords=('worker', 'workers', 'helper', 'dispatch', 'worktree', 'send', 'notify'), required_states=('awaiting',), commands=('worker', 'subagent'), events=(WorkerDelivered,))
