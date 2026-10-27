import hashlib
import json


class PortableBody:
    """The text an item travels as: its fields as JSON with sorted keys and nothing a machine writes for itself, so the same item is the same text on every machine, and the one hash of that text."""

    @staticmethod
    def text(fields: dict) -> str:
        return json.dumps(fields, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def fields(text: str) -> dict:
        return dict(json.loads(text))

    @staticmethod
    def hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
