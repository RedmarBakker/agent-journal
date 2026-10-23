from journal.features.feature import Feature
from journal.features.workers.clock_conduct import ClockConduct
from journal.features.workers.listeners.shortfall_return import ShortfallReturn
from journal.features.workers.listeners.task_touch import TaskTouch
from journal.features.workers.listeners.pool_job_intake import PoolJobIntake
from journal.features.workers.support.pool_worker_writes import PoolWorkerWrites
from journal.features.workers.support.pool_runner_writes import PoolRunnerWrites
from journal.features.workers.listeners.worker_task_changes import WorkerTaskChanges
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
from journal.engine.nudge import Nudge
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
from journal.features.workers.listeners.dispatch_refusal_cards import DispatchRefusalCards
from journal.features.workers.listeners.silent_worker_record import SilentWorkerRecord
from journal.features.workers.states.delegating import Delegating
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.states.soloing import Soloing


class Workers(Feature[WorkersData]):
    """A worker is an agent sent to write: code in a worktree of its own, a document, a change. A subagent only reads; a worker is the one that writes."""
    TIMEOUT = Option("workers.timeout_minutes", "Time limit of a worker run", "Minutes a worker may run before it is stopped and its report says so; 0 sets no limit", 60, unit="min")
    MODE = Option("workers.mode", "Work mode", "Builder: the agent builds it itself and sends workers when a job is better done beside it. Orchestrator: it plans, hands the work to workers, then reviews and merges it. Solo: it does everything itself, with no workers", "builder", kind="choice", choices=("builder", "orchestrator", "solo"), scope=OptionScope.PERSON, setter=USER)
    CHECK_REMINDER_USES = Option("workers.check_reminder_uses", "Name work to check every", "Tool uses between the reminders, while the agent works on, of a worker's work that waits to be checked and merged", 25, unit="tool uses")
    WORKER_LIMIT = Option("workers.most_out", "Workers out at once", "The most workers out at a time; a dispatch past it is refused until one reports. 0 is no limit", 3, unit="workers")
    SUBAGENT_LIMIT = Option("workers.most_subagents", "Subagents running at once", "The most subagents running at a time; one more is held until one finishes. 0 is no limit", 5, unit="subagents")
    PROFILE_LIMIT = Option("workers.idle_kept", "Workers kept for reuse per profile", "The most workers of one profile kept out or idle for reuse; past it a dispatch of that profile is refused while one of them is idle, so the job goes to that one. Reviewers always start fresh. 0 is no limit", 8, unit="workers")
    WORKTREE_STEP = Option("workers.worktree_step", "Make worker worktrees the journal's way", "The journal makes a worker's worktree, a worktree of each inner repository it needs and its library folders; off, your own commands below make them, told where in JOURNAL_WORKTREE and on which branch in JOURNAL_BRANCH", True, kind="switch", scope=OptionScope.MACHINE)
    PREPARATION_COMMANDS = Option("workers.preparation_commands", "Commands before a worker's worktree is made", "Your own shell commands, one per line, run in the project folder just before a worker's worktree is made; each is told JOURNAL_WORKTREE, JOURNAL_BRANCH, JOURNAL_PROJECT, JOURNAL_REPOSITORIES, JOURNAL_LIBRARIES and JOURNAL_COPIES", [], kind="lines", scope=OptionScope.MACHINE)
    BUILT_PATHS = Option("workers.built_paths", "Folders built from the sources", "Folders, one per line, that a build makes from the sources, such as a built viewer; a worker's merge that clashes only in them takes the project's side and builds them again with the command below", [], kind="lines")
    BUILD_COMMAND = Option("workers.build_command", "Command that builds them", "The shell command, run in the worker's worktree, that builds the folders above again after a merge clashed only in them", "", kind="text")
    POOL_SLOTS = Option("workers.pool_slots", "Worker slots given to the team's pool", "How many workers this machine runs at once for teammates who dispatch to the team's pool; 0 gives none", 0, unit="workers", scope=OptionScope.MACHINE, setter=USER)
    POOL_MINUTES = Option("workers.pool_daily_minutes", "Minutes a day of pool work on this machine", "How many minutes a day this machine runs workers for teammates, counted from midnight; past it a pool worker is turned down until the next day. 0 sets no limit", 0, unit="min", scope=OptionScope.MACHINE, setter=USER)
    POOL_PROFILES = Option("workers.pool_profiles", "Profiles a pool worker may use", "The worker profiles, one per line, a teammate may dispatch to the team's pool; a pool request naming another is refused", ["journal-medior"], kind="lines", setter=USER)
    COMPLETION_COMMANDS = Option("workers.completion_commands", "Commands after a worker's worktree is made", "Your own shell commands, one per line, run inside a worker's worktree once it is made, such as installing its dependencies; told the same as the commands before", [], kind="lines", scope=OptionScope.MACHINE)

    name = "workers"
    title = "Workers"
    help = "Agents sent to write one bounded job; the agent waits for their reports."
    modes = Modes(MODE, {"builder": PlansReady, "orchestrator": Orchestrating, "solo": Soloing})
    options = (TIMEOUT, MODE, CHECK_REMINDER_USES, WORKER_LIMIT, SUBAGENT_LIMIT, PROFILE_LIMIT, WORKTREE_STEP, PREPARATION_COMMANDS, COMPLETION_COMMANDS, BUILT_PATHS, BUILD_COMMAND, POOL_SLOTS, POOL_MINUTES, POOL_PROFILES)
    states = (Orchestrating, Soloing, OrchestratingPlan, Delegating)
    commands = (WorkerCommand, SubagentCommand, ArrivalCommand, TodoCommand, ProofCommand, DepartureCommand)
    seeds = (WorkersSeed, SubagentsSeed)
    jobs = (WorkerWatch,)
    process_cards = (WorkerProcessCard, SubagentProcessCard)
    host_writers = (PoolWorkerWrites, PoolRunnerWrites)
    listeners = (SubagentRecord, SubagentCards, WorkerCards, WorkerMomentCards, DispatchRefusalCards, SilentWorkerRecord, WorkerTaskChanges, ShortfallReturn, TaskTouch, WorkerBriefRecord, WorkerNoteRecord, WorkerTurnRecord, SubagentTurnRecord, SubagentMessageRecord, PoolJobIntake)
    data = (WorkersDataReader,)
    conduct = (WorkersConduct,)
    worker_conduct = (ClockConduct,)

    READINESS = Nudge(name, "clock_in_first", "your writes wait until you clock in", "journal task show <n>, then journal clock-in", repeat_interval=0)
    OUTPUT_UNFINISHED = Nudge(name, "own_output_running", "your output {{n}} still runs, and your run ends when you stop", "wait for it, then stop again", repeat_interval=0)
    OUTPUT_END = Nudge(name, "own_output_ended", "output {{n}} ended with code {{status}}", "read it with journal output read {{n}} --summary", repeat_interval=0)
    USER_CLOSURE = Nudge(name, "task_closed_by_user", "the user closed your task {{task}}", "stop now", repeat_interval=0)
    BRIEF_CHANGED = Nudge(name, "brief_changed", "the user rewrote point {{points}} of task {{task}}'s brief", "read it again with journal task show {{task}} and prove those points again", repeat_interval=0)
    OPEN_TODOS = Nudge(name, "open_todos", "your to-do list has {{count}} open items: {{items}}", "finish them, or say why with journal clock-out", repeat_interval=0)
    WORK_READY = Nudge(name, "work_ready", "worker {{n}}, {{name}}, clocked out: task {{task}} is ready to check", "journal task show {{task}}, then journal worker check {{n}} <point>, or --short \"<what is missing>\"", repeat_interval=0)
    CHECK_REMINDER = Nudge(name, "check_reminder", "worker {{n}}, {{name}}: task {{task}} still waits to be checked", "journal task show {{task}}, then journal worker check {{n}} <point>, or --short \"<what is missing>\"", repeat_interval=180)
    RUN_UNFINISHED = Nudge(name, "run_unfinished", "worker {{n}}, {{name}}, ended its run without clocking out and still holds its task", "journal worker send {{n}} \"<job>\", or journal worker release {{n}}", repeat_interval=0)
    WORKER_ARRIVAL = Nudge(name, "worker_clocked_in", "worker {{n}}, {{name}}, clocked in and is at work on its task", repeat_interval=0)
    WORKER_REPORTED = Nudge(name, "worker_reported", "worker {{n}}, {{name}}, reported in the chat", repeat_interval=0)
    ORCHESTRATE = Nudge(name, "orchestrate", "{{count}} tasks are open across the plans: {{tasks}}", "dispatch a worker on each you can, journal worker dispatch \"<Name>\" --task <n>; block a task that waits and go on with the rest", repeat_interval=0)
    TASK_DELEGATION = Nudge(name, "delegate_the_task", "{{name}} is in hand and you orchestrate; {{logged}}", "hand it to a worker with journal worker dispatch \"<Name>\" --task <n>, and review its report", repeat_interval=0)
    BLOCKED_CHECK = Nudge(name, "check_blocked_tasks", "tasks {{tasks}} are paused or blocked", "resume a paused one you can go on with, unblock one whose wait has passed or that you can decide, and report what you decided", repeat_interval=300)
    CREW_REMINDER = Nudge(name, "dispatch_while_busy", "{{count}} tasks are open and no worker has them: {{tasks}}", "dispatch workers on them, or send each to the worker that knows its files", repeat_interval=120)
    PLACE_FREE = Nudge(name, "worker_place_free", "worker {{n}}, {{name}}, is done; open: {{tasks}}", "send it its next job with journal worker send {{n}}, or dispatch another worker", repeat_interval=0)
    ORCHESTRATOR_MODE = Nudge(name, "now_orchestrating", "you now work as the orchestrator", "hand every task you can to a worker with journal worker dispatch, review and merge what comes back, and run the full suite yourself; decide without waiting for the user except before a step that cannot be undone or reaches outside the project", repeat_interval=0)
    SOLO_MODE = Nudge(name, "now_solo", "you now work solo", "do every job yourself: no worker is dispatched", repeat_interval=0)
    SOLO_DISPATCH = Nudge(name, "no_workers_when_solo", "you work solo: no worker is dispatched", repeat_interval=0)
    WORKER_STOPPED_UNREPORTED = Nudge(name, "worker_stopped_unreported", "worker {{n}}, {{name}}, stopped before it reported", repeat_interval=0)
    SUBAGENT_OVERFLOW = Nudge(name, "too_many_subagents", "{{running}} subagents are running, the most at once", "wait for one, or do it yourself", repeat_interval=0)
    WORKER_OVERFLOW = Nudge(name, "too_many_workers", "{{out}} workers are out, the most at once", "`journal worker wait`, or send the job to one that reported", repeat_interval=0)
    WORKER_FILE = Nudge(name, "file_is_the_workers", "that file is in worker {{n}}'s worktree", "`journal worker send {{n}} \"<job>\"`, or wait for its report and merge", repeat_interval=0)
    UNREAD_WORKER_REPORTS = Nudge(name, "act_on_the_reports", "{{reports_waiting}} reported and you have not acted on it", "give it its next job, stop it, or mark it done", repeat_interval=180, blocks_regardless=True)
    WORKER_KNOWS_FILES = Nudge(name, "send_it_to_the_worker_that_knows", "{{count}} idle workers already worked on files this job names:\n{{workers}}", "send the job to one of them, or add --fresh to the dispatch", repeat_interval=0)
    IDLE_CAP = Nudge(name, "send_it_to_an_idle_worker", "{{count}} of the {{kept}} {{profile}} workers kept are idle:\n{{workers}}", "send the job to one of them, or retire one with `journal worker complete <n> --why \"<reason>\"`", repeat_interval=0)
    REUSE_QUESTION = Nudge(name, "could_it_be_reused", "can worker {{n}}, {{name}}, be reused?", "if so, `journal worker send {{n}} \"<job>\"`; if not, repeat the command with --why \"<why>\"", repeat_interval=0)
    SILENT_WORKER = Nudge(name, "worker_quiet", "worker {{n}}, {{name}}, has been quiet for {{minutes}} minutes", "look at its transcript, notify it with `journal worker notify {{n}} \"<text>\"`, or stop it", repeat_interval=0)
    SUBAGENT_REUSE = Nudge(name, "send_the_job_to_the_subagent", "{{count}} idle subagents already worked on files this job names:\n{{subagents}}", "send the job to one with its SendMessage line, or retire one with `journal subagent retire <n>`", repeat_interval=0)
    nudges = (READINESS, WORK_READY, RUN_UNFINISHED, USER_CLOSURE, BRIEF_CHANGED, OUTPUT_UNFINISHED, OUTPUT_END, OPEN_TODOS, WORKER_ARRIVAL, WORKER_REPORTED, WORKER_STOPPED_UNREPORTED, UNREAD_WORKER_REPORTS, SUBAGENT_OVERFLOW, WORKER_OVERFLOW, WORKER_FILE, SUBAGENT_REUSE, WORKER_KNOWS_FILES, IDLE_CAP, REUSE_QUESTION, SILENT_WORKER, ORCHESTRATE, TASK_DELEGATION, SOLO_DISPATCH, ORCHESTRATOR_MODE, SOLO_MODE, BLOCKED_CHECK, CREW_REMINDER, PLACE_FREE, CHECK_REMINDER)

    skill = Skill("workers", 'Send a worker to write a bounded job and wait for its report; load it before dispatching one', """
# Workers

A subagent only reads. A worker writes: code in a worktree of its own, a document, a change.

- `journal worker dispatch "<Name>" --task <n> --changes "<the files or document it changes>" --tests "No tests|Scoped tests|Full suite" --profile journal-senior|journal-medior ["<more to tell it>"] [--provider claude|codex] [--worktree --libraries <a,b> | --copies <a,b> | --no-libraries]`:
  name it after a distinguished figure with a twist on their trade. A worker writes: `--changes` names what it changes,
  and a job that only reads, searches, researches or reviews is always a subagent's, never a worker's. `--tests` names the
  test template that says how it tests, and its text goes into the brief: Scoped tests for most jobs, No tests when you
  run them yourself, and Full suite seldom, since the full suite is yours to run once its work is back; the project's own
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
  alone: it blocks it and continues with every other open task. Solo: you do everything yourself and a worker's dispatch is refused. The user sets it
  with the plan bar's buttons.
- A worker works a shift on its task: it clocks in with `journal clock-in`, maintains its own list with `journal todo`,
  proves each point of the brief with `journal proof <point> "<file:line, and the test>"` or says why not with
  `--not-done`, commits its work, and clocks out with `journal clock-out "<report>"`, its one report. You are informed when
  it clocks in, and once when its work is ready to check; your stops name the work still waiting.
- `journal worker wait <n> [<n>...]` waits until they have clocked out; stopping is fine while you wait.
- Check each proof: read them with `journal task show <task>`, then `journal worker check <n> <point>`, or
  `journal worker check <n> <point> --short "<what is missing>"`, which sends it back to the same worker on the same task.
  Once every point is checked, `journal worker merge <n>` takes its branch in and closes the task; nothing else adds a
  worker's work, not the end of its run, a hand merge or a commit's tasks-done line.
- A worker whose run ends without clocking out still owns its task: send it again with `journal worker send <n>`, or
  release the task with `journal worker release <n>`. `journal worker list` shows every worker, and the subagents you
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
- Open tasks a busy worker is to take after its current one go in its queue: `journal worker queue <n> <task> [<task>...]`.
  Each is delegated to that worker at once, so it is never offered to you, nor blocked or paused; when its work is merged
  you are given the next in its queue with the line that sends it. Releasing the worker opens its queued tasks again.
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
""", keywords=('worker', 'workers', 'helper', 'dispatch', 'worktree', 'send', 'notify'), required_states=('awaiting',))
