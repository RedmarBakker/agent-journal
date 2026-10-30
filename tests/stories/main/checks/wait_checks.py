from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.lifted_wait_beside_a_block import LiftedWaitBesideABlock
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_checks_a_block_and_a_wait_made_are_listed_apart_and_left_out_of_the_agents_check_list(story):
    story.agent_runs(story.agents.subject, "check create lint --command true --brief 'the code is clean'")
    lint = story.created_number("check")
    deploy = story.agent_creates_task(story.agents.subject, "deploy")
    story.agent_runs(story.agents.subject, f"task block {deploy} 'the deploy' --until false")
    block = story.newest("checks")
    story.agent_runs(story.agents.subject, "await 'the deploy to finish' --until false")
    wait = story.newest("checks")
    result = story.user_opens("/journal/checks")
    result.expect_viewer_rows("rows", "id", [lint, block, wait])
    result.expect_viewer_part(("counts", "open"), 1)
    result = story.user_opens("/journal/checks?closed=1")
    result.expect_viewer_rows("rows", "id", [block, wait])
    result = story.agent_runs(story.agents.subject, "check list")
    result.expect_command_line_count(1)
    result.expect_command_text("lint")
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(LiftedWaitBesideABlock, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_lifted_waits_check_stays_and_a_blocks_check_goes_when_its_task_opens(story):
    story.agent_runs(story.agents.subject, f"task unblock {story.tasks.blocked}")
    story.expect_row("checks", story.checks.wait, {"wait_target": True})
    story.expect_row_absent("checks", story.checks.block)
    story.expect_stack(story.agents.subject, Ready)


@story(LiftedWaitBesideABlock, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_start_deletes_a_lifted_waits_check_and_keeps_the_one_a_blocked_task_waits_on(story):
    story.journal_starts_again()
    story.expect_row_absent("checks", story.checks.wait)
    story.expect_row("checks", story.checks.block, {"wait_target": True})
    story.expect_task(story.tasks.blocked, state=TaskState.BLOCKED)
    story.expect_stack(story.agents.subject, Ready)
