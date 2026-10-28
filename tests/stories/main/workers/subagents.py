from journal.engine.states.demand_block import DemandBlock
from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.unanswered_message import UnansweredMessage
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER, StartedSubagent

REVIEWER = "journal-plan-reviewer"
SUBAGENT = "agent-held"


@story(UnansweredMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_subagents_tool_use_is_never_held_by_the_agents_hold(story):
    story.subagent_starts(SUBAGENT, RESEARCHER)
    story.subagent_writes(SUBAGENT, "notes.md")
    story.expect_allowed()
    story.expect_stack(Ready, DemandBlock)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.SUBAGENT_LIMIT, 1)
def test_a_subagent_sent_past_the_running_limit_is_refused(story):
    story.expect_subagent_stack(story.start.subagent, Void, Researching)
    story.agent_sends_subagent(RESEARCHER, "find where the grammar is read")
    story.expect_refused(WorkersNudges.SUBAGENT_OVERFLOW, running=1)
    story.expect_stack(Ready)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(WorkersOptions.SUBAGENT_LIMIT, 0)
def test_a_running_limit_of_zero_lets_every_subagent_through(story):
    story.expect_subagent_stack(story.start.subagent, Void, Researching)
    story.agent_sends_subagent(REVIEWER, "review the parser plan")
    story.expect_allowed()
    story.expect_stack(Ready)
