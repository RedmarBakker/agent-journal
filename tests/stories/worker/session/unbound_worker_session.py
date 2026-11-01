from journal.engine.engine_nudges import EngineNudges
from journal.engine.states.void import Void
from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.providers.codex import Codex
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.worker.unbound_worker import UnboundWorker


@story(UnboundWorker, subject=AgentRole.WORKER)
@provider(Codex)
def test_a_codex_workers_first_hook_binds_it_as_the_worker_answered_by_its_floor_with_no_main_line(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, EngineNudges.JOBLESS_HELPER)
    result.expect_agent_not_told(story.agents.subject, BriefingNudges.OVERVIEW_FIRST)
    story.expect_stack(story.agents.subject, Void)


@story(UnboundWorker, subject=AgentRole.WORKER)
@provider(Codex)
def test_a_codex_workers_first_command_from_its_shell_binds_it_as_the_worker_on_its_floor(story):
    story.agent_runs_a_command(story.agents.subject, "echo hi")
    story.last_step.expect_shell_exit(0)
    story.expect_stack(story.agents.subject, Void)
