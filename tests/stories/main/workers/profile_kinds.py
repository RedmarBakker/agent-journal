from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.briefed_task import BriefedTask

DISPATCH = "worker dispatch 'Mr. Brunel' --task {task} --changes 'the files of its task' --tests 'Scoped tests' --profile {profile}"


@story(BriefedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_profile_the_user_saved_is_dispatched_on_the_model_it_names(story):
    story.user_posted("/journal/profiles/builder", {"description": "writes code", "tools": "Read, Edit", "body": "You write.", "profile_type": "worker", "model": "sonnet"})
    story.agent_runs(story.agents.subject, DISPATCH.format(task=story.tasks.briefed, profile="builder"))
    story.expect_command_text("on claude sonnet")
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(BriefedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagent_profile_is_never_dispatched_as_a_worker(story):
    story.agent_runs(story.agents.subject, DISPATCH.format(task=story.tasks.briefed, profile="journal-researcher"))
    story.expect_command_refused()
    story.expect_command_text("no worker profile")
    story.expect_task(story.tasks.briefed, delegated=False)
    story.expect_stack(story.agents.subject, Ready)


@story(BriefedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_profile_sent_as_a_subagent_is_refused_naming_the_dispatch(story):
    story.user_posted("/journal/profiles/builder", {"description": "writes code", "tools": "Read, Edit", "body": "You write.", "profile_type": "worker", "model": "sonnet"})
    story.agent_sends_subagent(story.agents.subject, "builder", "write the parser")
    story.expect_refusal_text("is a worker:")
    story.expect_refusal_text("--profile builder")
    story.expect_task(story.tasks.briefed, delegated=False)
    story.expect_stack(story.agents.subject, Ready)
