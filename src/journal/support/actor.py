from dataclasses import dataclass

from journal.support.actor_type import ActorType

# what joins the session of the agent that sent a subagent to the subagent's own in a subagent's actor
SUBAGENT_SEPARATOR = ":"


@dataclass(frozen=True)
class Actor:
    """Who did something: the system, an agent by its session, a user by their id, a plugin by its name, the user's paired phone by its number, an external agent of another project by its name, a worker by its number, or a verifier or a reviewer the journal sent by its number. Stored as one string, kind:id, on every row and every entry."""

    actor_type: ActorType
    id: str = ""

    @classmethod
    def system(cls) -> "Actor":
        return cls(ActorType.SYSTEM)

    @classmethod
    def subagent(cls, session: str, subagent_session: str) -> "Actor":
        return cls(ActorType.AGENT, f"{session}{SUBAGENT_SEPARATOR}{subagent_session}")

    @classmethod
    def agent(cls, session: str) -> "Actor":
        return cls(ActorType.AGENT, session)

    @classmethod
    def user(cls, id: int) -> "Actor":
        return cls(ActorType.USER, str(id))

    @classmethod
    def plugin(cls, name: str) -> "Actor":
        return cls(ActorType.PLUGIN, name)

    @classmethod
    def phone(cls, id: int) -> "Actor":
        return cls(ActorType.PHONE, str(id))

    @classmethod
    def external(cls, name: str) -> "Actor":
        return cls(ActorType.EXTERNAL, name)

    @classmethod
    def worker(cls, id: int) -> "Actor":
        return cls(ActorType.WORKER, str(id))

    @classmethod
    def verifier(cls, id: int) -> "Actor":
        return cls(ActorType.VERIFIER, str(id))

    @classmethod
    def reviewer(cls, id: int) -> "Actor":
        return cls(ActorType.REVIEWER, str(id))

    @classmethod
    def parse(cls, stamp: str) -> "Actor":
        type_name, _, id = stamp.partition(":")
        return cls(ActorType(type_name), id)

    @staticmethod
    def stamp_number(stamp: str, type_name: ActorType) -> int | None:
        prefix, colon, number = stamp.partition(":")
        if prefix != type_name.value or not colon:
            return None
        return int(number) if number.isdigit() else 0

    @property
    def lookup(self) -> str:
        return {ActorType.SYSTEM: "the journal", ActorType.AGENT: "the agent", ActorType.USER: "you", ActorType.PHONE: "you, from your phone", ActorType.EXTERNAL: self.id, ActorType.WORKER: f"worker {self.id}", ActorType.VERIFIER: f"verifier {self.id}", ActorType.REVIEWER: f"reviewer {self.id}"}.get(self.actor_type, f"plugin {self.id}")

    def is_user(self) -> bool:
        return self.actor_type in (ActorType.USER, ActorType.PHONE)

    def number(self) -> int:
        return int(self.id)

    def agent_session(self) -> str | None:
        return self.id.partition(SUBAGENT_SEPARATOR)[0] if self.is_agent() else None

    def is_subagent(self) -> bool:
        return self.is_agent() and SUBAGENT_SEPARATOR in self.id

    @property
    def stamp(self) -> str:
        return f"{self.actor_type.value}:{self.id}" if self.id else self.actor_type.value

    def is_agent(self) -> bool:
        return self.actor_type == ActorType.AGENT

    def is_desk_user(self) -> bool:
        return self.actor_type == ActorType.USER
