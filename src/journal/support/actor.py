from typing import Callable
from dataclasses import dataclass

from journal.support.actor_type import ActorType

# what joins the session of the agent that sent a subagent to the subagent's own in a subagent's actor
SUBAGENT_SEPARATOR = ":"


@dataclass(frozen=True, eq=False)
class Actor:
    """Who did something: the system, an agent by its session, a user by their id, a plugin by its name, the user's paired phone by its number, an external agent of another project by its name, a worker by its number, or a verifier or a reviewer the journal sent by its number. Stored as one string, kind:id, on every row and every entry."""

    actor_type: ActorType
    id: str = ""

    @classmethod
    def system(cls) -> "Actor":
        return cls.instance(ActorType.SYSTEM, "")

    @classmethod
    def subagent(cls, session: str, subagent_session: str) -> "Actor":
        return cls.instance(ActorType.AGENT, f"{session}{SUBAGENT_SEPARATOR}{subagent_session}")

    @classmethod
    def agent(cls, session: str) -> "Actor":
        return cls.instance(ActorType.AGENT, session)

    @classmethod
    def user(cls, id: int) -> "Actor":
        return cls.instance(ActorType.USER, str(id))

    @classmethod
    def plugin(cls, name: str) -> "Actor":
        return cls.instance(ActorType.PLUGIN, name)

    @classmethod
    def phone(cls, id: int) -> "Actor":
        return cls.instance(ActorType.PHONE, str(id))

    @classmethod
    def external(cls, name: str) -> "Actor":
        return cls.instance(ActorType.EXTERNAL, name)

    @classmethod
    def worker(cls, id: int) -> "Actor":
        return cls.instance(ActorType.WORKER, str(id))

    @classmethod
    def verifier(cls, id: int) -> "Actor":
        return cls.instance(ActorType.VERIFIER, str(id))

    @classmethod
    def reviewer(cls, id: int) -> "Actor":
        return cls.instance(ActorType.REVIEWER, str(id))

    @classmethod
    def parse(cls, stamp: str) -> "Actor":
        type_name, _, id = stamp.partition(":")
        return cls.instance(ActorType(type_name), id)

    @staticmethod
    def instance(actor_type: ActorType, id: str) -> "Actor":
        return next((kind for kind in Actor.__subclasses__() if kind.fits(actor_type, id)), Actor)(actor_type, id)

    @classmethod
    def fits(cls, actor_type: ActorType, id: str) -> bool:
        return actor_type == cls.kind

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

    def can_set_user_options(self) -> bool:
        return False

    def can_approve_plans_alone(self) -> bool:
        return False

    def can_move_worker_tasks(self) -> bool:
        return False

    def can_pair_phone(self) -> bool:
        return False

    def can_disconnect_phone(self) -> bool:
        return False

    def can_manage_plugins(self) -> bool:
        return False

    def is_system_actor(self) -> bool:
        return False

    def is_agent_actor(self) -> bool:
        return False

    def is_same_kind(self, compared: "Actor") -> bool:
        return self.actor_type == compared.actor_type

    def is_person(self) -> bool:
        return False

    def is_reviewer_actor(self) -> bool:
        return False

    def is_subagent_actor(self) -> bool:
        return False

    def desk_person_number(self, default: int) -> int:
        return default

    def person_name(self, name_lookup: Callable[[int], str]) -> str:
        return "someone"

    def chosen_way[T](self, user_way: T, agent_way: T) -> T:
        return agent_way

    def agent_choice[T](self, agent_way: T, person_way: T) -> T:
        return person_way

    def __eq__(self, compared: object) -> bool:
        return isinstance(compared, Actor) and (self.actor_type, self.id) == (compared.actor_type, compared.id)

    def __hash__(self) -> int:
        return hash((self.actor_type, self.id))

    @property
    def stamp(self) -> str:
        return f"{self.actor_type.value}:{self.id}" if self.id else self.actor_type.value

    def is_agent(self) -> bool:
        return self.actor_type == ActorType.AGENT

    def is_desk_user(self) -> bool:
        return self.actor_type == ActorType.USER
