from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.orchestrator_started_plans import OrchestratorStartedPlans


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(FitnessOptions.WARNINGS, False)
def test_a_worker_sent_one_task_of_a_plan_whose_other_task_waits_is_told_once_to_queue_it_with_the_fitness_warnings_off(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal worker dispatch 'Lady Lovelace' --task {story.tasks.first} --changes 'the files of its task' --profile journal-medior")
    result.expect_agent_told(story.agents.subject, WorkersNudges.QUEUE_RELATED, task=story.tasks.first, listed=str(story.tasks.second))
    story.expect_stack(story.agents.subject, Orchestrating, OrchestratingPlan)
