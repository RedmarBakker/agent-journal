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


@story(SkillsFeature, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_prompt_that_names_a_skills_word_holds_the_writes_until_that_skill_is_read(story):
    story.agent_is_prompted(f"please {PINS_KEYWORD} the design for me")
    story.expect_agent_told(SkillsNudges.SKILL_READ_REQUEST)
    story.agent_writes("footer.py")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(Pins.skill.folder)
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(SkillsFeature, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_journal_command_of_a_skills_noun_waits_for_that_skill(story):
    story.agent_runs_in_the_shell(f"journal {PINS_NOUN} list")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(Pins.skill.folder)
    story.agent_runs_in_the_shell(f"journal {PINS_NOUN} list")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(SkillsFeature, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_event_a_skill_names_makes_it_due_at_the_next_tool(story):
    story.user_sends_message("is the footer done?")
    story.agent_writes("footer.py")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(Messages.skill.folder)
    story.expect_allowed()
    story.expect_stack(Ready)


@story(SkillsFeature, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_chat_message_that_names_a_skills_word_holds_the_writes_once_the_agent_reads_it(story):
    message = story.user_sends_message(f"please {PINS_KEYWORD} the design for me")
    story.agent_reads_a_skill(Messages.skill.folder)
    story.agent_reads_message(message)
    story.agent_writes("footer.py")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(Pins.skill.folder)
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(SkillsFeature, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_skills_word_of_two_words_in_a_prompt_is_matched_as_a_phrase(story):
    story.user_switches_on(FlowchartsFeature)
    story.agent_is_prompted(f"draw me a {FLOWCHART_PHRASE} of the hooks")
    story.agent_writes("footer.py")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.agent_reads_a_skill(FlowchartsFeature.skill.folder)
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_stack(Ready)
