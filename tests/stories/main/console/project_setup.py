import json

from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

MINE = {"hooks": [{"type": "command", "command": "echo mine"}]}


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_setup_wires_the_hooks_the_skills_and_the_law_and_keeps_the_projects_own_rules(story):
    story.project_file_holding("AGENTS.md", "# my project\n\nMy own rules.\n")
    result = story.user_types("setup")
    result.expect_command_text("hooks   .claude/settings.local.json")
    story.expect_project_file(".claude/settings.local.json", "SessionStart", "MessageDisplay", "hook.sh claude")
    story.expect_project_file(".claude/skills/journal/SKILL.md", "a worker writes for you on one task")
    story.expect_project_file(".claude/skills/journal-workers/SKILL.md", "journal worker check")
    story.expect_project_file(".claude/agents/journal-researcher.md", "name: journal-researcher")
    story.expect_project_file("AGENTS.md", "# my project", "My own rules.", "L9 - A subagent only reads", "L10 - A worker's work is merged only once")
    story.expect_project_file("CLAUDE.md", "@AGENTS.md")
    story.expect_project_file(".gitignore", "/.journal", "/.claude/settings.local.json")
    story.expect_project_file("home/.local/bin/journal", ".journal/src/journal.sh", ".journal/journal")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_setup_run_twice_changes_nothing_the_second_time_and_keeps_the_users_own_hooks(story):
    story.project_file_holding(".claude/settings.local.json", json.dumps({"hooks": {"PreToolUse": [MINE]}, "theme": "dark"}))
    story.user_types("setup")
    first = story.project_text(".claude/settings.local.json")
    story.user_types("setup")
    story.expect_project_file_is(".claude/settings.local.json", first)
    story.expect_project_file(".claude/settings.local.json", "echo mine", '"theme": "dark"')
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_setup_wires_codex_where_its_folder_exists(story):
    story.project_file_holding(".codex/config.toml", "")
    result = story.user_types("setup")
    result.expect_command_text("hooks   .codex/hooks.json")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_setup_takes_out_version_3s_hooks_wherever_they_were_wired_and_keeps_the_users_own(story):
    old = {"hooks": [{"type": "command", "command": f"sh {story.project_root()}/.journal/src/hook.sh claude {story.project_root()}/.journal"}]}
    story.project_file_holding(".claude/settings.local.json", json.dumps({"hooks": {"PreToolUse": [old, MINE]}, "model": "opus"}))
    story.project_file_holding(".codex/hooks.json", json.dumps({"hooks": {"Stop": [old]}}))
    story.user_types("setup")
    story.expect_project_file_without(".claude/settings.local.json", "/.journal/src/hook.sh")
    story.expect_project_file(".claude/settings.local.json", "echo mine", '"model": "opus"')
    story.expect_project_file_without(".codex/hooks.json", "/.journal/src/hook.sh")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_setup_takes_the_journals_hooks_another_machine_committed_out_of_the_shared_settings_and_wires_this_machines_own(story):
    elsewhere = "/Users/someone-else/code/app/.journal/src/journal/hooks/hook.sh"
    committed = {"hooks": [{"type": "command", "command": f"test -f {elsewhere} && exec sh {elsewhere} claude /Users/someone-else/code/app; exit 0"}]}
    story.project_file_holding(".claude/settings.json", json.dumps({"hooks": {"SessionStart": [committed], "PreToolUse": [MINE]}, "theme": "dark"}))
    result = story.user_types("setup")
    result.expect_command_text("hooks   .claude/settings.local.json")
    story.expect_project_file_without(".claude/settings.json", "someone-else")
    story.expect_project_file(".claude/settings.json", "echo mine", '"theme": "dark"')
    story.expect_project_file(".claude/settings.local.json", "SessionStart", "hook.sh claude", str(story.project_root()))
    story.expect_stack(story.agents.subject, Ready)
