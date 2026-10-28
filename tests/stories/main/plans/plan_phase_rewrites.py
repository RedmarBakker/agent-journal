from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plans_phase_is_retitled_and_its_complete_when_line_written_anew(story):
    plan = story.agent_creates_plan("release", "ship it")
    story.agent_runs(f"plan phase {plan} 'Build it' --when 'it builds'")
    story.agent_runs(f"plan rephase {plan} 1 --title 'Build and prove it' --when 'it builds and the suite is green'")
    story.expect_command_text(f"phase 1 of plan {plan} is now: Build and prove it")
    story.agent_runs(f"plan show {plan}")
    story.expect_command_text("it builds and the suite is green")
    story.expect_stack(Ready, FollowingSequence)
