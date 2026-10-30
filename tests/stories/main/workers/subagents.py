from journal.engine.states.demand_block import DemandBlock
from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from journal.models.subagent_state import SubagentState
from journal.support.card_outcome import CardOutcome
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.unanswered_message import UnansweredMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER, StartedSubagent

REVIEWER = "journal-plan-reviewer"
SUBAGENT = "agent-held"


@story(UnansweredMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagents_tool_use_is_never_held_by_the_agents_hold(story):
    story.subagent_starts(SUBAGENT, RESEARCHER)
    result = story.subagent_writes(SUBAGENT, "notes.md")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, DemandBlock)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.SUBAGENT_LIMIT, 1)
def test_a_subagent_sent_past_the_running_limit_is_refused(story):
    story.expect_stack(story.agents.subagent, Void, Researching)
    result = story.agent_sends_subagent(story.agents.subject, RESEARCHER, "find where the grammar is read")
    result.expect_refused(story.agents.subject, WorkersNudges.SUBAGENT_OVERFLOW, running=1)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.SUBAGENT_LIMIT, 0)
def test_a_running_limit_of_zero_lets_every_subagent_through(story):
    story.expect_stack(story.agents.subagent, Void, Researching)
    result = story.agent_sends_subagent(story.agents.subject, REVIEWER, "review the parser plan")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)



@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_background_subagent_that_ended_reads_finished_then_runs_again_when_it_is_sent_a_message_and_is_counted_open(story):
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, "map the hooks", "a9")
    story.expect_dispatch_card(active=True, state=SubagentState.ACTIVE.value, outcome=str(CardOutcome.RUNNING))
    story.subagent_ends("a9")
    story.expect_dispatch_card(active=False, state=SubagentState.FINISHED.value, outcome=str(CardOutcome.PASSED))
    story.agent_messages_subagent(story.agents.subject, "a9", "one more")
    result = story.user_opens("/journal/subagents")
    result.expect_viewer_rows("rows", "state", ["running"])
    result.expect_viewer_part(("counts", "open"), 1)
    story.expect_stack(story.agents.subject, Ready)
