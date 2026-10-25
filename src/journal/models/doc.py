from dataclasses import dataclass
from typing import ClassVar

from journal.models.doc_edit_mode import DocEditMode
from journal.models.scoped import Scoped


@dataclass(frozen=True)
class Doc(Scoped):
    """A document of one environment, read in every environment when it is the project's (environment 0) or a hub's: a title, a line that says what it is, and its text."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "abstract", "body")

    title: str = ""
    abstract: str = ""
    body: str = ""
    edit_mode: DocEditMode = DocEditMode.LOCAL
    owner: int = 0
    is_copy: bool = False

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
