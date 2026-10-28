from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.verification.states.verifying import Verifying
from journal.features.verification.support.model_fit_evidence import MODEL_VERDICTS
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.verifier.verifier_judging_model import VerifierJudgingModel

TOO_STRONG, RIGHT, TOO_WEAK = MODEL_VERDICTS


@story(VerifierJudgingModel, mode=ORCHESTRATOR_MODE, scope=AgentRole.VERIFIER)
def test_a_model_that_fit_its_work_ends_the_verifier_and_tells_the_agent_nothing(story):
    story.agent_runs(f"verdict model {RIGHT} 'a parser of two rules fits the model it ran on'")
    story.expect_command_passed()
    story.expect_main_not_told(WorkersNudges.MODEL_OVERPOWERED)
    story.expect_main_not_told(WorkersNudges.MODEL_UNDERPOWERED)
    story.expect_stack(Void, Verifying, Ended)


@story(VerifierJudgingModel, mode=ORCHESTRATOR_MODE, scope=AgentRole.VERIFIER)
def test_a_dismissal_verdict_on_a_models_job_is_refused(story):
    story.agent_runs("verdict give yes 'the model was right'")
    story.expect_command_refused()
    story.expect_stack(Void, Verifying)
