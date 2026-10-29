from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

SKILL = "release-notes"
SKILL_TEXT = "---\nname: release-notes\n---\nWrite the release notes.\n"
EXAMPLE_TEXT = "One line per change.\n"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_skill_folder_published_to_the_library_imports_with_every_file_intact(story):
    story.the_project_holds_a_skill(SKILL, {"SKILL.md": SKILL_TEXT, "examples/short.md": EXAMPLE_TEXT})
    story.user_connects_to_a_library()
    story.user_types(f"library publish skill {SKILL} --note first")
    story.expect_command_passed()
    story.the_skill_folder_is_removed(SKILL)
    story.user_types(f"library import skill {SKILL}")
    story.expect_command_passed()
    story.expect_project_file_is(f".claude/skills/{SKILL}/SKILL.md", SKILL_TEXT)
    story.expect_project_file_is(f".claude/skills/{SKILL}/examples/short.md", EXAMPLE_TEXT)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_skill_is_never_published_to_the_library(story):
    story.user_connects_to_a_library()
    story.user_types("library publish skill journal")
    story.expect_command_refused()
    story.expect_command_text("the journal's own skills")
    story.expect_stack(story.agents.subject, Ready)
