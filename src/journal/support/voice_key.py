import hashlib

KEY_CHARACTERS = 16


class VoiceKey:
    """The idempotency key of an agent's words stored from its transcript: the kind of words, the session and the words as first recorded, so the same words are stored once however often the transcript is read, and an edit of the stored message never stores them again."""

    @staticmethod
    def create(kind: str, session: str, text: str) -> str:
        return f"{kind}:{session}:{hashlib.sha1(text.encode()).hexdigest()[:KEY_CHARACTERS]}"
