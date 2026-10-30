from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

HELPER_LINES = ("tests turn tests/test_parser.py", "clock-in", "clock-out 'done'", "review record 'all points pass'", "verdict model right 'it fit'", "proof 1 'parser.py:12'", "todo list")


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_main_agent_is_refused_every_verb_only_a_helper_runs(story):
    for line in HELPER_LINES:
        result = story.agent_runs(story.agents.subject, line)
        result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)
