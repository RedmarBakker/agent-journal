from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_run_ended import WorkerRunEnded

POINT = 1
FIRST, SECOND, THIRD = "the alias names are missing", "the tests do not run", "the lexer is still missing"


@story(WorkerRunEnded, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_point_sent_back_again_names_the_earlier_reason_and_a_third_time_names_the_model_to_change(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} {POINT} --short '{FIRST}'")
    story.expect_agent_told(story.agents.subject, WorkersNudges.PROOF_REJECTED, n=worker, point=POINT)
    story.worker_proves_its_point_again(worker, POINT, "parser.py:13, test_reads passes")
    story.agent_runs(story.agents.subject, f"worker check {worker} {POINT} --short '{SECOND}'")
    story.expect_agent_told(story.agents.subject, WorkersNudges.PROOF_REJECTED_REPEAT, n=worker, point=POINT, earlier=FIRST)
    story.worker_proves_its_point_again(worker, POINT, "parser.py:14, test_reads passes")
    story.agent_runs(story.agents.subject, f"worker check {worker} {POINT} --short '{THIRD}'")
    story.expect_agent_told(story.agents.subject, WorkersNudges.PROOF_REJECTED_OFTEN, n=worker, point=POINT, times=3, model="sonnet", earlier=f"{FIRST}; {SECOND}")
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
