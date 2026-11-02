"""Viewer delivery through an in-process Unix supervisor socket, without an agent process."""

from journal.engine.clock import Clock
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from journal.support.typed_lines import JOURNAL_PREFIX
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.restarted_idle_main_with_organization_seats import RestartedIdleMainWithOrganizationSeats


@story(RestartedIdleMainWithOrganizationSeats, subject=AgentRole.MAIN)
def test_an_idle_main_agent_gets_a_viewer_message_after_restart_when_an_unrelated_seat_has_no_native_session(story):
    message = story.user_sends_message("please check the plan again")

    story.expect_supervisor_received(story.agents.subject, MessagesNudges.NEW_MESSAGE, n=message)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(RestartedIdleMainWithOrganizationSeats, subject=AgentRole.MAIN)
def test_a_refused_viewer_message_retries_on_the_clock_without_an_idle_agents_hook(story):
    story.agent_supervisor_refuses_lines(story.agents.subject)
    message = story.user_sends_message("please resume once the terminal is ready")
    nudge = MessagesNudges.NEW_MESSAGE.create(n=message)
    story.expect_line_is_unsent(story.agents.subject, f"{JOURNAL_PREFIX} {nudge.rendered()}")
    story.expect_supervisor_received(story.agents.subject, MessagesNudges.NEW_MESSAGE, count=0, n=message)

    story.agent_supervisor_is_ready(story.agents.subject)
    story.clock_ticks(Clock.interval_seconds)

    story.expect_supervisor_received(story.agents.subject, MessagesNudges.NEW_MESSAGE, n=message)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
