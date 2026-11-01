from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.workers.states.working_task import WorkingTask
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_hook_without_its_header_is_still_the_workers_and_never_held_by_the_users_unread_messages(story):
    story.user_sends_message("for the main agent")
    for n in range(story.setting(MessagesOptions.EDIT_BLOCK_LIMIT) + 1):
        story.agent_writes_from_a_hook_without_its_header(story.agents.subject, f"w{n}.py")
    story.last_step.expect_allowed()
    story.last_step.expect_agent_not_told(story.agents.subject, MessagesNudges.INBOX_EDIT_BLOCK)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
