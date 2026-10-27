from dataclasses import replace

from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.portable_body import PortableBody
from journal.features.library.support.profile_body import ProfileBody
from journal.features.library.support.sequence_body import SequenceBody
from journal.features.library.support.template_body import TemplateBody
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.models.library_item import LibraryItem
from journal.repositories.library_items import LibraryItems
from journal.repositories.sequences import Sequences
from journal.repositories.templates import Templates
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.release import Release
from journal.version import VERSION


class LibraryUpdate:
    """Bringing an imported item to the library's latest version: the local copy, found by its imported_as link, is compared with the body kept when it was written; an unedited copy takes the new version and keeps its local title, an edited one is refused naming the fields that changed, unless the update replaces it."""

    def __init__(self, account: LibraryAccount, schema: Schema, items: LibraryItems, sequences: Sequences, templates: Templates, profiles: ProfileFiles) -> None:
        self.account, self.link = account, LibraryLink(account, schema)
        self.items, self.sequences, self.templates, self.profiles = items, sequences, templates, profiles

    def updated(self, item_type: str, name: str, actor: Actor, replacing: bool) -> LibraryItem:
        item = self.items.imported(self.account.connection().key, item_type, name)
        if item is not None and not self.items.has_copy(item, self.profiles.config.root):
            self.items.delete(item, actor)
            item = None
        if item is None:
            raise Rejection(f"{item_type} {name} is not imported here, or its copy was deleted: journal library import {item_type} {name}")
        latest = self.link.item(item_type, name).versions[-1]
        if latest.number <= item.version:
            raise Rejection(f"{item_type} {name} is at version {item.version} here, the library's latest")
        if Release(latest.lowest_version).is_newer(Release(VERSION)):
            raise Rejection(f"{item_type} {name} version {latest.number} needs journal {latest.lowest_version}: update the journal with journal update apply first")
        edited = self.edited_fields(item)
        if edited and not replacing:
            raise Rejection(f"{item_type} {name} was edited here ({', '.join(edited)} changed since version {item.version}): journal library update {item_type} {name} --replace takes version {latest.number} over your edits")
        return self.items.save(item.with_(version=latest.number, body=self.local_copy_replaced(item, latest.body, actor)), actor)

    def edited_fields(self, item: LibraryItem) -> list[str]:
        imported_fields, current = PortableBody.fields(item.body), PortableBody.fields(self.local_body(item))
        return sorted(name for name in set(imported_fields) | set(current) if imported_fields.get(name) != current.get(name))

    def local_body(self, item: LibraryItem) -> str:
        if item.item_type == "profile":
            imported = ProfileBody.profile(item.body)
            view = self.profiles.read(imported.name)
            return ProfileBody.text(replace(imported, description=view["description"], tools=view["tools"], body=view["body"]))
        [ref] = self.items.local_rows(item)
        return SequenceBody.text(self.sequences.find(ref.id)) if item.item_type == "sequence" else TemplateBody.text(self.templates.find(ref.id))

    def local_copy_replaced(self, item: LibraryItem, body: str, actor: Actor) -> str:
        if item.item_type == "profile":
            self.profiles.saved(ProfileBody.profile(body))
            return body
        [ref] = self.items.local_rows(item)
        if item.item_type == "sequence":
            row = self.sequences.find(ref.id)
            latest = SequenceBody.sequence(body)
            return SequenceBody.text(self.sequences.save(row.with_(steps=latest.steps, triggers=latest.triggers), actor))
        row = self.templates.find(ref.id)
        latest = TemplateBody.template(body)
        return TemplateBody.text(self.templates.save(row.with_(targets=latest.targets, purpose=latest.purpose, brief=latest.brief, parts=latest.parts, commands=latest.commands), actor))
