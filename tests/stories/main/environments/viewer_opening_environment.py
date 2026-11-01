from journal.engine.states.ended import Ended
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.ended_session import EndedSession


@setting(PlansOptions.PLAN_AGENTS, True)
@story(EndedSession, subject=AgentRole.MAIN)
def test_a_fresh_manifest_keeps_opening_on_the_latest_user_session_as_plan_agents_tick(story):
    story.monkeypatch.setattr(AgentEnvironments, "launched", lambda places, environment, agent, repositories=(): None)
    plans = []
    for number in range(3):
        plan = story.user_creates_plan(f"plan {number}", f"Finish plan {number}")
        story.user_adds_plan_task(plan, f"task {number}")
        story.user_approves_plan(plan).expect_viewer_passed()
        story.user_starts_plan(plan).expect_viewer_passed()
        plans.append(plan)

    story.another_environment("smoke-3")
    story.session_starts_in("smoke-3", "smoke-session")
    for number, plan in enumerate(plans):
        story.session_starts_in(f"plan-{plan}", f"plan-agent-{number}")
    for _ in range(3):
        story.clock_ticks(5)
        result = story.user_opens("/journal/manifest")
        result.expect_viewer_shows("environment", "smoke-3")

    story.expect_stack(story.agents.subject, Ready, Ended)


@story(EndedSession, subject=AgentRole.MAIN)
def test_a_fresh_manifest_opens_main_when_no_user_session_is_running(story):
    result = story.user_opens("/journal/manifest")
    result.expect_viewer_shows("environment", "main")
    story.expect_stack(story.agents.subject, Ready, Ended)
