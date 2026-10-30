from journal.features.flowcharts.feature import FlowchartsFeature
from journal.features.messages.feature import Messages
from journal.features.pins.feature import Pins
from journal.features.questions.states.waiting import Waiting
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.skills_feature import SkillsFeature

PINS_KEYWORD = Pins.skill.keywords[0]
FLOWCHART_PHRASE = next(keyword for keyword in FlowchartsFeature.skill.keywords if " " in keyword)
# words of everyday work that once made a skill due and name no subject of the journal's
QUESTION_ASK = "journal question ask 'which footer?' --options 'The agent writes the short one' 'The agent writes the long one'"
EVERYDAY_PROMPT = "send the footer to review, decide on the design options and choose the steps"


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_prompt_holds_the_writes_for_a_skill_it_names_by_its_subject_never_by_everyday_words(story):
    result = story.agent_is_prompted(story.agents.subject, EVERYDAY_PROMPT)
    result.expect_agent_not_told(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    result = story.agent_is_prompted(story.agents.subject, f"please {PINS_KEYWORD} the design for me")
    result.expect_agent_told(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(story.agents.subject, Pins.skill.folder)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_event_a_skill_names_makes_it_due_at_the_next_tool(story):
    story.user_sends_message("is the footer done?")
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    result = story.agent_reads_a_skill(story.agents.subject, Messages.skill.folder)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_chat_message_that_names_a_skills_word_holds_the_writes_once_the_agent_reads_it(story):
    message = story.user_sends_message(f"please {PINS_KEYWORD} the design for me")
    story.agent_reads_a_skill(story.agents.subject, Messages.skill.folder)
    story.agent_reads_message(story.agents.subject, message)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(story.agents.subject, Pins.skill.folder)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_skills_word_of_two_words_in_a_prompt_is_matched_as_a_phrase(story):
    story.user_switches_on(FlowchartsFeature)
    story.agent_is_prompted(story.agents.subject, f"draw me a {FLOWCHART_PHRASE} of the hooks")
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(story.agents.subject, FlowchartsFeature.skill.folder)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_command_of_a_skills_noun_waits_for_that_skill_so_a_question_waits_for_messages_then_on_the_user(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, QUESTION_ASK)
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    result.expect_agent_told_words(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST, "the messages skill")
    story.agent_reads_a_skill(story.agents.subject, Messages.skill.folder)
    story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.expect_stack(story.agents.subject, Ready, Waiting)
