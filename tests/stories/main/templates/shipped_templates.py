from journal.features.tasks.states.ready import Ready
from journal.features.templates.shipped import PLAN_SCOPED_TESTS
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

OLDER_BRIEF = "Run the tests of each task when it is done."


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_shipped_template_an_older_journal_wrote_is_brought_to_what_this_journal_ships_at_its_next_start(story):
    story.an_older_journal_wrote_the_template(PLAN_SCOPED_TESTS.title, OLDER_BRIEF)
    story.journal_starts_again()
    result = story.user_types(f"template show {story.template_number(PLAN_SCOPED_TESTS.title)}")
    result.expect_command_text(PLAN_SCOPED_TESTS.brief)
    result.expect_command_text_without(OLDER_BRIEF)
    story.expect_stack(story.agents.subject, Ready)
