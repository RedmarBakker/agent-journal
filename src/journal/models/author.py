from enum import StrEnum

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class Author(StrEnum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    COLLEAGUE = "colleague"

    @classmethod
    def build(cls, actor: Actor) -> "Author":
        return {ActorType.AGENT: cls.AGENT, ActorType.USER: cls.USER, ActorType.PHONE: cls.USER}.get(actor.actor_type, cls.SYSTEM)
