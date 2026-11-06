from journal.features.delivery.listeners.line_retyping import WAIT_LIMIT_SECONDS
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.main_agent_with_old_session_rows import MainAgentWithOldSessionRows
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_finished_wait_line_without_its_prefix_is_confirmed_and_not_typed_again(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "sleep 2")
    story.agent_runs(story.agents.subject, f"await 'the build' --output {output}")
    story.background_run_ends(story.agents.subject, output, status=0)
    line = TasksNudges.WAIT_END.create(outcome=f"output {output} finished")
    story.agent_is_prompted(story.agents.subject, line.rendered())
    story.expect_no_user_message_text_in("main", line.rendered())
    story.agent_stops(story.agents.subject)
    story.clock_ticks(WAIT_LIMIT_SECONDS * 2)
    story.expect_typed_nudge(TasksNudges.WAIT_END, outcome=f"output {output} finished")
    story.expect_stack(story.agents.subject, Ready)


@story(MainAgentWithOldSessionRows, subject=AgentRole.MAIN)
def test_a_passed_wait_is_not_retyped_after_its_check_is_deleted_with_old_main_sessions(story):
    story.agent_supervisor_accepts_lines(story.agents.subject)
    story.agent_runs(story.agents.subject, "await 'the nightly build' --until 'exit 0'")
    check = story.newest("checks")
    story.agent_reads(story.agents.subject)
    story.agent_stops(story.agents.subject)
    story.agent_runs(story.agents.subject, f"check run {check}")
    story.expect_row_absent("checks", check)
    story.agent_is_woken_by_the_typed_line(story.agents.subject)
    story.agent_reads(story.agents.subject)
    story.agent_stops(story.agents.subject)
    story.clock_ticks(WAIT_LIMIT_SECONDS + 1)
    story.clock_ticks(WAIT_LIMIT_SECONDS * 2 + 1)
    story.expect_row_absent("checks", check)
    story.expect_typed_nudge(TasksNudges.WAIT_CHECK_PASSED, count=1, what="the nightly build", lines="the check passed")
    story.expect_stack(story.agents.subject, Ready)
