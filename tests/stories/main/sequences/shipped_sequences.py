from journal.features.sequences.shipped import PLAN_BUILDING
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_shipped_sequence_an_older_journal_wrote_is_brought_to_what_this_journal_ships_at_its_next_start(story):
    story.an_older_journal_wrote_the_sequence(PLAN_BUILDING.title, PLAN_BUILDING.steps[:1])
    story.journal_starts_again()
    result = story.user_types(f"sequence show {story.sequence_number(PLAN_BUILDING.title)}")
    result.expect_command_text(PLAN_BUILDING.steps[-1].title)
    story.expect_stack(story.agents.subject, Ready)
