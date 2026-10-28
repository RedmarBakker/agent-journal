from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.profile_body import ProfileBody
from journal.features.library.support.sequence_body import SequenceBody
from journal.features.library.support.template_body import TemplateBody
from journal.features.profiles.support.profile_files import PREFIX, ProfileFiles
from journal.models.library_item import LibraryItem
from journal.models.sequence import Sequence
from journal.repositories.library_items import LibraryItems
from journal.repositories.sequences import Sequences
from journal.repositories.templates import Templates
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.release import Release
from journal.version import VERSION
from sync_server.item_version import ItemVersion

LIBRARY_TITLE_SUFFIX = " (from the library)"


class LibraryImport:
    """Importing an item of the team's library as a row of this journal, written by the importer: a sequence or template through its repository, a profile as its file, each joined to a LibraryItem that keeps the local copy's body as written, so a later edit shows against it. An item that needs a newer journal is refused with the update line; one already imported is pointed to update; a title a local row already has gets the words from the library after it; a profile never takes a name the journal ships; and a sequence's triggers and allowed commands are shown, and written only once accepted."""

    def __init__(self, account: LibraryAccount, schema: Schema, items: LibraryItems, sequences: Sequences, templates: Templates, profiles: ProfileFiles) -> None:
        self.account, self.link = account, LibraryLink(account, schema)
        self.items, self.sequences, self.templates, self.profiles = items, sequences, templates, profiles

    def version(self, item_type: str, name: str, number: int | None) -> ItemVersion:
        version = self.link.version(item_type, name, number) if number is not None else self.link.item(item_type, name).versions[-1]
        if Release(version.lowest_version).is_newer(Release(VERSION)):
            raise Rejection(f"{item_type} {name} {version.number} needs journal {version.lowest_version}: journal update apply")
        return version

    def imported(self, item_type: str, name: str, number: int | None, actor: Actor, accepted: bool) -> LibraryItem:
        key = self.account.connection().key
        existing = self.items.imported(key, item_type, name)
        if existing is not None:
            raise Rejection(f"{item_type} {name} is imported already: journal library update {item_type} {name}")
        version = self.version(item_type, name, number)
        item = self.items.save(LibraryItem(library_key=key, item_type=item_type, name=name, version=version.number, body=version.body), actor)
        writers = {"sequence": self.sequence_row, "template": self.template_row, "profile": self.profile_file}
        if item_type not in writers:
            raise Rejection(f"the library imports {', '.join(writers)} here; {item_type} is not one of them")
        return writers[item_type](item, actor, accepted)

    def sequence_row(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        sequence = SequenceBody.sequence(item.body)
        if not accepted and (sequence.triggers or any(step.allowed_commands for step in sequence.steps)):
            self.items.delete(item, actor)
            raise Rejection(self.powers(sequence))
        title = sequence.title + LIBRARY_TITLE_SUFFIX if self.sequences.titled(sequence.title) else sequence.title
        row = self.sequences.save(sequence.with_(title=title), actor)
        self.items.joined(item, row, actor)
        return self.items.save(item.with_(body=SequenceBody.text(row)), actor)

    def template_row(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        template = TemplateBody.template(item.body)
        title = template.title + LIBRARY_TITLE_SUFFIX if self.templates.matching(title=template.title) else template.title
        row = self.templates.save(template.with_(title=title), actor)
        self.items.joined(item, row, actor)
        return self.items.save(item.with_(body=TemplateBody.text(row)), actor)

    def profile_file(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        profile = ProfileBody.profile(item.body)
        if profile.name.startswith(PREFIX) or profile.name in self.profiles.names():
            self.items.delete(item, actor)
            raise Rejection(f"a profile named {profile.name} is the journal's own or exists here already: the library's copy is not written over it")
        path = self.profiles.saved(profile)
        return self.items.save(item.with_(file_path=path), actor)

    @staticmethod
    def powers(sequence: Sequence) -> str:
        triggers = "; ".join(f"{trigger.trigger_type} {trigger.moment or trigger.text or trigger.pattern or trigger.tool}" for trigger in sequence.triggers) or "none"
        commands = "; ".join(command for step in sequence.steps for command in step.allowed_commands) or "none"
        return f"sequence {sequence.title} starts on: {triggers}, and lets these commands through: {commands}. Read them, then import again with --accept to write it"
