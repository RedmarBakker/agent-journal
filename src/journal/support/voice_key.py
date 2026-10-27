import hashlib

KEY_CHARACTERS = 16


class VoiceKey:
    """The idempotency key of words stored from a source that is read again: the kind of words, the session and the words as first recorded, or the place in a transcript a block was read from, or the key of the hook they came by, none when the hook had none, so they are stored once however often the source is read, and an edit of the stored message never stores them again."""

    @staticmethod
    def create(type_name: str, session: str, text: str) -> str:
        return f"{type_name}:{session}:{hashlib.sha1(text.encode()).hexdigest()[:KEY_CHARACTERS]}"

    @staticmethod
    def placed(session: str, offset: int, index: int) -> str:
        return f"transcript:{session}:{offset}:{index}"

    @staticmethod
    def hooked(type_name: str, hook_key: str) -> str:
        return f"{type_name}:{hook_key}" if hook_key else ""
