from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.nudge import Nudge
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.ended_output import EndedOutput
from journal.features.shell.support.folder_change import FolderChange
from journal.features.shell.support.piped_test_run import PipedTestRun
from journal.features.shell.support.activity_label import LONG_RUNS
from journal.support.chain import Chain
from journal.support.command_shape import CommandShape
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.moment import Moment
from journal.support.timeout import Timeout
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.shell.shell_part import ShellPart

# the flag of an output read that picks lines by a pattern, the one kind of read a reader can stand for
PATTERN_READ = "--grep"

SILENCE_SECONDS = 5.0
BACKGROUND_CHECK_DELAY_SECONDS = 300.0
ALIAS_RUNS = 3
READER_RUNS = 5
COUNTING_SUGGESTION_RUNS = 50
TESTING = "testing"


class ShellConduct(Conduct):
    """The shell feature's conduct in every state: a file longer than the runner shows is read in parts, a journal command runs alone while an alias may chain, a test run piped into a filter is refused, a cd that would leave the shell outside its environment's folder is refused, a read of an output by hand is pointed at a reader or asked to become one, a line an alias runs is pointed at the alias and a line run three times is asked to become one, a test run no counting reader reads is offered one on its first run and every fiftieth, the commands that ended in the background are named once the agent is quiet, one the agent waits on left to the wait, one running five minutes is looked at, and a watched output's view is sent after every tool use until its command ends; a watched card that has shown nothing for 30 seconds is named once, after a tool use or while the agent waits."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return Transition.merged(self, [journal_isolation_check(self, event, settings), piped_test_check(self, event, settings), folder_change_check(self, event, settings), partial_read_check(self, event, settings), readers_check(self, event, settings), alias_check(self, event, settings), reader_suggestion_check(self, event, settings), counting_reader_check(self, event, settings)])

    def on_tool_finished(self, event: ToolFinished, settings: Settings) -> Transition:
        watch = event.data.part(ShellPart).watch
        if not watch.is_watching():
            return unread_check(self, event, settings)
        if watch.ending:
            return self.none(ShellNudges.WATCH_ENDED.create(n=watch.output, command=watch.command, ending=watch.ending, lines=watch.text()))
        return self.none(ShellNudges.WATCH_VIEW.create(n=watch.output, command=watch.command, lines=watch.text()))

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        return Transition.merged(self, [background_check(self, event, settings), ended_check(self, event, settings), unread_check(self, event, settings)])


def outcome_text(ended: tuple[EndedOutput, ...]) -> str:
    outcomes: dict[str, list[int]] = {}
    for output in ended:
        if output.summary is None:
            outcomes.setdefault(output.ending, []).append(output.id)
    grouped = [f"output{'s' if len(ids) > 1 else ''} {', '.join(map(str, ids))} {outcome}" for outcome, ids in outcomes.items()]
    return "; ".join([*grouped, *(f"output {output.id} {output.ending}: {output.summary}" for output in ended if output.summary is not None)])


def partial_read_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    cap = settings.integer(ShellOptions.SHOWN)
    return state.refuse(ShellNudges.PARTIAL_FILE_READ.create(lines=event.call.file_lines, cap=cap)) if event.call.file_lines > 2 * cap else state.none()


def journal_isolation_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    journal, parts = event.call.journal_parts()
    return state.refuse(ShellNudges.JOURNAL_COMMAND_ISOLATION.create()) if 0 < journal < parts else state.none()


def folder_change_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    changes = FolderChange.targets([part.text for part in event.call.parts])
    if not changes:
        return state.none()
    home = event.data.part(ShellPart).home
    targets = [target for target in changes if not FolderChange.is_home(target, home)]
    return state.refuse(ShellNudges.FOLDER_CHANGE_REFUSAL.create(target=targets[0], home=home)) if targets else state.none()


def reader_suggestion_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    shape = event.call.recorded().shape
    if not Timeout.tool_uses(READER_RUNS).is_elapsed(event.shape_runs) or ActivityLabel.build(shape) not in LONG_RUNS or any(r.commands.is_read(event.call.command) for r in shell.readers):
        return state.none()
    tip = ShellNudges.NEW_READER_SUGGESTION.create(command=shape)
    return state.none() if tip.rendered() in shell.tipped else state.none(tip)


def piped_test_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    program = PipedTestRun.piped_filter(event.call.command) if event.call.command and not event.subagent else ""
    return state.refuse(ShellNudges.PIPED_TEST_RUN.create(filter=program)) if program else state.none()


def counting_reader_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    shape = event.call.recorded().shape
    if ActivityLabel.build(shape) != TESTING or not Timeout.tool_uses(COUNTING_SUGGESTION_RUNS).started(1).is_period_start(event.shape_runs):
        return state.none()
    if any(r.is_counting() and r.commands.is_read(event.call.command) for r in event.data.part(ShellPart).readers):
        return state.none()
    return state.none(ShellNudges.COUNTING_READER_SUGGESTION.create(command=shape))


def alias_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    hints = [ShellNudges.ALIAS_HINT.create(name=alias.name, line=part.text) for part in event.call.parts for alias in shell.aliases if alias.matches(part.text)]
    if hints:
        return state.none(hints[0])
    command, shape = event.call.command, event.call.recorded().shape
    if not Timeout.tool_uses(ALIAS_RUNS).is_elapsed(event.shape_runs) or Chain.is_journal(CommandShape.inner(command)) or Chain.is_read_line(command) or " " not in shape:
        return state.none()
    reader = next((r.name for r in shell.readers if r.commands.is_read(command)), "<the reader that reads its output>")
    tip = ShellNudges.ALIAS_SUGGESTION.create(shape=shape, reader=f" --reader {reader}")
    return state.none() if tip.rendered() in shell.tipped else state.none(tip)


def readers_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    reads = [part for part in event.call.parts if part.reads_output]
    if not reads:
        return state.none()
    shell = event.data.part(ShellPart)
    tips = [ShellNudges.READER_HINT.create(reader=r.name, about=r.subject) for r in shell.readers if r.matches(reads[0].text)]
    # only a pattern read again is worth a reader; a plain --head, --tail or --lines read never is
    if PATTERN_READ in reads[0].read_shape and shell.output_reads.count(reads[0].read_shape) >= 2:
        tips.append(ShellNudges.READER_SUGGESTION.create(command=reads[0].read_shape))
    new_tips = [tip for tip in tips if tip.rendered() not in shell.tipped]
    return state.none(new_tips[0]) if new_tips else state.none()


def ended_check(state: BaseState, event: Ticked, settings: Settings) -> Transition:
    ended = event.data.part(ShellPart).unannounced
    if not Timeout.seconds(SILENCE_SECONDS).is_elapsed(event.silence_seconds) or not ended:
        return state.none()
    return state.none(ShellNudges.OUTPUTS_ENDED.create(outputs=outcome_text(ended), n=ended[0].id))


def unread_check(state: BaseState, event: AgentEvent, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    if event.subagent or not shell.unread or shell.unannounced:
        return state.none()
    interval = Timeout.tool_uses(settings.integer(ShellOptions.UNREAD_OUTPUT_INTERVAL)).combined(Timeout.seconds(settings.integer(FOREGROUND_OPTION)))
    if not interval.reset(shell.last_ending_line).has_passed(Moment(seconds=event.time, tool_uses=shell.tool_uses)):
        return state.none()
    return state.none(ShellNudges.UNREAD_OUTPUT.create(outputs=outcome_text(shell.unread), n=shell.unread[0].id))


def background_check(state: BaseState, event: Ticked, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    if not shell.background or not Timeout.seconds(BACKGROUND_CHECK_DELAY_SECONDS).started(shell.backgrounded_at).is_elapsed(event.time):
        return state.none()
    return state.none(ShellNudges.BACKGROUND_CHECK.create(background_outputs=", ".join(str(n) for n in shell.background)))
