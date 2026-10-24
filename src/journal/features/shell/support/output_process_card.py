import time
from pathlib import Path

from journal.chat.docking import Docking
from journal.chat.process_card import ProcessCard
from journal.chat.process_cards import DOCK_TIME_KEY, AUTO_DOCKED, DOCKED
from journal.chat.process_card_contents import ProcessCardContents
from journal.chat.card_detail import CardDetail
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.card_progress import CardProgress
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

HEADLINE_CHARACTERS = 60
ENDED_DOCK_SECONDS = 5
DOCK_DELAY_SECONDS = 5
UNDOCK_TIME_KEY = "undock_at"


class OutputProcessCard(ProcessCard):
    """The process card of a watched output: its title, its reader's lines and its progress, active until the command ends; docked above the chat once it has run five seconds, so a quick command never docks."""

    name = "output"

    def __init__(self, outputs: CommandOutputs, views: OutputViews, readers: Readers, messages: Messages, settings: SettingRows, docking: Docking) -> None:
        self.outputs, self.views, self.readers, self.messages, self.settings, self.docking = outputs, views, readers, messages, settings, docking

    def card_contents(self, output: CommandOutput) -> ProcessCardContents:
        view = self.views.view(output)
        part = CommandText.shown(self.watched_part(output))
        data = {"kind": "card", "icon": "terminal", "output": output.id, "line": part, "reader": output.watch_reader, "poor_line": self.views.poor_line(output, view), "empty_card": self.views.is_empty_card(output, view), "silent": view.silent, "summary_missing": self.views.is_summary_missing(output), **self.progress(output, view).fields(), **self.dock_state(output)}
        return ProcessCardContents(self.name, output.environment_id, OutputView.key(output.row_id), self.title(output, part), data, Actor.system(), CardKind.COMMANDS, not output.ended, self.views.card_text(output, view), output.session)

    def refresh(self, message: Message) -> dict:
        output = self.outputs.find(message.data["output"])
        view = self.views.view(output)
        return {**self.progress(output, view).fields(), **CardDetail.parts(self.views.card_text(output, view)), "active": not output.ended}

    def progress(self, output: CommandOutput, view: OutputView) -> CardProgress:
        return CardProgress(self.tone(output), view.figure, view.fraction, view.ending, self.views.count(output), view.is_counting)

    def dock_state(self, output: CommandOutput) -> dict:
        cards = self.messages.keyed(OutputView.key(output.row_id), Actor.system())
        if not cards:
            return {DOCKED: True, AUTO_DOCKED: True, DOCK_TIME_KEY: time.time() + DOCK_DELAY_SECONDS} if not output.ended and self.settings.option(ShellOptions.OUTPUT_DOCK) else {}
        if not output.ended or not cards[0].data.get(AUTO_DOCKED):
            return {}
        return {UNDOCK_TIME_KEY: cards[0].data.get(UNDOCK_TIME_KEY) or self.undock_time(cards[0].data.get(DOCK_TIME_KEY, 0))}

    @staticmethod
    def undock_time(dock_time: float) -> float:
        current_time = time.time()
        return dock_time if current_time < dock_time else current_time + ENDED_DOCK_SECONDS

    @staticmethod
    def tone(output: CommandOutput) -> str:
        if not output.ended:
            return ""
        return "good" if output.is_success() else "bad"

    def title(self, output: CommandOutput, part: str) -> str:
        reader = self.readers.lookup(output.watch_reader) if output.watch_reader else None
        heading = output.watch_title or (reader.label if reader is not None else "") or ActivityLabel.build(part)
        topic = reader.topic(output.command) if reader is not None else ""
        full = f"{heading}: {topic}" if topic else heading
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

    def card_view(self, output: CommandOutput) -> OutputView:
        cards = self.messages.keyed(OutputView.key(output.row_id), Actor.system())
        return OutputView.parsed(cards[0]) if cards else OutputView.empty()
