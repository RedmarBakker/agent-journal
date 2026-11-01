from journal.features.shell.support.activity_title import TITLE_RULE
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_readers_label_ending_half_a_sentence_is_refused_with_the_rule(story):
    result = story.agent_runs(story.agents.subject, "reader add go-packages --pattern ok --about 'a go test run' --label 'Running the tests of'")
    result.expect_command_refused()
    result.expect_command_text(TITLE_RULE)
    result.expect_command_text("stops on 'of'")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_reader_the_journal_ships_cannot_be_replaced(story):
    result = story.agent_runs(story.agents.subject, "reader add pytest --about mine --pattern .")
    result.expect_command_text("locked")
    result = story.agent_runs(story.agents.subject, "reader list")
    result.expect_command_line("pytest", "(locked)")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_reader_the_journal_ships_cannot_be_removed(story):
    result = story.agent_runs(story.agents.subject, "reader remove worker-merge")
    result.expect_command_text("locked")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_reader_for_a_search_alone_is_refused(story):
    result = story.agent_runs(story.agents.subject, "reader add greps --about 'a search' --pattern . --commands grep")
    result.expect_command_refused()
    result.expect_command_text("gets no reader")
    story.expect_stack(story.agents.subject, Ready)
