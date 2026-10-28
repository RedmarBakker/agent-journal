from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.verification.commands.verdict_command import REFUTED_VERDICT, SOUND_VERDICT
from journal.features.verification.states.verifying import Verifying
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.verifier.verifier_judging_dismissal import VerifierJudgingDismissal


@story(VerifierJudgingDismissal, mode=BUILDER_MODE, scope=AgentRole.VERIFIER)
def test_a_sound_verdict_ends_the_verifier_and_tells_the_agent_nothing_against_it(story):
    story.agent_runs(f"verdict give {SOUND_VERDICT} 'the reader shows the one line the run printed'")
    story.expect_command_passed()
    story.expect_main_not_told(ShellNudges.REPORT_REFUTED)
    story.expect_stack(Void, Verifying, Ended)


@story(VerifierJudgingDismissal, mode=BUILDER_MODE, scope=AgentRole.VERIFIER)
def test_a_verdict_against_the_dismissal_tells_the_agent_its_dismissal_was_refuted(story):
    story.agent_runs(f"verdict give {REFUTED_VERDICT} 'the reader hides the line the run printed'")
    story.expect_command_passed()
    story.expect_main_told(ShellNudges.REPORT_REFUTED)
    story.expect_stack(Void, Verifying, Ended)
