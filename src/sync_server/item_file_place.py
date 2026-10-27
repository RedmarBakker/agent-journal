from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from sync_server.refusal import Refusal

ITEMS_FOLDER = "items"


@dataclass(frozen=True)
class ItemFilePlace:
    """Where a file of an item's version is kept: under the item's type, name and version number, by the path its body names, which may hold folders of its own but never leaves the version's folder."""

    item_type: str
    name: str
    number: int
    file_name: str

    def checked(self) -> "ItemFilePlace":
        file_path = PurePosixPath(self.file_name)
        segments_valid = all(Path(part).name == part and part not in ("", ".", "..") for part in (self.item_type, self.name))
        if not segments_valid or not self.file_name or "\\" in self.file_name or self.file_name.split("/") != list(file_path.parts) or any(part in (".", "..") for part in file_path.parts):
            raise Refusal(f"no such item file: {self.item_type}/{self.name}/{self.number}/{self.file_name}")
        return self

    def folder_path(self, folder: Path) -> Path:
        return folder / ITEMS_FOLDER / self.item_type / self.name / str(self.number) / self.file_name
