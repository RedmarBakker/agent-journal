from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.orchestrator_started_plans import OrchestratorStartedPlans


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrators_finished_plan_task_leaves_the_next_open_and_a_task_in_its_hand_goes_to_a_busy_workers_queue(story):
    story.agent_runs(story.agents.subject, f"task start {story.tasks.first}")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.first} --how 'written'")
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    worker = story.agent_dispatches_worker(story.agents.subject, "Lady Lovelace", story.tasks.second)
    story.agent_runs(story.agents.subject, f"task start {story.tasks.invoice}")
    story.agent_runs(story.agents.subject, f"worker queue {worker} {story.tasks.invoice}")
    story.expect_command_passed()
    story.expect_task(story.tasks.invoice, delegated=True)
    story.expect_stack(story.agents.subject, Orchestrating, OrchestratingPlan, ExternalWait)
