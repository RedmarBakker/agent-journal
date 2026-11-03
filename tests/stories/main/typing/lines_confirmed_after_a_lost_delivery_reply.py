from journal.engine.clock import Clock
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.support.agent_role import AgentRole
from journal.support.typed_lines import JOURNAL_PREFIX
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.restarted_idle_main_with_organization_seats import RestartedIdleMainWithOrganizationSeats


@story(RestartedIdleMainWithOrganizationSeats, subject=AgentRole.MAIN)
def test_a_prompt_confirms_a_line_after_its_delivery_reply_is_lost(story):
    story.agent_supervisor_loses_the_reply_after_delivering_a_line(story.agents.subject)
    message = story.user_sends_message("please continue once")
    nudge = MessagesNudges.NEW_MESSAGE.create(n=message)
    line = f"{JOURNAL_PREFIX} {nudge.rendered()}"

    story.expect_supervisor_received(story.agents.subject, MessagesNudges.NEW_MESSAGE, count=1, n=message)
    story.agent_is_prompted(story.agents.subject, line)
    story.clock_ticks(Clock.interval_seconds)

    story.expect_supervisor_received(story.agents.subject, MessagesNudges.NEW_MESSAGE, count=1, n=message)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
