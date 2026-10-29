from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class PhoneActor(Actor):
    """The user's paired phone, by its number."""

    kind: ClassVar[ActorType] = ActorType.PHONE

    def can_set_user_options(self) -> bool:
        return True

    def can_approve_plans_alone(self) -> bool:
        return True

    def can_move_worker_tasks(self) -> bool:
        return True

    def can_read_comments(self) -> bool:
        return True
