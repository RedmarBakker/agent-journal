from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_command_that_names_the_rows_it_made_adds_no_created_line(story):
    story.agent_runs(story.agents.subject, "plan create release --brief 'ship the parser'")
    plan = story.created_number("plan")
    story.expect_command_text_without("created:")
    story.agent_runs(story.agents.subject, f"plan add {plan} 'write the notes'")
    story.expect_command_text(f"added to plan {plan}")
    story.expect_command_text_without("created:")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
