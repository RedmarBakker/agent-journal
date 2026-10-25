from journal.models.doc import Doc
from journal.models.doc_edit_mode import DocEditMode
from journal.repositories.doc_revisions import DocRevisions
from journal.repositories.docs import Docs
from journal.support.actor import Actor


class HubMove:
    """A document put on the hub: its revisions move first and the document follows in the same write, so the revision record finds them and writes none of its own."""

    def __init__(self, docs: Docs, revisions: DocRevisions) -> None:
        self.docs, self.revisions = docs, revisions

    def put(self, doc: Doc, hub_id: int, mode: DocEditMode, owner: int, actor: Actor) -> Doc:
        with self.docs.writing():
            self.revisions.moved(doc, hub_id, actor)
            return self.docs.save(doc.put_on_hub(hub_id, mode, owner), actor)
