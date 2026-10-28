from journal.features.messages.messages_nudges import MessagesNudges
from tests.scenarios.builder.stack_states import FOLLOWING_SEQUENCE, IDLE
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork, end=[IDLE, FOLLOWING_SEQUENCE])
def test_a_comment_on_a_document_asks_for_the_change_in_the_document(scenario):
    document = scenario.agent_writes_a_document("the footer", "## Layout\n\nThe footer holds the links.\n")
    comment = scenario.user_comments_on("docs", document, "put the copyright in the footer too")
    scenario.agent_runs(f"message read {comment}")
    scenario.expect_agent_told(MessagesNudges.COMMENT_READ, n=comment)
