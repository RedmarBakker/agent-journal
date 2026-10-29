import json
from dataclasses import dataclass
from sqlite3 import Row

from sync_server.refusal import Refusal


@dataclass(frozen=True)
class ItemVersion:
    """One numbered version of an item: its body as JSON and that body's hash, the lowest journal version that reads it, the publisher's note, who published it and when, and when the files its body names under files, each with its hash, were all in, 0 until then."""

    id: int
    item_id: int
    number: int
    body: str
    body_hash: str
    lowest_version: str
    note: str
    publisher_id: int
    published_at: float
    completed_at: float

    @classmethod
    def read(cls, row: Row | dict) -> "ItemVersion":
        return cls(row["id"], row["item_id"], row["number"], row["body"], row["body_hash"], row["lowest_version"], row["note"], row["publisher_id"], row["published_at"], row["completed_at"])

    def is_complete(self) -> bool:
        return self.completed_at > 0

    def file_hashes(self) -> dict[str, str]:
        return self.body_file_hashes(self.body)

    @staticmethod
    def body_file_hashes(body: str) -> dict[str, str]:
        try:
            files = json.loads(body).get("files", {})
        except (ValueError, AttributeError) as wrong:
            raise Refusal(f"a version's body is a JSON object, naming its files under files: {wrong}") from wrong
        return {str(name): str(file_hash) for name, file_hash in dict(files).items()}
