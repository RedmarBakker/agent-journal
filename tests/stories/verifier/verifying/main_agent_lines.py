from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.verification.states.verifying import Verifying
from journal.features.verification.verification_nudges import VerificationNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.verifier.verifier_judging_dismissal import VerifierJudgingDismissal


@story(VerifierJudgingDismissal, subject=AgentRole.VERIFIER)
def test_a_verifier_is_told_none_of_the_main_agents_lines_when_the_user_writes(story):
    story.user_sends_message("is the dismissal fair?")
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, VerificationNudges.VERIFIER_REFUSAL)
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.NEW_MESSAGE)
    story.expect_stack(story.agents.subject, Void, Verifying)
