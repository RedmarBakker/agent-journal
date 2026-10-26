from journal.events.listener import Listener
from journal.events.models.saving import Saving
from journal.models.doc import Doc
from journal.models.doc_edit_mode import DocEditMode
from journal.repositories.docs import Docs
from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from journal.support.rejection import Rejection
from journal.sync.hosting import Hosting
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink


class HubDocGuard(Listener[Saving]):
    """A change to a document on the hub is refused before it is made unless the person making it may: anyone changes the text of one free to edit, only whoever put it on the hub or an admin changes the text of a read-only one or who may edit it. The person is this journal's own, or on the hosted journal the one a browser signed in as; an admin of another journal is found among the team's people. The journal's own writes, a sync's among them, pass."""

    blocking = True

    def __init__(self, docs: Docs, account: TeamAccount, link: TeamServerLink, hosting: Hosting) -> None:
        self.docs, self.account, self.link, self.hosting = docs, account, link, hosting

    def handle(self, event: Saving) -> None:
        doc = event.model
        if not isinstance(doc, Doc) or doc.is_new or event.actor.kind == ActorType.SYSTEM:
            return
        prior = self.docs.find(doc.row_id)
        if not prior.is_on_hub() or not doc.is_edited_from(prior):
            return
        if doc.is_mode_changed_from(prior):
            refusal = f"only whoever put doc {prior.id} on the hub or an admin changes who may edit it"
        elif prior.edit_mode == DocEditMode.READ_ONLY:
            refusal = f"doc {prior.id} is read-only on the hub: only whoever put it there or an admin edits it"
        else:
            return
        person = self.person(event.actor)
        if not prior.is_changed_by(person, self.is_admin(person)):
            raise Rejection(refusal)

    def person(self, actor: Actor) -> int:
        return int(actor.id) if self.hosting.is_hosted() and actor.kind == ActorType.USER and actor.id.isdigit() else self.account.user_number()

    def is_admin(self, person: int) -> bool:
        if person == self.account.user_number():
            return self.account.is_admin()
        try:
            return any(member.id == person and member.role == "admin" for member in self.link.people().people)
        except (OSError, TeamRefusal):
            return False
