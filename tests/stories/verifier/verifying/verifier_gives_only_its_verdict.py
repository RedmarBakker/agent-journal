from journal.engine.states.void import Void
from journal.features.verification.states.verifying import Verifying
from journal.features.verification.verification_nudges import VerificationNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.verifier.verifier_judging_dismissal import VerifierJudgingDismissal


@story(VerifierJudgingDismissal, mode=BUILDER_MODE, subject=AgentRole.VERIFIER)
def test_a_verifier_is_refused_a_read_and_told_to_give_its_verdict(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, VerificationNudges.VERIFIER_REFUSAL)
    story.expect_stack(story.agents.subject, Void, Verifying)


@story(VerifierJudgingDismissal, mode=BUILDER_MODE, subject=AgentRole.VERIFIER)
def test_a_verifier_is_refused_a_journal_command_other_than_its_verdict(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task list")
    result.expect_refused(story.agents.subject, VerificationNudges.VERIFIER_REFUSAL)
    story.expect_stack(story.agents.subject, Void, Verifying)
