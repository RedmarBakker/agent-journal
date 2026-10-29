from journal.config import Config
from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.profile_body import ProfileBody
from journal.features.library.support.file_body import FileBody
from journal.features.library.support.plan_body import PlanBody
from journal.features.library.support.reader_body import ReaderBody
from journal.models.link import Link
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.phases import Phases
from journal.repositories.plans import PHASE_LINK, PHASE_TASK_LINK, PLAN_LINK, Plans
from journal.repositories.tasks import Tasks
from journal.features.library.support.skill_body import SkillBody
from journal.features.skills.support.skill_files import HOMES
from journal.features.library.support.sequence_body import SequenceBody
from journal.features.library.support.template_body import TemplateBody
from journal.features.profiles.support.profile_files import PREFIX, ProfileFiles
from journal.models.library_item import LibraryItem
from journal.models.model import Model
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
    """Importing an item of the team's library as a row of this journal, written by the importer: a sequence or template through its repository, a profile as its file, each joined to a LibraryItem that keeps the local copy's body as written, so a later edit shows against it. An item that needs a newer journal is refused with the update line; one already imported is pointed to update; a title a local row already has gets the words from the library after it; a profile never takes a name the journal ships; and a sequence's triggers and allowed commands, like a reader's pattern or script, are shown, and written only once accepted."""

    def __init__(self, account: LibraryAccount, schema: Schema, items: LibraryItems, sequences: Sequences, templates: Templates, profiles: ProfileFiles, config: Config, plans: Plans, phases: Phases, tasks: Tasks, links: Links) -> None:
        self.account, self.link, self.config = account, LibraryLink(account, schema), config
        self.items, self.sequences, self.templates, self.profiles = items, sequences, templates, profiles
        self.plans, self.phases, self.tasks, self.links = plans, phases, tasks, links

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
        writers = {"sequence": self.sequence_row, "template": self.template_row, "profile": self.profile_file, "reader": self.reader_file, "skill": self.skill_folder, "document": self.project_file, "file": self.project_file, "plan": self.draft_plan}
        if item_type not in writers:
            raise Rejection(f"the library imports {', '.join(writers)} here; {item_type} is not one of them")
        return writers[item_type](item, actor, accepted)

    def sequence_row(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        sequence = SequenceBody.sequence(item.body)
        if not accepted and (sequence.triggers or any(step.allowed_commands for step in sequence.steps)):
            self.items.delete(item, actor)
            raise Rejection(self.powers(sequence))
        row = self.sequences.save(sequence.with_(title=self.free_title(sequence.title, self.sequences.titled(sequence.title))), actor)
        return self.joined_item(item, row, SequenceBody.text(row), actor)

    def template_row(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        template = TemplateBody.template(item.body)
        row = self.templates.save(template.with_(title=self.free_title(template.title, bool(self.templates.matching(title=template.title)))), actor)
        return self.joined_item(item, row, TemplateBody.text(row), actor)

    def joined_item(self, item: LibraryItem, row: Model, body: str, actor: Actor) -> LibraryItem:
        self.items.joined(item, row, actor)
        return self.items.save(item.with_(body=body), actor)

    @staticmethod
    def free_title(title: str, is_duplicate: bool) -> str:
        return title + LIBRARY_TITLE_SUFFIX if is_duplicate else title

    def profile_file(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        profile = ProfileBody.profile(item.body)
        if profile.name.startswith(PREFIX) or profile.name in self.profiles.names():
            self.items.delete(item, actor)
            raise Rejection(f"a profile named {profile.name} is the journal's own or exists here already: the library's copy is not written over it")
        path = self.profiles.saved(profile)
        return self.items.save(item.with_(file_path=path), actor)

    def reader_file(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        path = self.config.readers / ReaderBody.file_name(item.body)
        if not accepted or path.exists():
            self.items.delete(item, actor)
        if path.exists():
            raise Rejection(f"a reader file named {path.name} exists here already: the library's copy is not written over it")
        if not accepted:
            raise Rejection(f"reader {item.name} runs on your commands' output: read it below, then import with --accept\n{ReaderBody.file_text(item.body)}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ReaderBody.file_text(item.body))
        return self.items.save(item.with_(file_path=str(path.relative_to(self.config.root))), actor)

    def skill_folder(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        folder = self.config.root / HOMES[0] / item.name
        if folder.exists():
            self.items.delete(item, actor)
            raise Rejection(f"a skill named {item.name} exists here already: the library's copy is not written over it")
        skill_file = SkillBody.save(folder, item.body)
        return self.items.save(item.with_(file_path=str(skill_file.relative_to(self.config.root))), actor)

    def project_file(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        file_name = FileBody.file_name(item.body)
        path = self.config.root / file_name
        if path.exists():
            self.items.delete(item, actor)
            raise Rejection(f"a file named {file_name} exists here already: the library's copy is not written over it")
        path.write_bytes(self.link.file(item.item_type, item.name, item.version, file_name))
        return self.items.save(item.with_(file_path=file_name), actor)

    def draft_plan(self, item: LibraryItem, actor: Actor, accepted: bool) -> LibraryItem:
        title = PlanBody.title(item.body)
        plan = self.plans.save(Plan(title=self.free_title(title, bool(self.plans.matching(title=title)))), actor)
        for outline in PlanBody.phases(item.body):
            phase = self.phases.save(Phase(environment_id=plan.environment_id, title=outline.title, completion_rule=outline.completion_rule, checkpoint=outline.checkpoint), actor)
            self.links.save(Link(source=Ref.build(phase), target=Ref.build(plan), link_type=PHASE_TASK_LINK), actor)
            for task_title in outline.task_titles:
                task = self.tasks.save(Task(environment_id=plan.environment_id, title=task_title), actor)
                self.links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
                self.links.save(Link(source=Ref.build(task), target=Ref.build(phase), link_type=PHASE_LINK), actor)
        return self.joined_item(item, plan, item.body, actor)

    @staticmethod
    def powers(sequence: Sequence) -> str:
        triggers = "; ".join(f"{trigger.trigger_type} {trigger.moment or trigger.text or trigger.pattern or trigger.tool}" for trigger in sequence.triggers) or "none"
        commands = "; ".join(command for step in sequence.steps for command in step.allowed_commands) or "none"
        return f"sequence {sequence.title} starts on: {triggers}, and lets these commands through: {commands}. Read them, then import again with --accept to write it"
