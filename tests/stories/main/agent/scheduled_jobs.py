from journal.features.schedules.schedules_nudges import SchedulesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

JOB = "200ed8b1"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_user_stops_a_scheduled_job_from_the_viewer_and_the_agent_is_told_to_delete_it(story):
    story.agent_schedules_a_job(story.agents.subject, JOB)
    agent = story.main_agent_id()
    result = story.user_presses(f"/journal/agents/{agent}/jobs/ffffffff/stop", {})
    result.expect_viewer_refused("")
    result = story.user_presses(f"/journal/agents/{agent}/jobs/{JOB}/stop", {})
    result.expect_viewer_passed()
    result.expect_agent_told(story.agents.subject, SchedulesNudges.STOP_JOB, job=JOB)
    story.agent_deletes_the_job(story.agents.subject, JOB)
    result = story.user_presses(f"/journal/agents/{agent}/jobs/{JOB}/stop", {})
    result.expect_viewer_refused("")
    story.expect_stack(story.agents.subject, Ready)
