from journal.models.doc import Doc
from journal.models.support.ref import Ref
from journal.repositories.docs import Docs
from journal.repositories.links import Links
from journal.repositories.scope import Scope

COPIED_FROM = "copied_from"
ATTACHED = "attached_to"


class DocSources:
    """Where a copy or an attachment of a hub document comes from, as it reads here: a source that is on the hub, or removed, which it is once the hub's document is gone, taken back off the hub or no longer readable; a copy and an attachment stay whatever becomes of their source."""

    def __init__(self, docs: Docs, links: Links, scope: Scope) -> None:
        self.docs, self.links, self.scope = docs, links, scope

    def copied(self, copy: Doc) -> str:
        return "; ".join(self.phrase("copied from", link.target) for link in self.links.all_matching(source=Ref.build(copy), kind=COPIED_FROM))

    def attached(self) -> list[str]:
        here = Ref("environments", self.scope.id)
        return [self.phrase("attached here:", link.source) for link in self.links.all_matching(target=here, kind=ATTACHED)]

    def phrase(self, what: str, source: Ref) -> str:
        found = self.docs.numbered([source.id])
        state = "on the hub" if found and found[0].is_on_hub() else "removed"
        title = f" {found[0].title}" if found and found[0].is_on_hub() else ""
        return f"{what} doc {source.id}{title} ({state})"
