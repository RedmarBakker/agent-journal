from datetime import datetime, timezone
from pathlib import Path
from journal.support.actor import Actor

from journal.models.command_output import CommandOutput
from journal.support.missing_row import MissingRow
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.process_check import ProcessCheck


class CommandOutputs(ScopedRepository[CommandOutput]):
    model = CommandOutput

    def chain_output(self, chain: str) -> CommandOutput:
        rows = self.selected_globally(self.query().filter(chain=chain).order("id"))
        if not rows:
            raise MissingRow(self.table, chain)
        return rows[-1]

    def ran_in(self, folder: str) -> list[CommandOutput]:
        return self.selected(self.query().filter(ran_in=folder).order_descending("id"))

    def background(self, session: str) -> list[CommandOutput]:
        return [o for o in self.selected(self.query().filter(session=session, moved=True, ended=False).order("id")) if self.is_running(Path(o.folder))]

    def unfinished(self, creator: Actor) -> list[CommandOutput]:
        return self.selected(self.query().filter(creator=creator, moved=True, ended=False).order("id"))

    def recent_unwatched_moves(self, session: str | None, count: int) -> list[CommandOutput]:
        return self.selected(self.query().filter(session=session, moved=True, watch_reader="").order_descending("id").limit(count))

    def latest(self, count: int) -> list[CommandOutput]:
        return self.selected(self.query().order_descending("id").limit(count))

    def backgrounded(self, session: str | None) -> list[CommandOutput]:
        return self.selected(self.query().filter(session=session, moved=True).order("id"))

    def unended_outputs(self, numbers: list[int]) -> list[CommandOutput]:
        return [output for output in (self.find(number) for number in numbers) if not output.ended]

    def active_outputs(self, environment_id: int, excluded_folder: str) -> list[CommandOutput]:
        return [output for output in self.running(environment_id) if output.folder != excluded_folder]

    def running(self, environment_id: int) -> list[CommandOutput]:
        query = self.query().filter(environment_id=environment_id, ended=False).order("id")
        return [o for o in self.selected_globally(query) if self.is_running(Path(o.folder))]

    def running_among(self, ids: list[int]) -> list[CommandOutput]:
        return [output for output in self.selected_globally(self.query().filter_listed("id", tuple(ids))) if self.is_running(Path(output.folder))] if ids else []

    def unended(self) -> list[CommandOutput]:
        return self.selected_globally(self.query().filter(ended=False).order("id"))

    def watch(self, output: CommandOutput, reader: str, title: str, actor: Actor) -> CommandOutput:
        for watched in self.watched(output.session):
            self.save(watched.unwatched(), actor)
        return self.save(output.watched(reader, title), actor)

    def last_run(self, command: str) -> CommandOutput | None:
        rows = self.selected(self.query().filter(command=command, ended=True).order_descending("id").limit(1))
        return rows[0] if rows else None

    def previous_run(self, output: CommandOutput) -> CommandOutput | None:
        rows = self.selected(self.query().filter(command=output.command, ended=True).filter_less("id", output.row_id).order_descending("id").limit(1))
        return rows[0] if rows else None

    def reader_outputs(self, reader: str, last: int = 50) -> list[CommandOutput]:
        return self.selected(self.query().filter(watch_reader=reader).order_descending("id").limit(last))

    def running_watched(self) -> list[CommandOutput]:
        return self.selected_globally(self.query().filter(ended=False).filter_alternatives(self.query().filter(is_watched=True), self.query().filter_unequal("watch_reader", "")).order("id"))

    def all_carded(self) -> list[CommandOutput]:
        return self.selected_globally(self.query().filter_alternatives(self.query().filter(is_watched=True), self.query().filter(moved=True, ended=False)).order("id"))

    def watched(self, session: str | None) -> list[CommandOutput]:
        return self.selected(self.query().filter(session=session, is_watched=True).order("id"))

    def unread(self, session: str) -> list[CommandOutput]:
        return self.selected(self.query().filter(session=session, moved=True, ended=True, is_announced=True, is_read=False, watch_reader="").order("id"))

    def recent_interruptions(self, cutoff_at: datetime) -> list[CommandOutput]:
        return self.selected(self.query().filter(is_interrupted=True, moved=True).filter_greater("updated_at", cutoff_at).order("id"))

    def unannounced(self, session: str) -> list[CommandOutput]:
        return self.selected(self.query().filter(session=session, moved=True, ended=True, is_announced=False).order("id"))

    @staticmethod
    def is_running(folder: Path) -> bool:
        if not folder.is_dir() or (folder / "done").is_file():
            return False
        if not (folder / "pid").is_file():
            return True
        return ProcessCheck.is_running_text((folder / "pid").read_text())

    def surplus(self, stored: int) -> list[CommandOutput]:
        return list(reversed(self.selected_globally(self.query().order_descending("id").offset(stored))))
