from argparse import Namespace
from pathlib import Path

from journal.console.support.hub_choice import HubChoice
from journal.console.support.hub_rows import HubRows
from journal.console.command import Command, HELPER_KINDS, WORKER_KINDS
from journal.support.caller import Caller
from journal.support.outline import Outline
from journal.features.docs.support.version3_doc import Version3Doc
from journal.features.docs.support.doc_sources import ATTACHED, COPIED_FROM, DocSources
from journal.features.docs.support.hub_move import HubMove
from journal.models.doc import Doc
from journal.models.doc_edit_mode import DocEditMode
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.scope import Scope
from journal.support.row_destination import RowDestination
from journal.support.no_action_reason import NoActionReason
from journal.support.rejection import Rejection
from journal.repositories.docs import Docs
from journal.repositories.doc_revisions import DocRevisions
from journal.engine.clock import Clock
from journal.sync.team_account import TeamAccount




class DocCommand(Command):
    noun = "doc"
    callers = {"show": HELPER_KINDS, "create": WORKER_KINDS, "update": WORKER_KINDS}

    def __init__(self, docs: Docs, revisions: DocRevisions, clock: Clock, hub_rows: HubRows, hub: HubChoice, account: TeamAccount, links: Links, scope: Scope, hub_move: HubMove, sources: DocSources, destination: RowDestination) -> None:
        self.docs, self.doc_revisions, self.clock, self.hub_rows, self.hub, self.account, self.links, self.scope, self.hub_move, self.sources = docs, revisions, clock, hub_rows, hub, account, links, scope, hub_move, sources
        self.destination = destination

    def arguments(self, verbs) -> None:
        creation = self.verb(verbs, "create", "write a document of this environment; the project's and every hub's are read here too")
        creation.add_argument("title")
        creation.add_argument("--file", required=True, help="a markdown file holding its text; ## headings are its sections")
        creation.add_argument("--abstract", default="", help="a one-line summary")
        creation.add_argument("--part", action="store_true", help="this is a part; the document is being written until a write without --part")
        update = self.verb(verbs, "update", "replace a document's text with a markdown file")
        update.add_argument("n", type=int)
        update.add_argument("--file", required=True, help="a markdown file holding its whole new text; ## headings are its sections")
        update.add_argument("--abstract", default=None, help="a new one-line summary")
        update.add_argument("--part", action="store_true", help="this is a part; a write without --part makes the document ready")
        self.verb(verbs, "ready", "mark a document as ready").add_argument("n", type=int)
        display = self.verb(verbs, "show", "a document: its outline, then one section at a time")
        display.add_argument("n", help="the document's number, or a team's name and number such as acme:31")
        Outline.arguments(display)
        self.verb(verbs, "list", "every document found here: this environment's, the project's and every hub's")
        exemption = self.verb(verbs, "settle", "sign a document off as needing no action, so it is no longer named as never acted on")
        exemption.add_argument("n", type=int)
        exemption.add_argument("--why", required=True, help="why it needs no action")
        self.verb(verbs, "revisions", "a document's revisions: number, when, who and what changed").add_argument("n", type=int)
        revision = self.verb(verbs, "revision", "one revision of a document, whole")
        revision.add_argument("n", type=int)
        revision.add_argument("k", type=int)
        closing = self.verb(verbs, "keep", "keep the open revision as it is; the next edit opens a new one")
        closing.add_argument("n", type=int)
        closing.set_defaults(verb="close_revision")
        sharing = self.verb(verbs, "share", "put a document of this environment on the hub, where it moves, read-only for the other members or free for them to edit")
        sharing.add_argument("n", type=int)
        sharing.add_argument("--mode", choices=(DocEditMode.READ_ONLY.value, DocEditMode.FREE.value), default=DocEditMode.READ_ONLY.value, help="read_only: only you and an admin change it; free: any member does")
        sharing.add_argument("--team", default="", help="the hub of the joined team of this name, which a journal of one team need not name")
        sharing.add_argument("--keep-copy", action="store_true", help="keep a copy of the document here; the hub gets a copy of its own")
        changing = self.verb(verbs, "mode", "change who may edit a document on the hub; only whoever put it there or an admin may")
        changing.add_argument("n", type=int)
        changing.add_argument("mode", choices=(DocEditMode.READ_ONLY.value, DocEditMode.FREE.value))
        copying = self.verb(verbs, "copy", "save a hub document as a document of this environment that stays on this machine: it never syncs, and the hub's stays as it is")
        copying.add_argument("n", type=int)
        attaching = self.verb(verbs, "attach", "attach a hub document that is free to edit to this environment: it is edited in place, on the hub")
        attaching.add_argument("n", type=int)
        unsharing = self.verb(verbs, "unshare", "take a document back off the hub, to this environment, where it is a document of your own again; the other members' journals let it go, and a copy or an attachment of it there stays, its source shown as removed")
        unsharing.add_argument("n", type=int)
        imported = self.verb(verbs, "import", "import the documents of version 3; a title already here is skipped")
        imported.add_argument("folder", help="version 3's project/doc folder")

    def create(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.save(Doc(title=args.title, abstract=args.abstract, body=Path(args.file).read_text(), unfinished=args.part), caller.actor)
        print(f"doc {doc.id}: {doc.title}{self.destination.phrase(doc)}")
        return 0

    def update(self, args: Namespace, caller: Caller) -> int:
        data = self.docs.find(args.n)
        doc = self.docs.save(data.with_(body=Path(args.file).read_text(), abstract=data.abstract if args.abstract is None else args.abstract, unfinished=args.part), caller.actor)
        print(f"doc {doc.id} written anew: {doc.title}")
        return 0

    def ready(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.save(self.docs.find(args.n).finished(), caller.actor)
        print(f"doc {doc.id} is ready: {doc.title}")
        return 0

    def show(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.find(self.hub_rows.number(args.n))
        print("\n".join([*filter(None, (f"doc {doc.id}: {doc.title}", doc.abstract, self.sources.copied(doc))), *Outline.build(doc.body).summary(args)]))
        return 0

    def revisions(self, args: Namespace, caller: Caller) -> int:
        for revision in self.doc_revisions.document_revisions(self.docs.find(args.n)):
            print(f"{revision.number:>3}  {revision.creation_time.astimezone():%Y-%m-%d %H:%M}  {revision.creation_actor.kind.value:<6} {revision.change}")
        return 0

    def revision(self, args: Namespace, caller: Caller) -> int:
        revisions = self.doc_revisions.document_revisions(self.docs.find(args.n))
        if not 1 <= args.k <= len(revisions):
            raise Rejection(f"doc {args.n} has revisions 1 to {len(revisions)}" if revisions else f"doc {args.n} has no revisions yet")
        revision = revisions[args.k - 1]
        print(f"""doc {args.n}, revision {revision.number} of {len(revisions)}: {revision.title}
{revision.abstract}

{revision.body}""".rstrip())
        return 0

    def close_revision(self, args: Namespace, caller: Caller) -> int:
        closed = self.doc_revisions.close(self.docs.find(args.n), self.clock.time(), caller.actor)
        print(f"revision {closed.number} of doc {args.n} kept; the next edit opens revision {closed.number + 1}")
        return 0

    def share(self, args: Namespace, caller: Caller) -> int:
        doc, hub, mode = self.docs.find(args.n), self.hub.hub(args.team), DocEditMode(args.mode)
        if doc.is_on_hub():
            raise Rejection(f"doc {doc.id} is on the hub already: journal doc mode {doc.id} {mode.value} changes who may edit it")
        owner = self.account.user_number()
        on_hub = self.hub_move.put(doc, hub.row_id, mode, owner, caller.actor)
        copy = self.copy_of(on_hub, caller) if args.keep_copy else None
        print(f"doc {on_hub.id} is on the {hub.team_name} hub, {mode.value.replace('_', '-')}" + (f"; doc {copy.id} is a copy of it kept here" if copy else ""))
        return 0

    def copy(self, args: Namespace, caller: Caller) -> int:
        doc = self.on_hub(args.n)
        copy = self.copy_of(doc, caller)
        print(f"doc {copy.id}: a copy of doc {doc.id}, kept on this machine")
        return 0

    def copy_of(self, doc: Doc, caller: Caller) -> Doc:
        copy = self.docs.save(doc.local_copy(), caller.actor)
        self.links.save(Link(source=Ref.build(copy), target=Ref.build(doc), kind=COPIED_FROM), caller.actor)
        return copy

    def attach(self, args: Namespace, caller: Caller) -> int:
        doc = self.on_hub(args.n)
        if doc.edit_mode != DocEditMode.FREE:
            raise Rejection(f"doc {doc.id} is read-only on the hub, so it cannot be edited in place here: journal doc copy {doc.id} saves a copy of it")
        environment = Ref("environments", self.scope.id)
        if self.links.all_matching(source=Ref.build(doc), target=environment, kind=ATTACHED):
            raise Rejection(f"doc {doc.id} is attached to this environment already")
        self.links.save(Link(source=Ref.build(doc), target=environment, kind=ATTACHED), caller.actor)
        print(f"doc {doc.id} is attached here, and edited in place on the hub")
        return 0

    def on_hub(self, number: int) -> Doc:
        doc = self.docs.find(number)
        if not doc.is_on_hub():
            raise Rejection(f"doc {doc.id} is not on the hub: journal doc share {doc.id} puts it there")
        return doc

    def unshare(self, args: Namespace, caller: Caller) -> int:
        doc = self.on_hub(args.n)
        back = self.hub_move.take_back(doc, self.scope.id, caller.actor)
        print(f"doc {back.id} is off the hub and a document of this environment again")
        return 0

    def mode(self, args: Namespace, caller: Caller) -> int:
        doc = self.on_hub(args.n)
        self.docs.save(doc.with_(edit_mode=DocEditMode(args.mode)), caller.actor)
        print(f"doc {doc.id} is {args.mode.replace('_', '-')} on the hub")
        return 0

    def settle(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.save(NoActionReason.signed(self.docs.find(args.n), args.why), caller.actor)
        print(f"doc {doc.id} signed off: {doc.settled_reason}")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        for doc in self.docs.all():
            print(f"{doc.id:>4}  {doc.title}" + (f"  ({self.sources.copied(doc)})" if doc.is_copy else ""))
        for line in self.sources.attached():
            print(line)
        return 0

    def import_(self, args: Namespace, caller: Caller) -> int:
        folder = Path(args.folder).expanduser()
        if not folder.is_dir():
            raise Rejection(f"no such folder: {folder}")
        rows = [doc for doc in map(Version3Doc.read, sorted(p for p in folder.iterdir() if p.is_dir())) if doc]
        new = [doc for doc in rows if not self.docs.titled(doc.title)]
        for doc in new:
            self.docs.of_project(doc, caller.actor)
        print(f"{len(new)} documents brought in, {len(rows) - len(new)} already here")
        return 0
