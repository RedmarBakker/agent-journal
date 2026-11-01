from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from tests.stories.fixtures.main.organization_task_two_parts_clocked_in import OrganizationTaskTwoPartsClockedIn


class OrganizationPartReturnedUnchecked(OrganizationTaskTwoPartsClockedIn):
    """A Role part has an older unchecked return handoff to the Plan."""

    parent = OrganizationTaskTwoPartsClockedIn

    def steps(self, story) -> None:
        worker = story.agents.workers.second()
        story.agent_proves(worker, 1, "the first maker point is met")
        story.agent_proves(worker, 2, "the second maker point is met")
        story.agent_clocks_out(worker, "both maker points are met").expect_command_passed()
        scope = story.app.container.get(Scope)
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        with scope.environment(plan.environment_id):
            task = story.app.container.get(Tasks).find(self.tasks.second_part)
            story.app.container.get(OrganizationHandoffs).handoff(task, plan, "plan", Actor.system())
