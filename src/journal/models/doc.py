from dataclasses import dataclass
from typing import ClassVar

from journal.models.doc_edit_mode import DocEditMode
from journal.models.scoped import Scoped
from journal.support.no_action_reason import NoActionReason


@dataclass(frozen=True)
class Doc(Scoped):
    """A document of one environment, read in every environment when it is the project's (environment 0) or a hub's: a title, a line that says what it is, its text, whether it is still being written in parts or ready, and why it needs no action once it is signed off as such."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "abstract", "body")

    title: str = ""
    abstract: str = ""
    body: str = ""
    edit_mode: DocEditMode = DocEditMode.LOCAL
    owner: int = 0
    settled_reason: str = ""
    unfinished: bool = False
    is_copy: bool = False

    def writing_status(self) -> str:
        return "Being written" if self.unfinished else "Ready"

    def finished(self) -> "Doc":
        return self.with_(unfinished=False)

    def with_no_action_needed(self, reason: str) -> "Doc":
        return self.with_(settled_reason=NoActionReason.checked(self, reason))

    def is_on_hub(self) -> bool:
        return self.edit_mode != DocEditMode.LOCAL

    def put_on_hub(self, hub_id: int, mode: DocEditMode, owner: int) -> "Doc":
        return self.with_(environment_id=hub_id, edit_mode=mode, owner=owner)

    def local_copy(self) -> "Doc":
        return Doc(title=self.title, abstract=self.abstract, body=self.body, is_copy=True)

    def taken_back(self, environment_id: int) -> "Doc":
        return self.with_(environment_id=environment_id, edit_mode=DocEditMode.LOCAL, owner=0)

    def is_withheld(self) -> bool:
        return self.is_copy

    def is_edited_from(self, prior: "Doc") -> bool:
        return (self.title, self.abstract, self.body, self.edit_mode, self.owner, self.environment_id) != (prior.title, prior.abstract, prior.body, prior.edit_mode, prior.owner, prior.environment_id)

    def is_mode_changed_from(self, prior: "Doc") -> bool:
        return (self.edit_mode, self.owner, self.environment_id) != (prior.edit_mode, prior.owner, prior.environment_id)

    def is_changed_by(self, member: int, is_admin: bool) -> bool:
        return is_admin or member == self.owner

    def title_words(self) -> str:
        return self.title

    def summary_line(self) -> str:
        return self.abstract or self.opening_line(self.body)
