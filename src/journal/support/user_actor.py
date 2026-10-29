from typing import Callable, ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class UserActor(Actor):
    """A user, by their account number."""

    kind: ClassVar[ActorType] = ActorType.USER

    def can_set_user_options(self) -> bool:
        return True

    def can_approve_plans_alone(self) -> bool:
        return True

    def can_move_worker_tasks(self) -> bool:
        return True

    def can_pair_phone(self) -> bool:
        return True

    def can_disconnect_phone(self) -> bool:
        return True

    def can_manage_plugins(self) -> bool:
        return True

    def chosen_way[T](self, user_way: T, agent_way: T) -> T:
        return user_way

    def desk_person_number(self, default: int) -> int:
        return int(self.id) if self.id.isdigit() else default

    def person_name(self, name_lookup: Callable[[int], str]) -> str:
        return name_lookup(int(self.id))

    def is_person(self) -> bool:
        return True
