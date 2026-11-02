from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.delivery.listeners.line_retyping import WAIT_LIMIT_SECONDS
from journal.support.agent_role import AgentRole
from journal.support.typed_lines import JOURNAL_PREFIX
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_another_current_agent import OrganizationPlanWithAnotherCurrentAgent
from tests.stories.fixtures.main.idle_organization_plan_seat import IdleOrganizationPlanSeat


@story(OrganizationPlanWithAnotherCurrentAgent, subject=AgentRole.MAIN)
def test_a_line_from_the_agent_bar_reaches_its_target_seat_when_another_agent_is_current(story):
    story.agent_uses_its_live_delivery(story.agents.main)
    result = story.user_types_to_agent(story.agents.main, "continue with the selected plan")
    result.expect_viewer_passed()
    story.expect_openrig_seat_received(story.agents.main, story.plan_rig_name(story.plans.first), "plan", "continue with the selected plan")
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(OrganizationPlanWithAnotherCurrentAgent, subject=AgentRole.MAIN)
def test_a_journal_line_from_a_seats_own_hook_keeps_its_target_when_another_agent_is_current(story):
    story.agent_uses_its_live_delivery(story.agents.main)
    story.agent_closes_its_turn(story.agents.main, "👍").expect_allowed(story.agents.main)
    line = MessagesNudges.EMOJI_REPLY.create(emoji="👍").rendered()
    story.expect_openrig_seat_received(story.agents.main, story.plan_rig_name(story.plans.first), "plan", f"{JOURNAL_PREFIX} {line}")
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(IdleOrganizationPlanSeat, subject=AgentRole.MAIN)
def test_a_retry_after_the_seats_session_is_lost_keeps_the_line_unsent_instead_of_claiming_it_was_typed(story):
    story.agent_uses_its_live_delivery(story.agents.main)
    sent = story.user_sends_message_in(f"plan-{story.plans.first}", "continue after the seat returns")
    sent.expect_viewer_passed()
    line = f"{JOURNAL_PREFIX} {MessagesNudges.NEW_MESSAGE.create(n=sent.viewer_answer['id']).rendered()}"
    story.expect_openrig_seat_received(story.agents.main, story.plan_rig_name(story.plans.first), "plan", line)
    story.agent_loses_its_organization_session(story.agents.main, "plan")
    story.clock_ticks(WAIT_LIMIT_SECONDS * 2 + 1)
    story.expect_line_is_unsent(story.agents.main, line)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
