import json

from journal.features.organization.support.rig_seats import PLAN_AGENT, PLAN_POD
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.plan_state import PlanState
from journal.models.rig import Rig
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.rigs import Rigs
from journal.support.caller import ORGANIZATION_RIG, ORGANIZATION_SEAT
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from tests.lab.simulated_seats import SimulatedSeats
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class PausedOrganizationHubPlan(OrganizationHubPlan):
    """An approved organization plan has a stopped rig with its new seat settings removed."""

    settings = (*OrganizationHubPlan.settings, (PlansOptions.PLAN_AGENTS, True))

    def steps(self, story) -> None:
        super().steps(story)
        story.openrig = SimulatedSeats()
        runtime = story.app.container.get(SeatRuntime)
        story.monkeypatch.setattr(runtime, "execute", story.openrig.execute)
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        rig = f"plan-{self.plans.first}"
        with story.app.container.get(Scope).environment(1):
            plans = story.app.container.get(Plans)
            plan = plans.find(self.plans.first)
            rig_row = story.app.container.get(Rigs).save(Rig(environment_id=plan.environment_id, name=rig), Actor.system())
            plans.rig_linked(plan, rig_row, Actor.system())
            environment = story.app.container.get(Environments).find(plan.environment_id)
            story.app.container.get(PlanAgents).prepared(plan, environment, plan.environment_id, Actor.system())
        story.openrig.rigs.add(rig)
        story.agent_runs(story.agents.main, f"plan pause {self.plans.first}").expect_command_passed()
        folder = runtime.spec_folder(rig)
        (folder / "saved-conversation.json").write_text("previous conversation")
        spec = runtime.read_spec(rig)
        plan = next(pod for pod in spec["pods"] if pod["id"] == PLAN_POD)
        member = next(member for member in plan["members"] if member["id"] == PLAN_AGENT)
        member["env"].pop(ORGANIZATION_SEAT)
        member["env"].pop(ORGANIZATION_RIG)
        spec_path = folder / "rig.yaml"
        spec_path.write_text(json.dumps(spec))
        story.openrig.remember_spec(rig, spec_path)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, CoordinatingPlans)
