from pathlib import Path

from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.agent_token import AgentToken
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.organization_plan_handoff_seat import OrganizationPlanHandoffSeat


@story(OrganizationPlanHandoffSeat, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_restarting_an_organization_plan_reads_only_its_own_environment_handoffs(story):
    first_plan, first_task = story.plans.first, story.tasks.first
    first_plan_seat = story.organization_seat_agent_in_plan("plan", first_plan)
    story.agent_runs_as_organization_seat_in_plan(
        first_plan_seat, "plan", first_plan, f"organization handoff {first_task} domain:alpha",
    ).expect_command_passed()
    first_domain = story.organization_seat_agent_in_plan("domain:alpha", first_plan)
    story.agent_starts_organization_seat_in_plan(first_domain, "domain:alpha", first_plan).expect_allowed(first_domain)
    story.agent_runs_as_organization_seat_in_plan(
        first_domain, "domain:alpha", first_plan, "organization inbox",
    ).expect_command_passed()
    story.user_pauses_plan(first_plan).expect_viewer_passed()

    other = story.another_environment("other-organization")
    folder = Path(__file__).resolve().parents[3] / "stories" / "fixtures" / "main" / "organization_hub"
    story.user_presses_in(other, "/journal/settings", {
        "plans": {"plan_agents": True}, "workers": {"organization_folder": str(folder)},
    }).expect_viewer_passed()
    story.user_presses_in(other, "/journal/organization/reload", {}).expect_viewer_passed()
    story.plans.second = story.user_creates_plan_in(other, "the other organization plan")
    second_plan = story.plans.second
    task = story.user_presses_in(other, f"/journal/plans/{second_plan}/tasks", {
        "title": "the other task", "brief": "- the other task is complete", "domain": "alpha",
    })
    task.expect_viewer_passed()
    story.tasks.second = task.viewer_answer["id"]
    second_task = story.tasks.second
    story.session_starts_in(other, "other-organization-main")
    other_main = StoryAgent(AgentRole.MAIN, session="other-organization-main")
    story.agent_in_runs(other_main, other, "other-organization-main", f"plan mode {second_plan} organization").expect_command_passed()
    story.user_presses_in(other, f"/journal/plans/{second_plan}/approve", {}).expect_viewer_passed()

    second_environment = story.app.container.get(Environments).existing(other)
    with story.app.container.get(Scope).environment(second_environment.row_id):
        contracts = story.app.container.get(Organization).reload()
        provider = story.app.container.get(Providers).lookup(story.provider)
        domains = tuple(domain.id for domain in contracts.domains)
        rig = story.plan_rig_name(second_plan)
        story.app.container.get(RigSpecs).write(
            rig, contracts, domains, story.app.config.root,
            lambda seat: SeatWorker(Actor.agent(""), AgentToken(f"story-seat-{rig}-{seat.qualified}"),
                                   f"plan-{second_plan}", seat.qualified, rig),
            provider,
        )
    story.user_presses_in(other, f"/journal/plans/{second_plan}/start", {}).expect_viewer_passed()
    second_plan_seat = story.organization_seat_agent_in_plan("plan", second_plan)
    story.agent_starts_organization_seat_in_plan(second_plan_seat, "plan", second_plan).expect_allowed(second_plan_seat)
    story.agent_runs_as_organization_seat_in_plan(
        second_plan_seat, "plan", second_plan, f"organization handoff {second_task} domain:alpha",
    ).expect_command_passed()
    second_domain = story.organization_seat_agent_in_plan("domain:alpha", second_plan)
    story.agent_starts_organization_seat_in_plan(second_domain, "domain:alpha", second_plan).expect_agent_told(
        second_domain, OrganizationNudges.UNREAD_HANDOFF,
    )
    story.agent_runs_as_organization_seat_in_plan(
        second_domain, "domain:alpha", second_plan, "organization inbox",
    ).expect_command_passed()

    restarted = story.user_starts_plan(first_plan)
    restarted.expect_viewer_passed()
    story.expect_organization_handoff_pending(first_plan, first_task, "domain:alpha")
    story.expect_organization_handoffs_read(second_plan, "domain:alpha")
    story.agent_starts_plan_seat(story.agents.subject, first_plan).expect_allowed(story.agents.subject)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)
