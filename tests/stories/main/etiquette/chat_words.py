from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.etiquette.etiquette_options import EtiquetteOptions
from journal.features.pins.pins_nudges import PinsNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_telling_the_user_a_link_is_pinned_with_none_made_is_pointed_out(story):
    result = story.agent_closes_its_turn(story.agents.subject, "The design is pinned above the chat, Sir Jesse.")
    result.expect_agent_told(story.agents.subject, PinsNudges.UNPINNED_CLAIM)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_words_about_pinning_that_claim_no_pin_and_a_pin_just_made_are_left_alone(story):
    story.agent_closes_its_turn(story.agents.subject, "Saying a link is pinned without pinning one is now pointed out.")
    story.agent_runs(story.agents.subject, "notice create 'The design' --link 'https://example.com/design' --label 'Open the design'")
    result = story.agent_closes_its_turn(story.agents.subject, "The design is pinned above the chat, Sir Jesse.")
    result.expect_agent_not_told(story.agents.subject, PinsNudges.UNPINNED_CLAIM)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_em_dashes_and_run_together_paragraphs_wait_past_the_display_and_both_ride_the_stop(story):
    result = story.agent_closes_its_turn(story.agents.subject, "The build — the one from last night — is green.")
    result.expect_agent_told(story.agents.subject, EtiquetteNudges.EM_DASH_WARNING)
    result = story.agent_closes_its_turn(story.agents.subject, ("The build is green. " * 25).strip())
    result.expect_agent_told(story.agents.subject, EtiquetteNudges.PARAGRAPH_SPACING)
    story.expect_last_answer_without(EtiquetteNudges.EM_DASH_WARNING)
    story.agent_stops(story.agents.subject)
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_last_answer_carries(EtiquetteNudges.PARAGRAPH_SPACING)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(EtiquetteOptions.PLAIN_CODE_INTERVAL, 3)
def test_every_set_number_of_code_edits_brings_the_plain_words_reminder_and_a_documents_edit_is_not_counted(story):
    story.repeat(2, lambda: story.agent_writes(story.agents.subject, "src/app.py"))
    result = story.agent_writes(story.agents.subject, "docs/notes.md")
    result.expect_agent_not_told(story.agents.subject, EtiquetteNudges.PLAIN_CODE)
    result = story.agent_writes(story.agents.subject, "src/app.vue")
    result.expect_agent_told(story.agents.subject, EtiquetteNudges.PLAIN_CODE)
    story.expect_stack(story.agents.subject, Ready)
