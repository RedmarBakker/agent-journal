from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.orchestrator_worker import OrchestratorWorker

NO_REVIEWER, ONE_REVIEWER = 0, 1


@story(OrchestratorWorker, mode=ORCHESTRATOR_MODE, scope=AgentRole.MAIN)
@setting(ReviewingOptions.REVIEWER, False)
def test_with_the_reviewer_off_a_clock_out_goes_to_the_agent_to_check(story):
    story.worker_proves(story.start.worker, 1, "parser.py:12, test_reads passes")
    story.worker_proves(story.start.worker, 2, "parser.py:30, test_names passes")
    story.worker_clocks_out(story.start.worker, "the parser is done")
    story.expect_agent_told(WorkersNudges.WORK_READY)
    story.expect_row_count("reviewers", NO_REVIEWER)
    story.expect_stack(Orchestrating)


@story(OrchestratorWorker, mode=ORCHESTRATOR_MODE, scope=AgentRole.MAIN)
@setting(ReviewingOptions.REVIEWER, True)
def test_with_the_reviewer_on_in_orchestrator_mode_a_clock_out_goes_to_a_reviewer(story):
    story.worker_proves(story.start.worker, 1, "parser.py:12, test_reads passes")
    story.worker_proves(story.start.worker, 2, "parser.py:30, test_names passes")
    story.worker_clocks_out(story.start.worker, "the parser is done")
    story.expect_agent_not_told(WorkersNudges.WORK_READY)
    story.expect_row_count("reviewers", ONE_REVIEWER)
    story.expect_stack(Orchestrating)
