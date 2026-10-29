from journal.db.schema import Schema
from journal.features.library.support.library_entry import LibraryEntry
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.library_name import LibraryName
from journal.features.library.support.profile_body import ProfileBody
from journal.features.library.support.file_body import DOCUMENT_SUFFIX, FileBody
from journal.features.library.support.reader_body import ReaderBody
from journal.features.library.support.skill_body import SkillBody
from journal.features.skills.support.skill_files import HOMES, SkillFiles
from journal.features.library.support.sequence_body import SequenceBody
from journal.features.library.support.template_body import TemplateBody
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.shell.support.readers import Readers
from journal.providers.support.profile import Profile
from journal.providers.support.profile_type import ProfileType
from journal.repositories.sequences import Sequences
from journal.repositories.templates import Templates
from journal.support.rejection import Rejection
from sync_server.item_version import ItemVersion
from sync_server.publish_request import PublishRequest


class LibraryPublish:
    """Publishing a sequence or template by its number, or a profile, a reader or a skill by its name, or a document or a file by its path, to the team's library: its portable body posted as the next version, named from its title, with this journal's version as the lowest that reads it; a shipped, locked sequence may be published too."""

    def __init__(self, account: LibraryAccount, schema: Schema, sequences: Sequences, templates: Templates, profiles: ProfileFiles, readers: Readers) -> None:
        self.link = LibraryLink(account, schema)
        self.sequences, self.templates, self.profiles, self.readers = sequences, templates, profiles, readers

    def published(self, item_type: str, reference: str, note: str, description: str | None) -> ItemVersion:
        if item_type in ("document", "file"):
            return self.file_published(item_type, reference, note, description)
        bodies = {"sequence": self.sequence_body, "template": self.template_body, "profile": self.profile_body, "reader": self.reader_body, "skill": self.skill_body}
        if item_type not in bodies:
            raise Rejection(f"the library publishes {', '.join(bodies)} here; {item_type} is not one of them")
        entry = bodies[item_type](reference)
        return self.link.publish(item_type, entry.name, PublishRequest(description if description is not None else entry.title, entry.body, note))

    def sequence_body(self, reference: str) -> LibraryEntry:
        sequence = self.sequences.find(self.number(reference))
        return LibraryEntry(LibraryName.title_name(sequence.title), sequence.title, SequenceBody.text(sequence))

    def template_body(self, reference: str) -> LibraryEntry:
        template = self.templates.find(self.number(reference))
        return LibraryEntry(LibraryName.title_name(template.title), template.title, TemplateBody.text(template))

    def profile_body(self, reference: str) -> LibraryEntry:
        view = self.profiles.read(reference)
        profile = Profile(view["name"], view["description"], view["tools"], view["body"], ProfileType(view["profile_type"]))
        return LibraryEntry(view["name"], view["description"], ProfileBody.text(profile))

    def reader_body(self, reference: str) -> LibraryEntry:
        files = self.readers.files(reference)
        if not files:
            raise Rejection(f"no reader named {reference}: `journal reader list` shows them")
        return LibraryEntry(reference, reference, ReaderBody.text(files[0]))

    def file_published(self, item_type: str, reference: str, note: str, description: str | None) -> ItemVersion:
        path = self.profiles.config.root / reference
        if not path.is_file() or not path.resolve().is_relative_to(self.profiles.config.root.resolve()):
            raise Rejection(f"no file of this project at {reference}")
        if item_type == "document" and path.suffix != DOCUMENT_SUFFIX:
            raise Rejection(f"a document is a markdown file; publish {reference} as a file")
        data = path.read_bytes()
        name = LibraryName.title_name(path.stem) + path.suffix.lower()
        version = self.link.publish(item_type, name, PublishRequest(description if description is not None else path.name, FileBody.text(path.name, data), note))
        return version if version.is_complete() else self.link.put_file(item_type, name, version.number, path.name, data)

    def skill_body(self, reference: str) -> LibraryEntry:
        folder = self.profiles.config.root / HOMES[0] / reference
        if not folder.is_dir() or SkillFiles.is_journals(folder):
            raise Rejection(f"no skill of this project is named {reference}: the journal's own skills and a plugin's are not published")
        return LibraryEntry(reference, reference, SkillBody.text(folder))

    @staticmethod
    def number(reference: str) -> int:
        if not reference.isdigit():
            raise Rejection(f"a sequence or template is published by its number, not {reference!r}")
        return int(reference)
