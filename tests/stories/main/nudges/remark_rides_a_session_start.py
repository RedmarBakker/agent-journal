from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

EM_DASHES = "The build — the one from last night — is green."


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_remark_waiting_when_a_session_starts_rides_the_start(story):
    story.agent_closes_its_turn(EM_DASHES)
    story.agent_starts_a_session()
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_remark_waiting_when_the_session_resumes_rides_the_resume(story):
    story.agent_closes_its_turn(EM_DASHES)
    story.agent_resumes_the_session()
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_stack(Ready)
