from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from journal.providers.claude import Claude
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.task_takeover import TaskTakeover


@story(TaskTakeover, subject=AgentRole.MAIN)
def test_the_session_that_took_over_reads_the_overview_before_it_writes(story):
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, BriefingNudges.OVERVIEW_REQUEST)
    story.agent_looks_at_the_overview(story.agents.subject)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_session_of_the_other_provider_takes_over_too(story):
    story.other_provider_session_starts()
    story.expect_agent_session(story.main_session())
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, subject=AgentRole.MAIN)
def test_a_takeover_keeps_the_followed_plan_in_hand(story):
    story.second_session_starts()
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(BuildWait, subject=AgentRole.MAIN)
def test_a_takeover_while_the_agent_waits_keeps_the_wait(story):
    story.second_session_starts()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_late_hook_of_the_session_taken_over_leaves_the_environment_with_the_new_one(story):
    first = story.main_session()
    story.second_session_starts()
    result = story.replaced_session_stops(first)
    result.expect_allowed()
    story.expect_agent_session(story.main_session())
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
@provider(Claude)
def test_a_session_of_the_other_provider_shows_none_of_the_status_the_first_session_reported(story):
    story.status_line_reports()
    story.expect_agent_bar_reported()
    story.other_provider_session_starts()
    story.expect_agent_bar_empty()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
