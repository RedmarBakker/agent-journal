from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

THIRD_PERSON_WORDS = "I left the footer as the user wants it."


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_remark_waiting_when_the_user_prompts_rides_the_prompt_and_not_the_next_tool_use(story):
    story.agent_closes_its_turn(THIRD_PERSON_WORDS)
    story.agent_is_prompted("go on")
    story.expect_last_answer_carries(EtiquetteNudges.SECOND_PERSON)
    story.agent_reads()
    story.expect_last_answer_without(EtiquetteNudges.SECOND_PERSON)
    story.expect_stack(Ready)
