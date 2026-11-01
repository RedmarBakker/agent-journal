from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_reminder_with_a_bad_condition_is_refused_with_its_reason(story):
    result = story.agent_runs(story.agents.subject, """reminder create x --on task_completed --when '{"count": "chores", "is": 0}'""")
    result.expect_command_text("no table is named 'chores'")
    result = story.agent_runs(story.agents.subject, """reminder create x --on task_completed --when '{"count": "tasks", "where": {"colour": "red"}, "is": 0}'""")
    result.expect_command_text("colour")
    result = story.agent_runs(story.agents.subject, """reminder create x --on task_completed --when '{"count": "tasks", "where": {"state": ["open", "sleeping"]}, "is": 0}'""")
    result.expect_command_text("tasks state is never sleeping")
    result = story.agent_runs(story.agents.subject, """reminder create x --on task_completed --when '{"count": "tasks"}'""")
    result.expect_command_text("a condition is")
    result = story.agent_runs(story.agents.subject, "reminder create x --on task_completed --when '{tasks'")
    result.expect_command_text("--when is not JSON")
    result = story.agent_runs(story.agents.subject, "reminder create x --once")
    result.expect_command_text("--when and --once go with --on")
    result = story.agent_runs(story.agents.subject, "reminder create x --on task_finished")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)
