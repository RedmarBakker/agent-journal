from journal.events.blocking import Blocking
from journal.features.tasks.support.default_task_assigner import DefaultTaskAssigner
from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import AGENT, WORK
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.tasks.listeners.testing_run_end import TestingRunEnd
from journal.features.tasks.support.tasks_data_reader import TasksDataReader
from journal.features.tasks.support.tasks_data import TasksData
from journal.features.tasks.commands.wait_command import WaitCommand
from journal.features.tasks.commands.impasse_command import ImpasseCommand
from journal.features.tasks.commands.task_command import TaskCommand
from journal.features.tasks.listeners.clear_waits import ClearWaits
from journal.features.tasks.listeners.ended_agent_tasks import EndedAgentTasks
from journal.features.tasks.listeners.delivery_gate_check import DeliveryGateCheck
from journal.features.tasks.listeners.task_cycle_check import TaskCycleCheck
from journal.features.tasks.tasks_conduct import TasksConduct
from journal.features.tasks.task_edit_conduct import TaskEditConduct
from journal.support.agent_role import AgentRole
from journal.support.skill import Skill
from journal.features.tasks.states.choosing_paused_work import ChoosingPausedWork
from journal.features.tasks.listeners.paused_decline_clearing import PausedDeclineClearing
from journal.features.tasks.listeners.user_paused_work_decline import UserPausedWorkDecline
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.listeners.release_waits import ReleaseWaits
from journal.features.tasks.listeners.task_move_cards import TaskMoveCards
from journal.features.tasks.listeners.impasse_card import ImpasseCard
from journal.features.tasks.listeners.reply_task_links import ReplyTaskLinks
from journal.features.tasks.tasks_demands import TasksDemands
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.tasks.tasks_part import TasksPart
from journal.features.tasks.listeners.delete_ended_wait_checks import DeleteEndedWaitChecks
from journal.features.tasks.listeners.delete_passed_wait_check import DeletePassedWaitCheck
from journal.features.tasks.seeds.unused_wait_checks import UnusedWaitChecks
from journal.features.tasks.commands.worker_task_command import WorkerTaskCommand

class Tasks(Feature[TasksData]):
    name = TasksPart.name
    card_families = (CardFamily("tasks", "Tasks", "task", WORK), CardFamily("impasse", "Agent stuck", "warn", AGENT))
    card_types = (CardTypeEntry(CardType.TASK_MOVES, "Tasks started and completed", "tasks"), CardTypeEntry(CardType.TASK_PAUSES, "Tasks paused and blocked", "tasks"), CardTypeEntry(CardType.IMPASSE, "Agent stuck", "impasse"))
    title = "Tasks"
    help = "A task is one unit of work with a life; a stop with one in hand is told to carry on, and its log is asked for as the edits mount."
    states = (Ready, Working, Impasse, ExternalWait, ChoosingPausedWork)
    assigners = (DefaultTaskAssigner,)
    commands = (TaskCommand, WaitCommand, ImpasseCommand)
    helper_commands = {AgentRole.WORKER: (WorkerTaskCommand,)}
    demands = (TasksDemands.PRIORITIES,)
    options = (TasksOptions.AUTO, TasksOptions.WAKE_MINUTES, TasksOptions.WAKE_COUNT, TasksOptions.SHORT_WAIT_SECONDS, TasksOptions.TESTING_SUGGESTION_MINUTES, TasksOptions.TESTING_SUGGESTION_TOOL_USES, TasksOptions.PRIORITY_REMIND_TASKS, TasksOptions.PRIORITY_BLOCK_TASKS, TasksOptions.FIRST_DELAY, TasksOptions.TASK_REMINDER_INTERVAL, TasksOptions.LOG_LIMIT, TasksOptions.LOG_AGE_LIMIT, TasksOptions.BLOCK_BATCH)
    seeds = (UnusedWaitChecks,)
    answer_listeners = ((UserPausedWorkDecline, Blocking.NEXT_DECISION), (EndedAgentTasks, Blocking.NEXT_DECISION), (ClearWaits, Blocking.NEXT_DECISION), (TaskCycleCheck, Blocking.ANSWER), (DeliveryGateCheck, Blocking.ANSWER))
    listeners = (TestingRunEnd, PausedDeclineClearing, ReleaseWaits, DeleteEndedWaitChecks, DeletePassedWaitCheck, TaskMoveCards, ImpasseCard, ReplyTaskLinks)
    conduct = (TasksConduct, TaskEditConduct)
    helper_conduct = {AgentRole.WORKER: (TaskEditConduct,)}
    data = (TasksDataReader,)

    nudges = (TasksNudges.PAUSED_CHOICE, TasksNudges.WAIT_STOP, TasksNudges.WAIT_LIFTED, TasksNudges.WAIT_CHECK_PASSED, TasksNudges.WAIT_REFUSAL, TasksNudges.WAIT_SWITCH_REFUSAL, TasksNudges.WAIT_REASON_REQUEST, TasksNudges.WAIT_REASON_LINE, TasksNudges.OUTPUT_POLL_REFUSAL, TasksNudges.PRIORITIES_REMINDER, TasksNudges.PRIORITIES_REFUSAL, TasksNudges.TASK_CHANGED, TasksNudges.TASK_POINTS_CHANGED, TasksNudges.BLOCKED_REVIEW, TasksNudges.PAUSE_WAIT_END, TasksNudges.TASK_CONTINUATION, TasksNudges.STOP_LOG_REQUEST, TasksNudges.OPEN_TASK, TasksNudges.STOPPED_WITH_WORK, TasksNudges.UNLOGGED_TASK, TasksNudges.NEXT_TASK_STARTED, TasksNudges.PAUSED_TASKS, TasksNudges.POSTPONED_WORK, TasksNudges.COMMIT_CLOSURE, TasksNudges.STOP_POLLING, TasksNudges.LOG_REQUEST, TasksNudges.LOG_EDIT_BLOCK, TasksNudges.CURRENT_TASK_REMINDER, TasksNudges.PAUSED_TASK_REMINDER, TasksNudges.PAUSED_TASK_CLOSURE_REMINDER, TasksNudges.WAIT_CHECK, TasksNudges.IDLE_CHECK, TasksNudges.WAIT_END, TasksNudges.WAIT_NEXT_TASK, TasksNudges.WAIT_PAUSED_TASK, TasksNudges.TEST_FAILURE, TasksNudges.TESTING_SUGGESTION, TasksNudges.UNTESTED_TASK_EDITS, TasksNudges.WAIT_LONG, TasksNudges.TASK_REOPENED, TasksNudges.TASKS_RELEASED, TasksNudges.BROKEN_WAIT, TasksNudges.BLOCKED_TASK_REMINDER, TasksNudges.TASK_OPENED, TasksNudges.TASK_ARRIVED)

    skill = Skill("tasks", 'Declare, log and finish the current work; load it when you start or are asked to', """
# Tasks

A task is one unit of work with a lifecycle: open, started, done. Only one is current at a time. A quick edit
needs no task; file one for work that is an item of its own, that waits, or that the user should see tracked.

- `journal task create "<title>" --brief "<what and where to start>"` files one; `--start` starts it at once.
- Add `--from <message n>` when it comes from one of the user's messages, so the chat shows the task above it:
  `journal task create "Footer names the shop" --brief "Done when every page's footer shows the shop name" --from 412 --start`.
- Add `--priority low|high|critical` when the task is not normal.
- Five tasks of yours left at the default priority are asked about once; at ten your next write waits until each has
  one from `journal task edit <n> --priority <level>`, or `journal task priorities confirm` says normal is right.
- `journal task edit <n> --title "<title>" --brief "<what and done when>"` writes either or both anew: the title when
  the first was wrong, the brief when the user corrects a task or a plan's review changes it.
- Read the brief with `journal task show <n>` before you edit it: `--brief` replaces it whole.
- Never write a revision as a log line. Add `--from <message n>` to an edit when a message of the user's changes the task.
- `journal task start <n>` takes a task in hand; `journal task list` shows every task here.
- `journal task show <n>` reads one whole, title, state, plan and phase, brief and every log line, so you pick it up
  where it stood.
- Log with `journal task log <n> "<where it stands>"` after each step that matters, and always before a compaction.
- Only the task in hand takes a log line; change a task not running with `journal task edit`.
- Finish with `journal task complete <n> --how "<outcome>"`:
  `journal task complete 12 --how "Every footer shows the shop name; test_footer passes"`.
- One task is in hand at a time: starting another pauses the one in hand, and the output says so.
- `journal task pause <n> "<why>"` sets a started task aside for something else first; `journal task resume <n>` picks
  it up. Pause for choice, never for being stuck.
- A wait is a block the journal can see, never words in a log line.
- Block a task that waits on another with `journal task block <n> --on task:<m>`, or on an answer with
  `--on question:12`: it opens by itself once that row is answered or closed.
- Block one that waits on anything else with `--until '<command>'`, run every two minutes, such as a check that a pull
  request is merged; it opens once the command passes. Single quotes keep a `$(...)` in it to run each time.
- Block one that waits on a decision with no row to watch with `journal task block <n> "<what it waits on>"`, and open
  it with `journal task unblock <n>` when that has arrived.
- A blocked task is neither offered nor nudged, only listed with its reason.
- Unblocking a task or a plan, by hand or by its wait, releases its waits and retires the check its block made.
- Wait for something outside your control with `journal await "<what you wait for>" --output <n>` for a command in the
  background, or `--until "<script>"`, run every 30 seconds, for anything else; then end your turn.
- Add `--reader <name>` to a wait on a command to watch it as it runs while you wait.
- A wait ends by itself once its thing is done, and you are told the result; working again ends it too.
- A wait that names neither, or a wait on the user, is refused: ask with `journal question ask`, or end your turn.
- Log as you go, counted in edits: after twenty-five with nothing logged you are asked to, every twenty-five the current
  work is named again, and at fifty the next write waits for the log line (settings tasks.first_nudge_after,
  tasks.name_every and tasks.log_after). A log line starts a new version.
- A stop with current work names it again, three times a version; then the stop passes.
- A commit whose message includes `Journal: tasks done <n>` on a line of its own completes task n.
- Auto mode (the setting tasks.auto, on by default) works the list: at a stop, or when your task closes with none in
  hand, the journal starts the next for you, and only the user stops you.
- Auto mode's next is your own paused task whose wait ended first, then the next task of your plan or of an approved
  plan, then the first open task by priority.
- A task you paused by choice is never resumed for you: while it waits beside an open task, the stop asks which to take
  up, `journal task resume <n>` for the paused one or `journal task skip-paused` for the open one until your next close.
- An open task more urgent than every paused one is started at once; with no open task the first paused one is.
- With auto mode off the journal starts no task for you.
- File work you put off in words as a task: work put off in words is lost.
- Stopping with a task in hand is informed to continue.
- When you are stuck, say so with `journal stuck "<why>"`: the journal sends nothing until your next tool use.
""", keywords=('task', 'tasks', 'todo'), required_states=('working', 'stuck', 'awaiting'), commands=('task',))
