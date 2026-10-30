from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.providers.codex import Codex
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

SUBAGENT = "sub1"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagents_command_is_told_by_the_hook_that_announced_it_and_the_announcement_is_used_up_by_it(story):
    story.subagent_starts(SUBAGENT, RESEARCHER)
    result = story.subagent_runs_in_the_shell(SUBAGENT, "journal task create x")
    result.expect_allowed()
    result = story.command_from_a_shell("task create x", {}, {"session": "another-session"})
    result.expect_command_passed()
    result = story.command_from_a_shell("task create x", {}, {"session": story.main_session()})
    result.expect_command_text("a subagent may not run journal task create")
    result = story.command_from_a_shell("task create x", {}, {"session": story.main_session()})
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_command_under_the_subagent_actor_runs_the_journals_reads_and_files_its_own_documents_only(story):
    subagent = {"X-Journal-Actor": "sub-agent"}
    result = story.command_from_a_shell("task list", subagent, {})
    result.expect_command_passed()
    result = story.command_from_a_shell("report create 'what the parser misses' --abstract 'two gaps' --body 'none yet'", subagent, {})
    result.expect_command_passed()
    for line in ("task create x", "message send hello"):
        result = story.command_from_a_shell(line, subagent, {})
        result.expect_command_text(f"a subagent may not run journal {line.split()[0]} {line.split()[1]}")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@provider(Codex)
def test_a_codex_command_from_another_thread_than_the_session_started_with_is_a_subagents(story):
    shell = {"agent": True, "provider": "codex"}
    result = story.command_from_a_shell("task create x", {"X-Journal-Thread": "thread-2"}, shell)
    result.expect_command_text("a subagent may not run journal task create")
    result = story.command_from_a_shell("task list", {"X-Journal-Thread": story.main_session()}, shell)
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready)
