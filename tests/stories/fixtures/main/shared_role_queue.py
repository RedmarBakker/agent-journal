from pathlib import Path

from journal.engine.states_catalogue import StatesCatalogue
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.plans.plans_options import PlansOptions
from tests.stories.fixtures.main.working_agent import WorkingAgent


def awaiting_state(story):
    return story.app.container.get(StatesCatalogue).restored("awaiting", {})


class SharedRoleQueue(WorkingAgent):
    """A journal-cardinality builder holds one task from the first plan while three tasks from two plans wait in its queue."""

    stack = (CoordinatingPlans,)
    settings = (
        (OrganizationOptions.FOLDER, str(Path(__file__).with_name("shared_role_queue"))),
        (PlansOptions.PLAN_AGENTS, True),
    )

    def steps(self, story) -> None:
        super().steps(story)
        story.configure_simulated_openrig()
        self.plans.first = story.user_creates_plan("Alpha delivery", "Complete the first alpha plan")
        self.tasks.active = story.user_adds_plan_task(self.plans.first, "Active task")
        self.tasks.first_queued = story.user_adds_plan_task(self.plans.first, "First queued task")
        self.tasks.second_queued = story.user_adds_plan_task(self.plans.first, "Second queued task")
        self.plans.second = story.user_creates_plan("Beta delivery", "Complete the second plan")
        self.tasks.other_plan = story.user_adds_plan_task(self.plans.second, "Other plan task")
        for plan in (self.plans.first, self.plans.second):
            story.agent_runs(story.agents.main, f"plan mode {plan} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        story.user_approves_plan(self.plans.second)
        result = story.agent_runs(
            story.agents.main,
            f"worker dispatch 'Mary Jackson' --task {self.tasks.active} --changes 'the files of its task' --tests 'Scoped tests' --role builder",
        )
        result.expect_command_passed()
        self.workers.first = story.newest("workers")
        story.agent_starts_a_session(story.agents.workers.first())
        story.agent_clocks_in(story.agents.workers.first())

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, CoordinatingPlans, awaiting_state(story))
