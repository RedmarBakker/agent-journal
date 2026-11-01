from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(WorkerDelivered, subject=AgentRole.MAIN)
@setting(WorkersOptions.WORKER_LIMIT, 1)
def test_with_every_place_full_a_refused_dispatch_names_the_clocked_out_worker_as_the_work_to_check(story):
    lexer = story.agent_creates_briefed_task(story.agents.subject, "the lexer", "- splits the words")
    result = story.agent_runs(story.agents.subject, f"journal worker dispatch 'Ada Byron' --task {lexer} --changes 'the lexer' --tests 'Scoped tests' --profile journal-medior --model sonnet")
    result.expect_command_refused()
    result.expect_command_text(WorkersNudges.PLACES_FULL.create(n=str(story.agents.workers.first())).rendered())
    story.expect_task(lexer, delegated=False)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready)
