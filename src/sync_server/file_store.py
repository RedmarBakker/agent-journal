import shutil
from pathlib import Path

from sync_server.file_place import TABLES, FilePlace
from sync_server.item_file_place import ItemFilePlace
from sync_server.missing_item import MissingItem
from sync_server.refusal import Refusal

LIMIT_BYTES = 50 * 1024 * 1024


class FileStore:
    """The files attached to the team's rows, stored in the data folder under the row's table, number and the file's name, which are the same on every machine, and the files of the library's item versions; each is written under a draft name and renamed into place, so a reader never finds half a file; a row's files go when it is withdrawn from the team."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def put(self, place: FilePlace | ItemFilePlace, data: bytes) -> int:
        if len(data) > LIMIT_BYTES:
            raise Refusal(f"a file of {len(data) // (1024 * 1024)} MB is over the team server's limit of {LIMIT_BYTES // (1024 * 1024)} MB")
        target = place.checked().folder_path(self.folder)
        target.parent.mkdir(parents=True, exist_ok=True)
        draft = target.with_name(f"{target.name}.part")
        draft.write_bytes(data)
        draft.replace(target)
        return len(data)

    def version_removed(self, item_type: str, name: str, number: int) -> None:
        folder = ItemFilePlace(item_type, name, number, "-").checked().folder_path(self.folder).parent
        if folder.is_dir():
            shutil.rmtree(folder)

    def version_bytes(self, item_type: str, name: str, number: int) -> int:
        folder = ItemFilePlace(item_type, name, number, "-").checked().folder_path(self.folder).parent
        return sum(path.stat().st_size for path in folder.rglob("*") if path.is_file()) if folder.is_dir() else 0

    def is_stored(self, place: ItemFilePlace) -> bool:
        return place.checked().folder_path(self.folder).is_file()

    def removed(self, row_table: str, row: int) -> None:
        if row_table in TABLES and (folder := self.folder / row_table / str(row)).is_dir():
            shutil.rmtree(folder)

    def get(self, place: FilePlace | ItemFilePlace) -> bytes:
        source = place.checked().folder_path(self.folder)
        if not source.is_file():
            raise MissingItem(f"the team server holds no file {source.relative_to(self.folder)}")
        return source.read_bytes()
