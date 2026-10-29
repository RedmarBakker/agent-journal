from journal.features.organization.support.role import Role
from journal.features.organization.support.role_instances import RoleInstances
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.rejection import Rejection


class RoleQueue:
    """A step a solo plan cannot take on, since every plan shares its Role, handed to that Role's one instance: the step's task let go by the agent and put in the instance's queue, refused while no instance runs."""

    def __init__(self, instances: RoleInstances, tasks: Tasks) -> None:
        self.instances, self.tasks = instances, tasks

    def queued(self, role: Role, task: Task, holder: Ref | None, actor: Actor) -> Worker:
        instance = self.instances.existing(role, task)
        if instance is None:
            raise Rejection(f"no instance of {role.title} runs yet: the main agent starts it with journal worker dispatch --role {role.id}")
        self.tasks.drop_holder(task, holder, actor)
        self.tasks.queued(task, Ref.build(instance), actor)
        return instance
