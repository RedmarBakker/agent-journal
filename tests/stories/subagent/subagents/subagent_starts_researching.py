from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent

MAIN_AGENT_READS = 60


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_works_on_a_stack_of_its_own_and_stays_listed_through_the_main_agents_tool_uses(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.repeat(MAIN_AGENT_READS, lambda: story.agent_reads(story.agents.main))
    result = story.agent_runs(story.agents.main, "worker list")
    result.expect_command_line("find where the parser is called")
    story.expect_stack(story.agents.main, Ready)
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_writes_while_the_main_agent_owes_a_reply(story):
    message = story.user_sends_message("how far is the parser?")
    story.agent_runs(story.agents.main, f"message read {message}")
    result = story.agent_writes(story.agents.subject, "notes.md")
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.MESSAGE_READ)
    story.expect_stack(story.agents.subject, Void, Researching)
