from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from journal.support.typed_lines import JOURNAL_PREFIX
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


@story(OrganizationPlanWithDomainSeats, subject=AgentRole.MAIN)
def test_a_message_wakes_the_plan_seat_without_a_supervisor_inbox(story):
    plan = story.plans.first
    story.agent_starts_plan_seat(story.agents.main, plan).expect_allowed(story.agents.main)
    story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview").expect_command_passed()
    story.expect_openrig_seat_environment(story.agents.main, "plan")
    story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {story.tasks.first} domain:alpha",
    ).expect_command_passed()
    story.agent_stops_plan_seat(story.agents.main, plan).expect_allowed(story.agents.main)
    story.agent_uses_its_live_delivery(story.agents.main)

    sent = story.user_sends_message_in(f"plan-{plan}", "continue with the engineering work")
    sent.expect_viewer_passed()
    line = MessagesNudges.NEW_MESSAGE.create(n=sent.viewer_answer["id"]).rendered()
    story.expect_openrig_seat_received(story.agents.main, story.plan_rig_name(plan), "plan", f"{JOURNAL_PREFIX} {line}")
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
