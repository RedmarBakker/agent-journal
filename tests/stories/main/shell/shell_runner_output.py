from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

FAILING_CODE = 3


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_long_output_is_kept_and_only_named_by_its_number(story):
    output = story.agent_runs_a_command(f"python3 -c \"print('x' * {story.setting(ShellOptions.COMMAND_SHOWN) + 1})\"")
    story.expect_new_output()
    story.expect_agent_told(ShellNudges.OUTPUT_STORED, n=output)
    story.expect_shell_text_without("x" * story.setting(ShellOptions.COMMAND_SHOWN))
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(ShellOptions.READ_SHOWN, 100)
def test_a_reading_command_past_its_read_characters_is_shown_by_its_two_ends(story):
    lines = story.setting(ShellOptions.READ_SHOWN)
    story.agent_runs_a_command(f"cat {story.project_file('long.txt', lines)}")
    story.expect_shell_text("line 0", f"line {lines - 1}")
    story.expect_shell_text_without(f"line {lines // 2}\n")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(ShellOptions.OUTPUT_COUNT, 2)
def test_only_the_newest_outputs_are_kept_past_the_count(story):
    for _ in range(story.setting(ShellOptions.OUTPUT_COUNT) + 1):
        story.agent_runs_a_command("echo hi | head -1")
    story.expect_output_count(story.setting(ShellOptions.OUTPUT_COUNT))
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_kept_output_is_read_by_its_number_with_a_part_named(story):
    output = story.agent_runs_a_command("echo hi | head -1")
    story.agent_runs(f"output read {output} --all")
    story.expect_command_passed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_kept_output_read_with_no_part_named_is_refused(story):
    output = story.agent_runs_a_command("echo hi | head -1")
    story.agent_runs(f"output read {output}")
    story.expect_command_refused()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_status_of_a_kept_output_says_how_it_ended(story):
    output = story.agent_runs_a_command("echo hi | head -1")
    story.agent_runs(f"output status {output}")
    story.expect_command_passed()
    story.expect_command_text("finished")
    story.expect_stack(Ready)
