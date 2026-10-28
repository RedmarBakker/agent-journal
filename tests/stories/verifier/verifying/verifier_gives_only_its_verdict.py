from journal.engine.states.void import Void
from journal.features.verification.states.verifying import Verifying
from journal.features.verification.verification_nudges import VerificationNudges
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.verifier.verifier_judging_dismissal import VerifierJudgingDismissal


@story(VerifierJudgingDismissal, mode=BUILDER_MODE)
def test_a_verifier_is_refused_a_read_and_told_to_give_its_verdict(story):
    story.agent_reads()
    story.expect_refused(VerificationNudges.VERIFIER_REFUSAL)
    story.expect_stack(Void, Verifying)


@story(VerifierJudgingDismissal, mode=BUILDER_MODE)
def test_a_verifier_is_refused_a_journal_command_other_than_its_verdict(story):
    story.agent_runs_in_the_shell("journal task list")
    story.expect_refused(VerificationNudges.VERIFIER_REFUSAL)
    story.expect_stack(Void, Verifying)
