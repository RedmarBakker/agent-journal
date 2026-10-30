from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.reviewing.states.reviewing import Reviewing
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE, subject=AgentRole.REVIEWER)
def test_a_reviewer_is_told_none_of_the_main_agents_lines_when_the_user_writes(story):
    story.user_sends_message("is the parser right?")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.NEW_MESSAGE)
    story.expect_stack(story.agents.subject, Void, Reviewing)
