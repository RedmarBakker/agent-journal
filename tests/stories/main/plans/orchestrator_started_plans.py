from journal.engine.states.ended import Ended
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.orchestrator_started_plans import OrchestratorStartedPlans


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_the_orchestrator_is_reminded_of_every_started_plan_and_told_once_of_one_that_stalls_while_another_moves(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told(story.agents.subject, WorkersNudges.STARTED_PLANS)
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.PLAN_STALLED)
    story.time_travel(minutes=story.setting(WorkersOptions.PLAN_STALL_MINUTES) + 1)
    story.agent_runs(story.agents.subject, f"task edit {story.tasks.invoice} --brief '- the invoice is sent'")
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told(story.agents.subject, WorkersNudges.PLAN_STALLED, n=story.plans.first)
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.PLAN_STALLED)
    story.expect_stack(story.agents.subject, Orchestrating, OrchestratingPlan, Ended)
