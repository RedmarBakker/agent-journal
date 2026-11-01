from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_instruction_a_prompt_raises_comes_before_a_remark_waiting_in_its_answer(story):
    story.agent_closes_its_turn(story.agents.subject, "I left the footer as the user wants it.")
    message = story.user_sends_message("is the footer done?")
    story.agent_is_prompted(story.agents.subject, "is the footer done?")
    story.expect_last_answer_lines_in_order(MessagesNudges.NEW_MESSAGE.create(n=message), EtiquetteNudges.SECOND_PERSON)
    story.expect_stack(story.agents.subject, Ready)
