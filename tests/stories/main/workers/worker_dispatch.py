from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.briefed_task import BriefedTask


@story(BriefedTask, subject=AgentRole.MAIN)
def test_a_dispatch_that_names_no_change_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"worker dispatch 'Lady Lovelace' --task {story.tasks.briefed} --profile journal-medior --model sonnet")
    result.expect_command_refused()
    story.expect_task(story.tasks.briefed, state=TaskState.OPEN, delegated=False)
    story.expect_stack(story.agents.subject, Ready)


@story(BriefedTask, subject=AgentRole.MAIN)
def test_a_dispatch_on_a_completed_task_is_refused(story):
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.briefed} --how done")
    result = story.agent_runs(story.agents.subject, f"worker dispatch 'Lady Lovelace' --task {story.tasks.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    result.expect_command_refused()
    story.expect_task(story.tasks.briefed, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)
