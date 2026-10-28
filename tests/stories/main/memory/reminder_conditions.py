from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reminder_with_a_bad_condition_is_refused_with_its_reason(story):
    story.agent_runs("""reminder create x --on task_completed --when '{"count": "chores", "is": 0}'""")
    story.expect_command_text("no table is named 'chores'")
    story.agent_runs("""reminder create x --on task_completed --when '{"count": "tasks", "where": {"colour": "red"}, "is": 0}'""")
    story.expect_command_text("colour")
    story.agent_runs("""reminder create x --on task_completed --when '{"count": "tasks", "where": {"state": ["open", "sleeping"]}, "is": 0}'""")
    story.expect_command_text("tasks state is never sleeping")
    story.agent_runs("""reminder create x --on task_completed --when '{"count": "tasks"}'""")
    story.expect_command_text("a condition is")
    story.agent_runs("reminder create x --on task_completed --when '{tasks'")
    story.expect_command_text("--when is not JSON")
    story.agent_runs("reminder create x --once")
    story.expect_command_text("--when and --once go with --on")
    story.agent_runs("reminder create x --on task_finished")
    story.expect_command_refused()
    story.expect_stack(Ready)
