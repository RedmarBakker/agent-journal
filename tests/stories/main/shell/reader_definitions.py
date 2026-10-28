from journal.features.shell.support.activity_title import TITLE_RULE
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_readers_label_ending_half_a_sentence_is_refused_with_the_rule(story):
    story.agent_runs("reader add go-packages --pattern ok --about 'a go test run' --label 'Running the tests of'")
    story.expect_command_refused()
    story.expect_command_text(TITLE_RULE)
    story.expect_command_text("stops on 'of'")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reader_the_journal_ships_cannot_be_replaced(story):
    story.agent_runs("reader add pytest --about mine --pattern .")
    story.expect_command_text("locked")
    story.agent_runs("reader list")
    story.expect_command_line("pytest", "(locked)")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reader_the_journal_ships_cannot_be_removed(story):
    story.agent_runs("reader remove worker-merge")
    story.expect_command_text("locked")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reader_for_a_search_alone_is_refused(story):
    story.agent_runs("reader add greps --about 'a search' --pattern . --commands grep")
    story.expect_command_refused()
    story.expect_command_text("gets no reader")
    story.expect_stack(Ready)
