from journal.engine.clock import Clock
from journal.engine.states.ended import Ended
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.plan_state import PlanState
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.ended_session import EndedSession
from tests.stories.fixtures.main.solo_plan_agent_started import SoloPlanAgentStarted


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_a_compaction_start_keeps_a_live_launched_environment_open_after_a_later_session_ends_while_plan_agents_tick(story):
    story.another_environment("smoke-3")
    story.time_travel(seconds=Clock.interval_seconds)
    story.session_starts_in("smoke-3", "smoke-session", source="compact").expect_allowed()
    story.another_environment("retired")
    story.time_travel(seconds=Clock.interval_seconds)
    story.session_starts_in("retired", "retired-session").expect_allowed()
    story.session_ends_in("retired", "retired-session").expect_allowed()
    for _ in range(3):
        story.clock_ticks(Clock.interval_seconds)
        result = story.user_opens("/journal/manifest")
        result.expect_viewer_shows("environment", "smoke-3")

    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(EndedSession, subject=AgentRole.MAIN)
def test_a_fresh_manifest_opens_main_when_no_user_session_is_running(story):
    result = story.user_opens("/journal/manifest")
    result.expect_viewer_shows("environment", "main")
    story.expect_stack(story.agents.subject, Ready, Ended)
