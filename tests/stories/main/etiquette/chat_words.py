from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.etiquette.etiquette_options import EtiquetteOptions
from journal.features.pins.pins_nudges import PinsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_shop_talk_and_the_third_person_are_named_at_the_next_tool_use(story):
    story.agent_closes_its_turn("I ran journal task start 3 because the user wants it.")
    story.expect_agent_told(EtiquetteNudges.SHOP_TALK_WARNING)
    story.expect_agent_told(EtiquetteNudges.SECOND_PERSON)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_telling_the_user_a_link_is_pinned_with_none_made_is_pointed_out(story):
    story.agent_closes_its_turn("The design is pinned above the chat, Sir Jesse.")
    story.expect_agent_told(PinsNudges.UNPINNED_CLAIM)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_words_about_pinning_that_claim_no_pin_and_a_pin_just_made_are_left_alone(story):
    story.agent_closes_its_turn("Saying a link is pinned without pinning one is now pointed out.")
    story.agent_runs("notice create 'The design' --link 'https://example.com/design' --label 'Open the design'")
    story.agent_closes_its_turn("The design is pinned above the chat, Sir Jesse.")
    story.expect_agent_not_told(PinsNudges.UNPINNED_CLAIM)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_em_dashes_and_run_together_paragraphs_are_pointed_out_at_the_next_tool_use(story):
    story.agent_closes_its_turn("The build — the one from last night — is green.")
    story.expect_agent_told(EtiquetteNudges.EM_DASH_WARNING)
    story.agent_closes_its_turn(("The build is green. " * 25).strip())
    story.expect_agent_told(EtiquetteNudges.PARAGRAPH_SPACING)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(EtiquetteOptions.PLAIN_CODE_INTERVAL, 3)
def test_every_set_number_of_code_edits_brings_the_plain_words_reminder_and_a_documents_edit_is_not_counted(story):
    story.repeat(2, lambda: story.agent_writes("src/app.py"))
    story.agent_writes("docs/notes.md")
    story.expect_agent_not_told(EtiquetteNudges.PLAIN_CODE)
    story.agent_writes("src/app.vue")
    story.expect_agent_told(EtiquetteNudges.PLAIN_CODE)
    story.expect_stack(Ready)
