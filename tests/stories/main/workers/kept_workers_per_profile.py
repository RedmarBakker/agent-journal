from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.idle_worker import IdleWorker

DISPATCH = "journal worker dispatch 'Ada' 'speed up the parser' --profile {profile} --fresh"


@story(IdleWorker, subject=AgentRole.MAIN)
@setting(WorkersOptions.PROFILE_LIMIT, 1)
def test_a_dispatch_past_its_profiles_kept_workers_is_refused_naming_the_idle_one_while_another_profile_goes(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, DISPATCH.format(profile="journal-medior"))
    result.expect_refused(story.agents.subject, WorkersNudges.IDLE_CAP, count=1, total=1, profile="journal-medior")
    result.expect_refusal_text(f"journal worker send {story.agents.workers.first()}")
    result = story.agent_runs_in_the_shell(story.agents.subject, DISPATCH.format(profile="journal-senior"))
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(IdleWorker, subject=AgentRole.MAIN)
@setting(WorkersOptions.PROFILE_LIMIT, 0)
def test_a_profile_kept_workers_limit_of_nought_refuses_no_dispatch(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, DISPATCH.format(profile="journal-medior"))
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)
