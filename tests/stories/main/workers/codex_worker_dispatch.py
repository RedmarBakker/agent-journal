from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.providers.codex import Codex
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.main.briefed_task import BriefedTask


@story(BriefedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@provider(Codex)
def test_a_codex_agent_dispatches_a_codex_worker(story):
    worker = story.agent_dispatches_worker(story.agents.subject, "Ada Lovelace", story.tasks.briefed)
    story.expect_worker(worker, provider="codex")
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
