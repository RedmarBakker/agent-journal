from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.library_name import LibraryName
from journal.features.library.support.profile_body import ProfileBody
from journal.features.library.support.sequence_body import SequenceBody
from journal.features.library.support.template_body import TemplateBody
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.providers.support.profile import Profile
from journal.providers.support.profile_type import ProfileType
from journal.repositories.sequences import Sequences
from journal.repositories.templates import Templates
from journal.support.rejection import Rejection
from sync_server.item_version import ItemVersion
from sync_server.publish_request import PublishRequest


class LibraryPublish:
    """Publishing a sequence or template by its number, or a profile by its name, to the team's library: its portable body posted as the next version, named from its title, with this journal's version as the lowest that reads it; a shipped, locked sequence may be published too."""

    def __init__(self, account: LibraryAccount, schema: Schema, sequences: Sequences, templates: Templates, profiles: ProfileFiles) -> None:
        self.link = LibraryLink(account, schema)
        self.sequences, self.templates, self.profiles = sequences, templates, profiles

    def published(self, item_type: str, reference: str, note: str, description: str | None) -> ItemVersion:
        bodies = {"sequence": self.sequence_body, "template": self.template_body, "profile": self.profile_body}
        if item_type not in bodies:
            raise Rejection(f"the library publishes {', '.join(bodies)} here; {item_type} is not one of them")
        name, title, body = bodies[item_type](reference)
        return self.link.publish(item_type, name, PublishRequest(description if description is not None else title, body, note))

    def sequence_body(self, reference: str) -> tuple[str, str, str]:
        sequence = self.sequences.find(self.number(reference))
        return LibraryName.from_title(sequence.title), sequence.title, SequenceBody.text(sequence)

    def template_body(self, reference: str) -> tuple[str, str, str]:
        template = self.templates.find(self.number(reference))
        return LibraryName.from_title(template.title), template.title, TemplateBody.text(template)

    def profile_body(self, reference: str) -> tuple[str, str, str]:
        view = self.profiles.read(reference)
        profile = Profile(view["name"], view["description"], view["tools"], view["body"], ProfileType(view["profile_type"]))
        return view["name"], view["description"], ProfileBody.text(profile)

    @staticmethod
    def number(reference: str) -> int:
        if not reference.isdigit():
            raise Rejection(f"a sequence or template is published by its number, not {reference!r}")
        return int(reference)
