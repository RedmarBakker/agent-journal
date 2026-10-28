from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

TOP_USAGE = "usage: journal [-h]"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_verb_that_does_not_exist_is_answered_with_the_nouns_own_usage_once(story):
    story.agent_runs("task nope")
    story.expect_command_refused()
    story.expect_command_text("usage: journal task")
    story.expect_command_text_without(TOP_USAGE)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_nouns_help_lists_its_verbs_and_is_no_failure(story):
    story.agent_runs("plan --help")
    story.expect_command_passed()
    story.expect_command_text("approve")
    story.expect_command_text_without(TOP_USAGE)
    story.agent_runs("setup --help")
    story.expect_command_text("restart")
    story.expect_command_text("project")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_every_row_noun_has_the_dock_verbs_and_a_noun_that_is_no_row_has_not(story):
    story.agent_runs("report --help")
    story.expect_command_text("dock")
    story.agent_runs("search --help")
    story.expect_command_text_without("dock")
    story.expect_stack(Ready)
