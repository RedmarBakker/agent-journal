from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.MAIN)
@setting(WorkersOptions.WORKER_LIMIT, 1)
def test_a_dispatch_past_the_most_workers_out_at_once_is_refused(story):
    lexer = story.agent_creates_briefed_task(story.agents.subject, "the lexer", "- splits the words")
    result = story.agent_runs(story.agents.subject, f"worker dispatch 'Ada Byron' --task {lexer} --changes 'the lexer' --tests 'Scoped tests' --profile journal-medior --model sonnet")
    result.expect_command_refused()
    result.expect_command_text(WorkersNudges.WORKER_OVERFLOW.create(out=1).rendered().partition(":")[0].partition(".")[0])
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
