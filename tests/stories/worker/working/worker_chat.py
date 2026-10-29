from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker


@story(DispatchedWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_workers_job_and_written_turns_are_messages_of_its_own_chat_once_each_with_their_tags_left_as_text_and_a_queued_note_never_read_again(story):
    message = story.user_sends_message("how is the parser?")
    story.agent_has_written(story.agents.subject, f"[!reply:{message}] the parser reads")
    story.agent_has_written(story.agents.subject, '[!todo="a stray task"] names next')
    story.agent_clocks_in(story.agents.subject)
    story.agent_has_taken_a_queued_note(story.agents.subject, "check the header too")
    story.agent_has_written(story.agents.subject, "the parser is done")
    story.agent_stops(story.agents.subject)
    story.expect_worker_chat_after_its_job(
        story.agents.subject,
        ("agent", f"[!reply:{message}] the parser reads"),
        ("agent", '[!todo="a stray task"] names next'),
        ("agent", "the parser is done"),
    )
    story.expect_task_count(1)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
