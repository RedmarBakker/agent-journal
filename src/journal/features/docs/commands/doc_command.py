from argparse import Namespace
from pathlib import Path

from journal.console.support.hub_choice import HubChoice
from journal.console.support.hub_rows import HubRows
from journal.console.command import Command, HELPER_KINDS, WORKER_KINDS
from journal.support.caller import Caller
from journal.support.outline import Outline
from journal.features.docs.support.version3_doc import Version3Doc
from journal.models.doc import Doc
from journal.models.doc_edit_mode import DocEditMode
from journal.support.rejection import Rejection
from journal.repositories.docs import Docs
from journal.repositories.doc_revisions import DocRevisions
from journal.engine.clock import Clock
from journal.sync.team_account import TeamAccount


class DocCommand(Command):
    noun = "doc"
    callers = {"show": HELPER_KINDS, "create": WORKER_KINDS, "update": WORKER_KINDS}

    def __init__(self, docs: Docs, revisions: DocRevisions, clock: Clock, hub_rows: HubRows, hub: HubChoice, account: TeamAccount) -> None:
        self.docs, self.doc_revisions, self.clock, self.hub_rows, self.hub, self.account = docs, revisions, clock, hub_rows, hub, account

    def arguments(self, verbs) -> None:
        creation = self.verb(verbs, "create", "write a document of this environment; the project's and every hub's are read here too")
        creation.add_argument("title")
        creation.add_argument("--file", required=True, help="a markdown file holding its text; ## headings are its sections")
        creation.add_argument("--abstract", default="", help="one line that says what it is")
        update = self.verb(verbs, "update", "write a document's text anew from a markdown file, its title kept")
        update.add_argument("n", type=int)
        update.add_argument("--file", required=True, help="a markdown file holding its whole new text; ## headings are its sections")
        update.add_argument("--abstract", default=None, help="a new one line that says what it is")
        display = self.verb(verbs, "show", "a document: its outline, then one section at a time")
        display.add_argument("n", help="the document's number, or a team's name and number such as acme:31")
        Outline.arguments(display)
        self.verb(verbs, "list", "every document found here: this environment's, the project's and every hub's")
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
        imported = self.verb(verbs, "import", "bring in the documents version 3 kept, each folder's doc.md; one titled as a document here already is left")
        imported.add_argument("folder", help="version 3's project/doc folder")

    def create(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.save(Doc(title=args.title, abstract=args.abstract, body=Path(args.file).read_text()), caller.actor)
        print(f"doc {doc.id}: {doc.title}")
        return 0

    def update(self, args: Namespace, caller: Caller) -> int:
        data = self.docs.find(args.n)
        doc = self.docs.save(data.with_(body=Path(args.file).read_text(), abstract=data.abstract if args.abstract is None else args.abstract), caller.actor)
        print(f"doc {doc.id} written anew: {doc.title}")
        return 0

    def show(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.find(self.hub_rows.number(args.n))
        print("\n".join([*filter(None, (f"doc {doc.id}: {doc.title}", doc.abstract)), *Outline.build(doc.body).summary(args)]))
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
        if args.keep_copy:
            on_hub = self.docs.save(doc.copy_on_hub(hub.row_id, mode, owner), caller.actor)
        else:
            on_hub = self.docs.save(doc.put_on_hub(hub.row_id, mode, owner), caller.actor)
            self.doc_revisions.moved(on_hub, caller.actor)
        print(f"doc {on_hub.id} is on the {hub.team_name} hub, {mode.value.replace('_', '-')}" + (f"; doc {doc.id} stays here" if args.keep_copy else ""))
        return 0

    def mode(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.find(args.n)
        if not doc.is_on_hub():
            raise Rejection(f"doc {doc.id} is not on the hub: journal doc share {doc.id} puts it there")
        self.docs.save(doc.with_(edit_mode=DocEditMode(args.mode)), caller.actor)
        print(f"doc {doc.id} is {args.mode.replace('_', '-')} on the hub")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        for doc in self.docs.all():
            print(f"{doc.id:>4}  {doc.title}")
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
