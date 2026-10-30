from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

WORK_BY_COMMAND = (("pytest -q", "testing"), ("npm --prefix src/web run build", "building"), ("git log -1", "reading"), ("python3 tools/seed.py", "running"))


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_agents_tool_work_names_a_test_run_or_a_build_by_the_shell_line_in_hand(story):
    for line, work in WORK_BY_COMMAND:
        story.agent_runs_in_the_shell(story.agents.subject, line)
        result = story.user_opens(f"/journal/agents?ids={story.main_agent_id()}")
        result.expect_viewer_part(("rows", 0, "tool_work"), work)
        story.agent_has_run_printing(story.agents.subject, line, "")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_agents_doing_is_the_first_part_of_its_shell_call_another_tool_its_verb_and_nothing_once_it_ends(story):
    story.agent_runs_in_the_shell(story.agents.subject, "ls src && git status")
    result = story.user_opens(f"/journal/agents?ids={story.main_agent_id()}")
    result.expect_viewer_part(("rows", 0, "doing"), "ls src")
    story.agent_has_run_printing(story.agents.subject, "ls src && git status", "clean")
    story.agent_reads(story.agents.subject)
    result = story.user_opens(f"/journal/agents?ids={story.main_agent_id()}")
    result.expect_viewer_part(("rows", 0, "doing"), "reading a file")
    story.expect_stack(story.agents.subject, Ready)
