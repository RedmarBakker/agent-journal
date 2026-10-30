from journal.features.flowcharts.feature import FlowchartsFeature
from journal.features.messages.feature import Messages
from journal.features.pins.feature import Pins
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.skills_feature import SkillsFeature

PINS_KEYWORD, PINS_NOUN = Pins.skill.keywords[0], Pins.skill.commands[0]
FLOWCHART_PHRASE = next(keyword for keyword in FlowchartsFeature.skill.keywords if " " in keyword)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_prompt_that_names_a_skills_word_holds_the_writes_until_that_skill_is_read(story):
    result = story.agent_is_prompted(story.agents.subject, f"please {PINS_KEYWORD} the design for me")
    result.expect_agent_told(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(story.agents.subject, Pins.skill.folder)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_command_of_a_skills_noun_waits_for_that_skill(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal {PINS_NOUN} list")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(story.agents.subject, Pins.skill.folder)
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal {PINS_NOUN} list")
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
