from argparse import Namespace
from pathlib import Path

from journal.console.command import Command
from journal.support.caller import Caller
from journal.support.outline import Outline
from journal.features.docs.support.version3_doc import Version3Doc
from journal.models.doc import Doc
from journal.models.support.abstract_text import ABSTRACT_LENGTH_CHARACTERS
from journal.support.no_action_reason import NoActionReason
from journal.support.rejection import Rejection
from journal.repositories.docs import Docs
from journal.repositories.doc_revisions import DocRevisions
from journal.engine.clock import Clock




class DocCommand(Command):
    noun = "doc"

    def __init__(self, docs: Docs, revisions: DocRevisions, clock: Clock) -> None:
        self.docs, self.doc_revisions, self.clock = docs, revisions, clock

    def arguments(self, verbs) -> None:
        creation = self.verb(verbs, "create", "write a document of this environment; the project's are read here too")
        creation.add_argument("title")
        creation_text = creation.add_mutually_exclusive_group(required=True)
        creation_text.add_argument("--file", help="a markdown file holding its text; ## headings are its sections")
        creation_text.add_argument("--body", help="its text, as markdown; ## headings are its sections")
        creation.add_argument("--abstract", required=True, help=f"one short description of what it is about, at most {ABSTRACT_LENGTH_CHARACTERS} characters")
        creation.add_argument("--part", action="store_true", help="this is a part; the document is being written until a write without --part")
        update = self.verb(verbs, "update", "replace a document's text with a markdown file")
        update.add_argument("n", type=int)
        update_text = update.add_mutually_exclusive_group(required=True)
        update_text.add_argument("--file", help="a markdown file holding its whole new text; ## headings are its sections")
        update_text.add_argument("--body", help="its whole new text, as markdown; ## headings are its sections")
        update.add_argument("--abstract", default=None, help=f"a new short description, at most {ABSTRACT_LENGTH_CHARACTERS} characters")
        update.add_argument("--part", action="store_true", help="this is a part; a write without --part makes the document ready")
        self.verb(verbs, "ready", "mark a document as ready").add_argument("n", type=int)
        display = self.verb(verbs, "show", "a document: its outline, then one section at a time")
        display.add_argument("n", type=int)
        Outline.arguments(display)
        self.verb(verbs, "list", "every document found here: this environment's and the project's")
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
        imported = self.verb(verbs, "import", "import the documents of version 3; a title already here is skipped")
        imported.add_argument("folder", help="version 3's project/doc folder")

    def create(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.save(Doc(title=args.title, abstract=args.abstract, body=self.text(args), unfinished=args.part), caller.actor)
        print(f"doc {doc.id}: {doc.title}")
        return 0

    @staticmethod
    def text(args: Namespace) -> str:
        return Path(args.file).read_text() if args.file else args.body

    def update(self, args: Namespace, caller: Caller) -> int:
        data = self.docs.find(args.n)
        doc = self.docs.save(data.with_(body=self.text(args), abstract=data.abstract if args.abstract is None else args.abstract, unfinished=args.part), caller.actor)
        print(f"doc {doc.id} written anew: {doc.title}")
        return 0

    def ready(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.save(self.docs.find(args.n).finished(), caller.actor)
        print(f"doc {doc.id} is ready: {doc.title}")
        return 0

    def show(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.find(args.n)
        print("\n".join([f"doc {doc.id}: {doc.title}", *filter(None, (doc.abstract,)), *Outline.build(doc.body).summary(args)]))
        return 0

    def revisions(self, args: Namespace, caller: Caller) -> int:
        for revision in self.doc_revisions.document_revisions(self.docs.find(args.n)):
            print(f"{revision.number:>3}  {revision.creation_time.astimezone():%Y-%m-%d %H:%M}  {revision.creation_actor.actor_type.value:<6} {revision.change}")
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

    def settle(self, args: Namespace, caller: Caller) -> int:
        doc = self.docs.save(NoActionReason.signed(self.docs.find(args.n), args.why), caller.actor)
        print(f"doc {doc.id} signed off: {doc.settled_reason}")
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
            self.docs.project_saved(doc, caller.actor)
        print(f"{len(new)} documents brought in, {len(rows) - len(new)} already here")
        return 0
