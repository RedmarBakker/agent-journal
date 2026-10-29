from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
def test_the_line_that_an_awaited_output_ended_carries_what_its_reader_picks(story):
    story.agent_runs(story.agents.subject, "reader add summary-lines --pattern '[0-9]+ (passed|failed)' --about 'the summary of a test run'")
    output = story.agent_runs_a_command(story.agents.subject, f"sh -c 'sleep {story.setting(FOREGROUND_OPTION) * 2}; echo FAILED tests/a.py::test_b; echo 1 failed, 3 passed; exit 1'")
    story.agent_runs(story.agents.subject, f"await 'the tests' --output {output} --reader summary-lines")
    story.background_run_ends(output)
    story.expect_typed(TasksNudges.WAIT_END.create(outcome=f"output {output} failed with code 1: 1 failed, 3 passed"))
    story.expect_stack(story.agents.subject, Ready)
