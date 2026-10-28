from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.soloing import Soloing
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, SOLO_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.briefed_task import BriefedTask
from tests.stories.fixtures.main.solo_agent import SoloAgent
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.worker.working_worker import WorkingWorker

REVIEWER = "journal-plan-reviewer"


@story(BriefedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.BUILDER_DISPATCH_ALLOWED, False)
def test_a_builder_may_not_dispatch_a_worker_when_the_user_turned_it_off(story):
    story.agent_runs_in_the_shell(f"journal worker dispatch 'Lady Lovelace' --task {story.start.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_refused(WorkersNudges.MODE_REFUSAL)
    story.expect_stack(Ready)


@story(BriefedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.BUILDER_DISPATCH_ALLOWED, True)
def test_a_builder_allowed_to_dispatch_is_let_through(story):
    story.agent_runs_in_the_shell(f"journal worker dispatch 'Lady Lovelace' --task {story.start.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.BUILDER_QUEUE_ALLOWED, False)
def test_a_builder_may_not_queue_a_workers_next_task_when_the_user_turned_it_off(story):
    story.agent_runs_in_the_shell(f"journal worker queue {story.start.worker} {story.start.briefed}")
    story.expect_refused(WorkersNudges.MODE_REFUSAL)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.BUILDER_SUBAGENTS_ALLOWED, False)
def test_a_builder_sends_a_subagent_only_while_the_user_allows_it(story):
    story.agent_sends_subagent(REVIEWER, "review the parser plan")
    story.expect_refused(WorkersNudges.MODE_REFUSAL)
    story.user_sets(WorkersOptions.BUILDER_SUBAGENTS_ALLOWED, True)
    story.agent_sends_subagent(REVIEWER, "review the parser plan")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(SoloAgent, mode=SOLO_MODE, scope=AgentRole.MAIN)
def test_a_solo_agent_may_not_dispatch_a_worker_nor_send_one_its_next_job(story):
    story.agent_runs_in_the_shell(f"journal worker dispatch 'Lady Lovelace' --task {story.start.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_refused(WorkersNudges.SOLO_DISPATCH)
    story.agent_runs_in_the_shell("journal worker send 1 'the next job'")
    story.expect_refused(WorkersNudges.SOLO_DISPATCH)
    story.expect_stack(Soloing)


@story(SoloAgent, mode=SOLO_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.SOLO_SUBAGENTS_ALLOWED, False)
def test_a_solo_agent_may_not_send_a_subagent_unless_the_user_allows_it(story):
    story.agent_sends_subagent(REVIEWER, "review the parser plan")
    story.expect_refused(WorkersNudges.MODE_REFUSAL)
    story.expect_stack(Soloing)


@story(SoloAgent, mode=SOLO_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.SOLO_SUBAGENTS_ALLOWED, True)
def test_a_solo_agent_the_user_allows_subagents_may_send_one(story):
    story.agent_sends_subagent(REVIEWER, "review the parser plan")
    story.expect_allowed()
    story.expect_stack(Soloing)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_switching_to_solo_mode_names_the_mode(story):
    story.user_sets(WorkersOptions.MODE, SOLO_MODE)
    story.expect_agent_told(WorkersNudges.SOLO_MODE)
    story.agent_reads()
    story.expect_stack(Soloing)


@story(SoloAgent, mode=SOLO_MODE, scope=AgentRole.MAIN)
def test_switching_back_to_builder_mode_leaves_the_solo_state(story):
    story.user_sets(WorkersOptions.MODE, BUILDER_MODE)
    story.agent_reads()
    story.expect_stack(Ready)
