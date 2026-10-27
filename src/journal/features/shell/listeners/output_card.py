from journal.features.shell.support.activity_label import LONG_RUNS, ActivityLabel
from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.saved import Saved
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.features.shell.support.activity_title import ActivityTitle
from journal.features.shell.support.reader_judge import ReaderJudge
from journal.models.command_output import CommandOutput
from journal.repositories.reader_reports import ReaderReports
from journal.support.actor import Actor


class OutputCard(Listener[Saved]):
    """An output moved to the background or watched is a process card in the chat once it has run 3 seconds, written again each time the output is saved, as it moves, is watched and ends; a run that ends sooner never reaches the chat, and one that ends in the foreground after its card showed keeps it, turned to how it ended."""

    def __init__(self, card: OutputProcessCard, cards: ProcessCards, judge: ReaderJudge, reports: ReaderReports, labels: ActivityLabel) -> None:
        self.labels = labels
        self.card, self.cards, self.judge, self.reports = card, cards, judge, reports

    def handle(self, event: Saved) -> None:
        output = event.model
        if not isinstance(output, CommandOutput):
            return
        if not (output.moved or output.is_watched or output.watch_reader):
            return
        is_long_run = output.has_run_long(output.update_time.timestamp()) or self.labels.line_label(output.command) in LONG_RUNS
        if self.card.is_shown(output) or is_long_run:
            if contents := self.card.card_contents(output):
                self.cards.show(contents)
                if output.is_watched and ActivityTitle.is_one_word(contents.label) and (report := self.judge.one_word_title_report(output, contents.label)):
                    self.reports.save(report, Actor.system())
