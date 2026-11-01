from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.working_worker import WorkingWorker

NO_REVIEWER, ONE_REVIEWER = 0, 1


@story(WorkingWorker, subject=AgentRole.MAIN)
@setting(ReviewingOptions.REVIEWER, False)
def test_with_the_reviewer_off_a_clock_out_goes_to_the_agent_to_check(story):
    story.agent_proves(story.agents.workers.first(), 1, "parser.py:12, test_reads passes")
    story.agent_proves(story.agents.workers.first(), 2, "parser.py:30, test_names passes")
    result = story.agent_clocks_out(story.agents.workers.first(), "the parser is done")
    result.expect_agent_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_row_count("reviewers", NO_REVIEWER)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, subject=AgentRole.MAIN)
@setting(ReviewingOptions.REVIEWER, True)
def test_with_the_reviewer_on_a_clock_out_goes_to_a_reviewer(story):
    story.agent_proves(story.agents.workers.first(), 1, "parser.py:12, test_reads passes")
    story.agent_proves(story.agents.workers.first(), 2, "parser.py:30, test_names passes")
    result = story.agent_clocks_out(story.agents.workers.first(), "the parser is done")
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_row_count("reviewers", ONE_REVIEWER)
    story.expect_stack(story.agents.subject, Ready)
