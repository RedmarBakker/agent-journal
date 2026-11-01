from journal.engine.states.void import Void
from journal.features.shell.support.output_view import OutputView
from journal.features.workers.states.working_task import WorkingTask
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_run_of_a_worker_shows_in_the_chat_under_the_worker_s_name(story):
    run = story.agent_has_a_background_run_printing(story.agents.subject, "python3 -m pytest tests/test_parser.py", "collected 3 items", "...")
    story.agent_runs(story.agents.subject, f"output watch {run}")
    story.expect_card_data(story.card_number(OutputView.key(run)), worker="Lady Lovelace")
    story.expect_stack(story.agents.subject, Void, WorkingTask)
