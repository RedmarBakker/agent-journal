import json

from journal.features.organization.support.seat_runtime import SeatRuntime
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
from tests.stories.fixtures.main.organization_hub_plan_with_plan_agents import OrganizationHubPlanWithPlanAgents


class PausedOrganizationHubPlan(OrganizationHubPlanWithPlanAgents):
    """An approved organization plan has a stopped rig with its new seat settings removed."""

    parent = OrganizationHubPlanWithPlanAgents
    settings = ()

    def steps(self, story) -> None:
        story.configure_simulated_openrig()
        runtime = story.app.container.get(SeatRuntime)
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        rig = story.plan_rig_name(self.plans.first)
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
        for pod in spec["pods"]:
            for member in pod["members"]:
                member["env"].pop(ORGANIZATION_SEAT)
                member["env"].pop(ORGANIZATION_RIG)
                if pod["id"] == "alpha" and member["id"] == "domain-agent":
                    agent = member["agent_ref"].removeprefix("local:agents/")
                    agent_folder = runtime.spec_folder(rig) / "agents" / agent
                    profile_path = agent_folder / "agent.yaml"
                    profile = json.loads(profile_path.read_text())
                    profile["profiles"]["default"]["uses"]["skills"].remove("journal-organization-seat-routing")
                    profile["resources"]["skills"] = [
                        skill for skill in profile["resources"]["skills"]
                        if skill["id"] != "journal-organization-seat-routing"
                    ]
                    profile_path.write_text(json.dumps(profile, indent=2) + "\n")
                    (agent_folder / "guidance" / "role.md").write_text("The Domain seat has stale guidance.\n")
                    (agent_folder / "skills" / "journal-organization-seat-routing" / "SKILL.md").write_text("The Domain seat has a stale routing skill.\n")
        spec_path = folder / "rig.yaml"
        spec_path.write_text(json.dumps(spec))
        story.openrig.remember_spec(rig, spec_path)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, CoordinatingPlans)
