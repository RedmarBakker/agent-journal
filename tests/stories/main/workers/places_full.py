from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.orchestrator_worker_delivered import OrchestratorWorkerDelivered


@story(OrchestratorWorkerDelivered, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.WORKER_LIMIT, 1)
def test_with_every_place_full_a_refused_dispatch_names_the_clocked_out_worker_as_the_work_to_check(story):
    lexer = story.agent_creates_briefed_task(story.agents.subject, "the lexer", "- splits the words")
    story.agent_runs_in_the_shell(story.agents.subject, f"journal worker dispatch 'Ada Byron' --task {lexer} --changes 'the lexer' --tests 'Scoped tests' --profile journal-medior --model sonnet")
    story.expect_agent_told(story.agents.subject, WorkersNudges.PLACES_FULL, n=str(story.agents.workers.first()))
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Orchestrating)
