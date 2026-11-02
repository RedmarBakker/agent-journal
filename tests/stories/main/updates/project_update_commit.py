from subprocess import CompletedProcess

from journal.console.support.project_update_commit import ProjectUpdateCommit
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


def simulate_git(story, changed=(), repository=True, staged_before=(), head_files=None, rejected_contents=None, expected_contents=None, expected_missing=(), ignored=(), tracked=()):
    staged = set(staged_before)
    commits = []
    changed = set(changed)
    head_files = head_files or {}
    rejected_contents = rejected_contents or {}
    expected_contents = expected_contents or {}
    expected_missing = set(expected_missing)
    ignored = set(ignored)
    tracked = set(tracked)

    def git(_service, *arguments, given=""):
        if arguments[:2] == ("rev-parse", "--show-toplevel"):
            return CompletedProcess(arguments, 0 if repository else 128, "project\n" if repository else "", "")
        if arguments[0] == "show" and arguments[1].startswith("HEAD:"):
            path = arguments[1].removeprefix("HEAD:")
            return CompletedProcess(arguments, 0, head_files[path], "") if path in head_files else CompletedProcess(arguments, 128, "", "missing path")
        if arguments[0] == "ls-files":
            path = arguments[-1]
            return CompletedProcess(arguments, 0 if path in tracked else 1, path if path in tracked else "", "")
        if arguments[0] == "check-ignore":
            selected = set(path for path in given.split("\0") if path)
            found = sorted(selected & ignored)
            return CompletedProcess(arguments, 0 if found else 1, "\0".join(found) + ("\0" if found else ""), "")
        if arguments[0] == "add":
            separator = arguments.index("--") if "--" in arguments else len(arguments)
            selected = set(arguments[separator + 1:]) if separator < len(arguments) else changed
            staged.update((changed & selected) if "-f" in arguments else (changed & selected) - ignored)
            return CompletedProcess(arguments, 0, "", "")
        if arguments[:2] == ("diff", "--cached") and "--name-only" in arguments:
            separator = arguments.index("--") if "--" in arguments else len(arguments)
            selected = set(arguments[separator + 1:])
            found = sorted(staged & selected)
            return CompletedProcess(arguments, 0, "\0".join(found) + ("\0" if found else ""), "")
        if arguments[0] == "commit":
            commits.append(arguments)
            selected = set(arguments[arguments.index("--") + 1:]) if "--" in arguments else set()
            if "--only" not in arguments or len(commits) > 1 or selected & set(staged_before):
                return CompletedProcess(arguments, 1, "", "the update included a file already staged by the user")
            for path, forbidden in rejected_contents.items():
                file = story.app.config.root / path
                forbidden = (forbidden,) if isinstance(forbidden, str) else forbidden
                if path in selected and file.is_file() and any(part in file.read_text() for part in forbidden):
                    return CompletedProcess(arguments, 1, "", f"the update included user text from {path}")
            for path in expected_missing:
                if path in selected and (story.app.config.root / path).exists():
                    return CompletedProcess(arguments, 1, "", f"the update did not remove {path}")
            for path, contents in expected_contents.items():
                file = story.app.config.root / path
                if path in selected and (not file.is_file() or any(part not in file.read_text() for part in contents)):
                    return CompletedProcess(arguments, 1, "", f"the update did not commit the journal change to {path}")
        return CompletedProcess(arguments, 0, "", "")

    story.monkeypatch.setattr(ProjectUpdateCommit, "git", git)


def update_identity(story, release="agentic-organization"):
    story.monkeypatch.setenv("JOURNAL_UPDATE_REF", release)
    story.project_file_holding(".journal/src/commit", "9aa0fef971a4\n")


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_commits_its_changed_skills_in_one_release_named_commit(story):
    release = "v4.8.2"
    skill = ".agents/skills/journal/SKILL.md"
    update_identity(story, release)
    story.project_file_holding(skill, "old installed skill\n")
    story.project_file_holding("notes.md", "the user's dirty file\n")
    simulate_git(story, (skill, "notes.md"), staged_before=("notes.md",))

    result = story.user_types("setup")

    result.expect_command_passed()
    result.expect_command_lines_holding(f"update commit: Update the journal to {release}", 1)
    result.expect_command_text(f"update commit: Update the journal to {release} at 9aa0fef ({skill})")
    result.expect_command_text_without("notes.md")
    story.expect_project_file_without(skill, "old installed skill")
    story.expect_project_file_is("notes.md", "the user's dirty file\n")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_with_no_changed_installed_files_makes_no_commit(story):
    update_identity(story, "v4.8.2")
    story.project_file_holding("notes.md", "the user's dirty file\n")
    simulate_git(story, ("notes.md",))

    result = story.user_types("setup")

    result.expect_command_text_without("update commit:")
    story.expect_project_file_is("notes.md", "the user's dirty file\n")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_in_a_project_without_git_does_not_commit(story):
    update_identity(story, "v4.8.2")
    simulate_git(story, repository=False)

    result = story.user_types("setup")

    result.expect_command_text_without("update commit:")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_commits_a_skill_removed_from_both_agent_homes(story):
    update_identity(story)
    skills = (
        ".agents/skills/journal-questions/SKILL.md",
        ".claude/skills/journal-questions/SKILL.md",
    )
    for skill in skills:
        story.project_file_holding(skill, "---\nname: journal-questions\n---\nold skill\n")
    simulate_git(story, skills, expected_missing=skills, ignored=skills, tracked=skills)

    result = story.user_types("setup")

    result.expect_command_passed()
    result.expect_command_text("update commit: Update the journal to agentic-organization at 9aa0fef (" + ", ".join(skills) + ")")
    for skill in skills:
        story.expect_no_project_file(skill)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_commits_the_changed_shared_hooks_settings(story):
    update_identity(story)
    settings = ".claude/settings.json"
    local = ".claude/settings.local.json"
    story.project_file_holding(settings, '{"theme":"dark","hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"journal/hooks/hook.sh"}]}]}}\n')
    story.project_file_holding(local, '{"theme":"local"}\n')
    baseline = '{"theme":"light","hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"journal/hooks/hook.sh"}]}]}}\n'
    simulate_git(story, (settings, local), head_files={settings: baseline}, rejected_contents={settings: ('"theme": "dark"', "journal/hooks/hook.sh")}, expected_contents={settings: ('"theme": "light"',)}, ignored=(settings, local))

    result = story.user_types("setup")

    result.expect_command_passed()
    result.expect_command_text("update commit: Update the journal to agentic-organization at 9aa0fef (" + settings + ")")
    story.expect_project_file(settings, '"theme": "dark"')
    story.expect_project_file_without(settings, "journal/hooks/hook.sh")
    story.expect_project_file(local, '"theme": "local"')
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_commits_its_claude_block_without_the_users_other_text(story):
    update_identity(story)
    imports = "CLAUDE.md"
    user_text = "The user's own note stays outside the journal block."
    story.project_file_holding(imports, f"# Project instructions\n{user_text}\n")
    simulate_git(story, (imports,), head_files={imports: "# Project instructions\n"}, rejected_contents={imports: user_text}, expected_contents={imports: ("@AGENTS.md",)})

    result = story.user_types("setup")

    result.expect_command_passed()
    result.expect_command_text("update commit: Update the journal to agentic-organization at 9aa0fef (CLAUDE.md)")
    story.expect_project_file(imports, user_text, "@AGENTS.md")
    story.expect_stack(story.agents.subject, Ready)
