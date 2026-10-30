from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.idle_worker import IdleWorker

DISPATCH = "journal worker dispatch 'Ada' 'speed up the parser' --profile {profile} --fresh"


@story(IdleWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.PROFILE_LIMIT, 1)
def test_a_dispatch_past_its_profiles_kept_workers_is_refused_naming_the_idle_one_while_another_profile_goes(story):
    story.agent_runs_in_the_shell(story.agents.subject, DISPATCH.format(profile="journal-medior"))
    story.expect_refused(story.agents.subject, WorkersNudges.IDLE_CAP, count=1, total=1, profile="journal-medior")
    story.expect_refusal_text(f"journal worker send {story.agents.workers.first()}")
    story.agent_runs_in_the_shell(story.agents.subject, DISPATCH.format(profile="journal-senior"))
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(IdleWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.PROFILE_LIMIT, 0)
def test_a_profile_kept_workers_limit_of_nought_refuses_no_dispatch(story):
    story.agent_runs_in_the_shell(story.agents.subject, DISPATCH.format(profile="journal-medior"))
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)
