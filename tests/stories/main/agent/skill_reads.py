from journal.features.docs.feature import DocsFeature
from journal.features.pins.feature import Pins
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.support.card_type import CardType
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.skills_feature import SkillsFeature

TOOL_SKILL, FILE_SKILL = "commandments-plain-code-words", "commandments-python-flow"


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_skill_not_the_journals_loaded_by_the_tool_or_read_as_its_file_shows_in_the_chat(story):
    story.agent_loads_a_skill(story.agents.subject, TOOL_SKILL)
    story.agent_has_read(story.agents.subject, str(story.app.config.root / ".agents/skills" / FILE_SKILL / "SKILL.md"))
    story.expect_chat_marks(CardType.SKILLS, f"Skill {TOOL_SKILL} loaded", f"Skill {FILE_SKILL} loaded")
    story.expect_stack(story.agents.subject, Ready)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_two_skills_read_at_once_are_both_held_by_the_agent(story):
    story.agent_reads_skills_at_once(story.agents.subject, Pins.skill.folder, DocsFeature.skill.folder)
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal {Pins.skill.commands[0]} list")
    result.expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal {DocsFeature.skill.commands[0]} list")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SkillsFeature, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagents_report_in_a_notification_owes_no_skill_by_its_words_while_the_users_words_still_do(story):
    story.agent_is_prompted(story.agents.subject, "<task-notification><task-id>a1</task-id><status>completed</status><result>a plan, a roadmap, a worker, a report and a doc</result></task-notification>")
    result = story.agent_writes(story.agents.subject, "notes.md")
    result.expect_allowed()
    story.agent_is_prompted(story.agents.subject, "draw me a roadmap")
    result = story.agent_writes(story.agents.subject, "notes.md")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(story.agents.subject, Ready)
