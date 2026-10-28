from journal.features.shell.shell_conduct import READ_LIMIT_FACTOR
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(ShellOptions.SHOWN, 10)
def test_a_whole_read_of_a_file_longer_than_the_shown_lines_allow_is_refused(story):
    longest = READ_LIMIT_FACTOR * story.setting(ShellOptions.SHOWN)
    story.agent_reads(story.project_file("long.txt", longest + 1))
    story.expect_refused(ShellNudges.PARTIAL_FILE_READ, lines=longest + 1, cap=story.setting(ShellOptions.SHOWN))
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(ShellOptions.SHOWN, 10)
def test_a_whole_read_of_a_file_exactly_as_long_as_allowed_goes_through(story):
    story.agent_reads(story.project_file("long.txt", READ_LIMIT_FACTOR * story.setting(ShellOptions.SHOWN)))
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(ShellOptions.SHOWN, 10)
def test_a_part_read_of_a_long_file_goes_through(story):
    longest = READ_LIMIT_FACTOR * story.setting(ShellOptions.SHOWN)
    story.agent_reads_part(story.project_file("long.txt", longest + 1), story.setting(ShellOptions.SHOWN))
    story.expect_allowed()
    story.expect_stack(Ready)
