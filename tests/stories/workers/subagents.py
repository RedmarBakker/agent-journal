from journal.engine.states.demand_block import DemandBlock
from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.started_subagent import RESEARCHER, StartedSubagent
from tests.stories.fixtures.unanswered_message import UnansweredMessage

REVIEWER = "journal-plan-reviewer"
SUBAGENT = "agent-held"


@story(UnansweredMessage, end=[Ready, DemandBlock])
def test_a_subagents_tool_use_is_never_held_by_the_agents_hold(story):
    story.subagent_starts(SUBAGENT, RESEARCHER)
    story.subagent_writes(SUBAGENT, "notes.md")
    story.expect_allowed()
    story.expect_stack(Ready, DemandBlock)


@story(StartedSubagent, end=[Ready])
@setting(WorkersOptions.SUBAGENT_LIMIT, 1)
def test_a_subagent_sent_past_the_running_limit_is_refused(story):
    story.expect_subagent_stack(story.start.subagent, Void, Researching)
    story.agent_sends_subagent(RESEARCHER, "find where the grammar is read")
    story.expect_refused(WorkersNudges.SUBAGENT_OVERFLOW, running=1)


@story(StartedSubagent, end=[Ready])
@setting(WorkersOptions.SUBAGENT_LIMIT, 0)
def test_a_running_limit_of_zero_lets_every_subagent_through(story):
    story.expect_subagent_stack(story.start.subagent, Void, Researching)
    story.agent_sends_subagent(REVIEWER, "review the parser plan")
    story.expect_allowed()


@story(StartedSubagent, end=[Ready])
def test_a_subagent_that_ends_stays_researching_for_a_message_that_resumes_it(story):
    story.subagent_ends(story.start.subagent)
    story.expect_subagent_stack(story.start.subagent, Void, Researching, Ended)
