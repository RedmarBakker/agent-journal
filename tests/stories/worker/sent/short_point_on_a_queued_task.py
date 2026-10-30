from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_whose_queued_task_comes_back_short_takes_that_task_in_hand_and_proves_it_again(story):
    docs = story.agent_creates_task(story.agents.main, "the docs")
    story.agent_runs(story.agents.main, f"worker queue {story.agents.subject} {docs}")
    story.agent_proves(story.agents.subject, 1, "parser.py:12, test_reads passes")
    story.agent_proves(story.agents.subject, 2, "parser.py:30, test_names passes")
    story.agent_clocks_out(story.agents.subject, "the parser is done")
    story.agent_runs(story.agents.subject, "clock-in")
    story.agent_proves(story.agents.subject, 1, "docs.md:4, the docs name the parser")
    story.agent_clocks_out(story.agents.subject, "the docs are done")
    story.worker_run_ends_with_its_session(story.agents.subject, "the queue is done")
    story.agent_runs(story.agents.main, f"worker check {story.agents.subject} 1 --task {story.tasks.briefed}")
    story.agent_runs(story.agents.main, f"worker check {story.agents.subject} 2 --task {story.tasks.briefed}")
    result = story.agent_runs(story.agents.main, f"worker check {story.agents.subject} 1 --task {docs} --short 'name the test'")
    result.expect_command_passed()
    story.worker_proves_its_point_again(story.agents.subject, 1, "docs.md:6, test_docs_name_the_parser passes")
    story.expect_task(docs, state=TaskState.STARTED)
    result = story.agent_clocks_out(story.agents.subject, "the test is named")
    result.expect_agent_told(story.agents.main, WorkersNudges.WORK_READY)
    story.expect_stack(story.agents.subject, Void, Ended)
