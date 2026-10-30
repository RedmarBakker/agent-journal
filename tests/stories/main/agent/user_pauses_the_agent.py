from journal.features.pausing.pausing_nudges import PausingNudges
from journal.features.pausing.states.user_pause import UserPause
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_paused_agent_is_refused_its_writes_and_told_to_carry_on_when_resumed(story):
    story.user_pauses_the_agent()
    story.expect_stack(story.agents.subject, Ready, Working, UserPause)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, PausingNudges.PAUSED)
    result = story.user_resumes_the_agent()
    result.expect_agent_told(story.agents.subject, PausingNudges.RESUMED)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_paused_agent_reads_and_journals_through_the_pause_while_its_work_waits(story):
    story.user_pauses_the_agent()
    message = story.user_sends_message("look at the footer")
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, PausingNudges.PAUSED)
    for line in (f"journal message read {message}", "journal task list", "journal search footer", f"journal message send 'I am paused; I wait for you' --reply-to {message}"):
        result = story.agent_runs_in_the_shell(story.agents.subject, line)
        result.expect_allowed()
    for line in (f"journal message read {message} && echo hi", "pytest -q"):
        result = story.agent_runs_in_the_shell(story.agents.subject, line)
        result.expect_refused(story.agents.subject, PausingNudges.PAUSED)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, UserPause)
