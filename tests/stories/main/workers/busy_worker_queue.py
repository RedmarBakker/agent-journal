from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_tasks_queued_for_a_busy_worker_are_delegated_at_once_shown_on_its_row_and_never_queued_twice(story):
    worker = story.agents.workers.first()
    docs = story.agent_creates_task(story.agents.subject, "the docs")
    help_page = story.agent_creates_task(story.agents.subject, "the help page")
    story.agent_runs(story.agents.subject, f"worker queue {worker} {docs} {help_page} --report each")
    story.expect_command_text(f"queue: task {docs}, task {help_page}")
    story.expect_task(docs, delegated=True)
    story.expect_task(help_page, delegated=True)
    story.agent_runs(story.agents.subject, f"worker queue {worker} {docs} --report each")
    story.expect_command_refused()
    story.expect_command_text("only an open task")
    story.user_opens(f"/journal/workers?ids={worker}")
    story.expect_viewer_part(("rows", 0, "task", "task_id"), story.tasks.briefed)
    story.expect_viewer_part(("rows", 0, "queue"), [{"id": docs, "title": "the docs"}, {"id": help_page, "title": "the help page"}])
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
