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

    def is_on_hub(self) -> bool:
        return self.edit_mode != DocEditMode.LOCAL

    def put_on_hub(self, hub_id: int, mode: DocEditMode, owner: int) -> "Doc":
        return self.with_(environment_id=hub_id, edit_mode=mode, owner=owner)

    def copy_on_hub(self, hub_id: int, mode: DocEditMode, owner: int) -> "Doc":
        return Doc(environment_id=hub_id, title=self.title, abstract=self.abstract, body=self.body, edit_mode=mode, owner=owner)

    def is_changed_by(self, member: int, is_admin: bool) -> bool:
        return is_admin or member == self.owner

    def title_words(self) -> str:
        return self.title

    def summary_line(self) -> str:
        return self.abstract or self.opening_line(self.body)
