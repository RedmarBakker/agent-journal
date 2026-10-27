from journal.models.doc import Doc
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.repositories.docs import Docs
from journal.repositories.links import Links
from journal.repositories.scope import Scope

COPY_SOURCE = Link.COPY_SOURCE
ATTACHED = Link.ATTACHED_TO


class DocSources:
    """Where a copy or an attachment of a hub document comes from, as it reads here: a source that is on the hub, or removed, which it is once the hub's document is gone, taken back off the hub or no longer readable; a copy and an attachment stay whatever becomes of their source."""

    def __init__(self, docs: Docs, links: Links, scope: Scope) -> None:
        self.docs, self.links, self.scope = docs, links, scope

    def copied(self, copy: Doc) -> str:
        return "; ".join(self.phrase("copied from", link.target) for link in self.links.all_matching(source=Ref.build(copy), link_type=COPY_SOURCE))

    def attached(self) -> list[str]:
        environment = Ref("environments", self.scope.id)
        return [self.phrase("attached here:", link.source) for link in self.links.all_matching(target=environment, link_type=ATTACHED)]

    def phrase(self, what: str, source: Ref) -> str:
        found = self.docs.numbered([source.id])
        state = "on the hub" if found and found[0].is_on_hub() else "removed"
        title = f" {found[0].title}" if found and found[0].is_on_hub() else ""
        return f"{what} doc {source.id}{title} ({state})"
