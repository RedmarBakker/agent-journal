from journal.engine.states.void import Void
from journal.features.verification.states.verifying import Verifying
from journal.features.verification.verification_nudges import VerificationNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.verifier.verifier_judging_dismissal import VerifierJudgingDismissal


@story(VerifierJudgingDismissal, subject=AgentRole.VERIFIER)
def test_a_verifier_is_refused_a_read_and_told_to_give_its_verdict(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, VerificationNudges.VERIFIER_REFUSAL)
    story.expect_stack(story.agents.subject, Void, Verifying)


@story(VerifierJudgingDismissal, subject=AgentRole.VERIFIER)
def test_a_verifier_can_read_the_model_chosen_for_its_judgement(story):
    result = story.agent_runs(story.agents.subject, "verdict model")
    result.expect_command_passed()
    result.expect_command_text("verifier model:")
    story.expect_stack(story.agents.subject, Void, Verifying)


@story(VerifierJudgingDismissal, subject=AgentRole.VERIFIER)
def test_a_verifier_is_refused_a_journal_command_outside_its_verdict_noun(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task list")
    result.expect_refused(story.agents.subject, VerificationNudges.VERIFIER_REFUSAL)
    story.expect_stack(story.agents.subject, Void, Verifying)
