from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

EM_DASHES = "The build — the one from last night — is green."


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_waiting_at_the_session_end_is_carried_by_the_next_session_start(story):
    story.agent_closes_its_turn(story.agents.subject, EM_DASHES)
    story.agent_ends_the_session(story.agents.subject)
    story.expect_last_answer_without(EtiquetteNudges.EM_DASH_WARNING)
    story.agent_starts_a_session(story.agents.subject)
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_stack(story.agents.subject, Ready)
