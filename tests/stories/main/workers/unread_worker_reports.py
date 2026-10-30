from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.idle_worker import IdleWorker


@story(IdleWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_report_not_acted_on_is_named_at_each_stop_until_the_agent_acts_on_it(story):
    worker = story.agents.workers.first()
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told(story.agents.subject, WorkersNudges.UNREAD_WORKER_REPORTS, reports_waiting=f"worker {worker} (Lady Lovelace)")
    story.agent_runs(story.agents.subject, f"worker release {worker} --drop")
    story.agent_runs(story.agents.subject, f"worker complete {worker} --why 'the parser goes to someone else'")
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.UNREAD_WORKER_REPORTS)
    story.expect_stack(story.agents.subject, Ready, Working)
