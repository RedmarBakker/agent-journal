from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

SHOP_TALK = "I ran journal task start 3 for the footer."


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_remark_told_on_a_tool_use_is_not_told_again_at_the_stop_even_for_the_same_words_again(story):
    story.agent_closes_its_turn(story.agents.subject, SHOP_TALK)
    story.agent_reads(story.agents.subject)
    story.expect_last_answer_carries(EtiquetteNudges.SHOP_TALK_WARNING)
    story.agent_closes_its_turn(story.agents.subject, SHOP_TALK)
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_last_answer_without(EtiquetteNudges.SHOP_TALK_WARNING)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_remark_told_on_a_stop_is_not_told_again_on_the_next_prompt(story):
    story.agent_closes_its_turn(story.agents.subject, SHOP_TALK)
    story.agent_stops(story.agents.subject)
    story.agent_is_prompted_in_a_new_turn(story.agents.subject, "go on")
    story.expect_last_answer_without(EtiquetteNudges.SHOP_TALK_WARNING)
    story.expect_stack(story.agents.subject, Ready)

