from journal.features.shell.support.command_mark_policy import CommandMarkPolicy
from journal.support.card_outcome import CardOutcome
import time
from pathlib import Path

from journal.chat.docking import Docking
from journal.chat.process_card import ProcessCard
from journal.chat.process_cards import DOCK_TIME_KEY, AUTO_DOCKED, DOCKED, FINAL
from journal.chat.process_card_contents import ProcessCardContents
from journal.chat.card_detail import CardDetail
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.card_progress import CardProgress
from journal.features.shell.support.git_titles import GitTitles
from journal.features.shell.support.git_commands import GitCommands
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.output_view import OutputView
from journal.features.shell.support.output_views import OutputViews
from journal.features.shell.support.readers import Readers
from journal.models.command_output import CommandOutput
from journal.models.message import Message
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.messages import Messages
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.card_kind import CardKind
from journal.support.command_text import CommandText
from journal.features.shell.shell_options import ShellOptions
from journal.support.time_source import TimeSource

HEADLINE_CHARACTERS = 60
ENDED_DOCK_SECONDS = 5
DOCK_DELAY_SECONDS = 5
UNDOCK_TIME_KEY = "undock_at"


class OutputProcessCard(ProcessCard):
    """The process card of a watched output: its title, its reader's lines and its progress, active until the command ends; docked above the chat once it has run five seconds, so a quick command never docks; a card written for a run that has ended is final from its first write."""

    name = "output"

    def __init__(self, outputs: CommandOutputs, views: OutputViews, readers: Readers, messages: Messages, settings: SettingRows, docking: Docking, mark_policy: CommandMarkPolicy, time_source: TimeSource, git_titles: GitTitles) -> None:
        self.time_source, self.git_titles = time_source, git_titles
        self.outputs, self.views, self.readers, self.messages, self.settings, self.docking, self.mark_policy = outputs, views, readers, messages, settings, docking, mark_policy

    def card_contents(self, output: CommandOutput) -> ProcessCardContents | None:
        if self.mark_policy.forbids_mark(output):
            return None
        view = self.views.view(output)
        part = CommandText.shown(self.watched_part(output))
        data = {"kind": "card", "output": output.id, "line": part, "reader": output.watch_reader, "poor_line": self.views.poor_line(output, view), "empty_card": self.views.is_empty_card(output, view), "silent": view.silent, "summary_missing": self.views.is_summary_missing(output), "summary": self.views.summary(output), **self.progress(output, view).fields(), **self.run_times(output), **self.dock_state(output), FINAL: output.ended}
        return ProcessCardContents(self.name, output.environment_id, OutputView.key(output.row_id), self.title(output, part), data, Actor.system(), CardKind.COMMANDS, not output.ended, self.views.card_text(output, view), output.session)

    def stored_contents(self, outputs: list[CommandOutput]) -> list[ProcessCardContents]:
        return [contents for output in outputs if OutputFiles(Path(output.folder)).is_stored() and (contents := self.card_contents(output))]

    def refresh(self, message: Message) -> dict:
        output = self.outputs.find(message.data["output"])
        view = self.views.view(output)
        return {**self.progress(output, view).fields(), **CardDetail.parts(self.views.card_text(output, view)), **self.run_times(output), "active": not output.ended}

    def progress(self, output: CommandOutput, view: OutputView) -> CardProgress:
        return CardProgress(self.outcome(output), view.figure, view.fraction, view.ending, self.views.count(output), view.is_counting)

    @staticmethod
    def run_times(output: CommandOutput) -> dict:
        began = {"began_at": output.creation_time.timestamp()}
        return {**began, "ended_at": output.update_time.timestamp()} if output.ended else began

    def dock_state(self, output: CommandOutput) -> dict:
        cards = self.messages.keyed(OutputView.key(output.row_id), Actor.system())
        if not cards:
            return {DOCKED: True, AUTO_DOCKED: True, DOCK_TIME_KEY: output.creation_time.timestamp() + DOCK_DELAY_SECONDS} if not output.ended and self.settings.option(ShellOptions.OUTPUT_DOCK) else {}
        if not output.ended or not cards[0].data.get(AUTO_DOCKED):
            return {}
        return {UNDOCK_TIME_KEY: cards[0].data.get(UNDOCK_TIME_KEY) or self.undock_time(cards[0].data.get(DOCK_TIME_KEY, 0))}

    def undock_time(self, dock_time: float) -> float:
        current_time = self.time_source.seconds()
        return dock_time if current_time < dock_time else current_time + ENDED_DOCK_SECONDS

    @staticmethod
    def outcome(output: CommandOutput) -> CardOutcome:
        if ActivityLabel.is_reading(output.command):
            return CardOutcome.NONE
        if not output.ended:
            return CardOutcome.RUNNING
        return CardOutcome.PASSED if output.is_success() else CardOutcome.FAILED

    def title(self, output: CommandOutput, part: str) -> str:
        reader = self.readers.found(output.watch_reader)
        if GitCommands.is_git_line(output.command) and (plain := self.git_titles.title(output.command, output.ran_in)):
            return plain[:HEADLINE_CHARACTERS]
        heading = output.watch_title or (reader.label if reader is not None else "") or ActivityLabel.chain_label(part, output.command)
        topic = reader.topic(output.command) if reader is not None else ""
        full = reader.topic_label.replace("{topic}", topic) if topic and reader.topic_label and not output.watch_title else (f"{heading}: {topic}" if topic else heading)
        return full[:1].upper() + full[1:HEADLINE_CHARACTERS]

    @staticmethod
    def watched_part(output: CommandOutput) -> str:
        files = OutputFiles(Path(output.folder))
        if not files.is_stored() or not files.recorded():
            return output.headline()
        open_parts = [i for i in files.recorded() if not files.has_ended(i)]
        return files.part_text(open_parts[0] if open_parts else files.recorded()[-1])

    def undocked(self, output: CommandOutput, actor: Actor) -> None:
        for card in self.messages.keyed(OutputView.key(output.row_id), Actor.system()):
            self.docking.release(card, actor)

    def is_shown(self, output: CommandOutput) -> bool:
        return bool(self.messages.keyed(OutputView.key(output.row_id), Actor.system()))

    def card_view(self, output: CommandOutput) -> OutputView:
        cards = self.messages.keyed(OutputView.key(output.row_id), Actor.system())
        return OutputView.parsed(cards[0]) if cards else OutputView.empty()
