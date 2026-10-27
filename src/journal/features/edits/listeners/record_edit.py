import time as timing
from dataclasses import asdict, replace
from pathlib import Path

from journal.config import Config
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.edits.support.file_copies import STORED_CHARS, FileCopies
from journal.features.edits.support.image_files import ImageFiles
from journal.features.edits.support.file_modification_tracker import FileModificationTracker
from journal.features.edits.support.patch_rows import PatchRows
from journal.support.part import Part
from journal.support.actor import Actor
from journal.models.edit import Edit
from journal.repositories.edits import Edits
from journal.support.file_edit import FileEdit
from journal.support.file_write import FileWrite
from journal.support.time_source import TimeSource

ROW_COUNT = 200


class RecordEdit(AgentListener[ToolFinished]):
    """When a call that writes files ends, each file it wrote is stored as an edit row before the hook answers, so the pane that polls next sees it: for the editor's tools from the patch they return, or from the file against its last copy when they return none, for a shell line from the call's written paths against the file as the journal last saw it; the file as it is now is stored, so the next change is compared against it. A script that writes files by paths it builds is found by the files whose modification time changed."""

    blocking = True

    def __init__(self, config: Config, edits: Edits, copies: FileCopies, modified_at: FileModificationTracker, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.config, self.edits, self.copies, self.modified_at = config, edits, copies, modified_at

    def handle(self, event: ToolFinished) -> None:
        if event.call.is_journal:
            return
        if isinstance(event.call.operation, (FileEdit, FileWrite)):
            self.patched(event)
            return
        call_paths = [p for p in event.call.edited_paths if Part.is_project_file(p)]
        for path in dict.fromkeys(self.project_path(p) for p in [*call_paths, *self.modified_at.moved(event.tool_use)]):
            if not Part.is_journal_owned(path):
                self.changed(event, path)

    def patched(self, event: ToolFinished) -> None:
        if not event.call.edited_paths:
            return
        path = self.project_path(event.call.edited_paths[0])
        if Part.is_journal_owned(path):
            return
        patch = PatchRows.build(event.response)
        old_text = self.copies.last_text(path) if patch.rows else ""
        if not patch.rows:
            for file_path in dict.fromkeys(self.project_path(p) for p in event.call.edited_paths):
                if not Part.is_journal_owned(file_path):
                    self.changed(event, file_path)
            return
        self.recorded(Edit(session=event.session, tool_use=event.tool_use, path=path, edit_type="create" if isinstance(event.call.operation, FileWrite) else "edit", time=self.time_source.seconds(),
                       added=patch.counted("add"), removed=patch.counted("del"), first_line=patch.first_line, last_line=patch.last_line, rows=tuple(asdict(r) for r in patch.rows[:ROW_COUNT])), event, old_text)

    def changed(self, event: ToolFinished, path: str) -> None:
        if ImageFiles.is_image(path):
            self.pictured(event, path)
            return
        text = self.copies.current_text(path)
        last_text = self.copies.last_text(path)
        if text is None:
            self.deleted(event, path, last_text)
            return
        patch = PatchRows.version_rows(last_text, text)
        if not patch.rows:
            return
        self.recorded(Edit(session=event.session, tool_use=event.tool_use, path=path, edit_type="create" if not last_text else "edit", time=self.time_source.seconds(), command=event.call.command,
                       added=patch.counted("add"), removed=patch.counted("del"), first_line=patch.first_line, last_line=patch.last_line, rows=tuple(asdict(r) for r in patch.rows[:ROW_COUNT])), event, last_text)

    def pictured(self, event: ToolFinished, path: str) -> None:
        if (self.config.root / path).is_file():
            self.edits.record(Edit(session=event.session, tool_use=event.tool_use, path=path, edit_type="edit", time=self.time_source.seconds(), command=event.call.command), Actor.agent(event.session))

    def deleted(self, event: ToolFinished, path: str, last_text: str) -> None:
        if not last_text:
            return
        patch = PatchRows.version_rows(last_text, "")
        self.edits.record(Edit(session=event.session, tool_use=event.tool_use, path=path, edit_type="delete", time=self.time_source.seconds(), command=event.call.command, added=0, removed=patch.counted("del"), first_line=patch.first_line, last_line=patch.last_line, rows=tuple(asdict(r) for r in patch.rows[:ROW_COUNT]), old_text=self.bounded_texts(last_text, "")[0]), Actor.agent(event.session))
        self.copies.store(path, "")

    def recorded(self, edit: Edit, event: ToolFinished, old_text: str) -> None:
        text = self.copies.current_text(edit.path)
        bounded = self.bounded_texts(old_text, text)
        self.edits.record(replace(edit, old_text=bounded[0], new_text=bounded[1]), Actor.agent(event.session))
        if text is not None:
            self.copies.store(edit.path, text)

    def bounded_texts(self, old_text: str, new_text: str | None) -> tuple[str, str]:
        return ("", "") if new_text is None or len(old_text) > STORED_CHARS or len(new_text) > STORED_CHARS else (old_text, new_text)

    def project_path(self, path: str) -> str:
        try:
            return str(Path(path).resolve().relative_to(self.config.root.resolve()))
        except ValueError:
            return Path(path).name
