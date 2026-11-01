from subprocess import CompletedProcess

from journal.console.support.project_update_commit import ProjectUpdateCommit
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


def simulate_git(story, changed=(), repository=True, staged_before=()):
    service = story.app.container.get(ProjectUpdateCommit)
    staged = set(staged_before)
    commits = []
    changed = set(changed)

    def git(*arguments):
        if arguments[:2] == ("rev-parse", "--show-toplevel"):
            return CompletedProcess(arguments, 0 if repository else 128, "project\n" if repository else "", "")
        if arguments[0] == "check-ignore":
            return CompletedProcess(arguments, 1, "", "")
        if arguments[0] == "add":
            separator = arguments.index("--") if "--" in arguments else len(arguments)
            selected = set(arguments[separator + 1:]) if separator < len(arguments) else changed
            staged.update(changed & selected)
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
        return CompletedProcess(arguments, 0, "", "")

    story.monkeypatch.setattr(service, "git", git)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_commits_its_changed_skills_in_one_release_named_commit(story):
    release = "v4.8.2"
    skill = ".agents/skills/journal/SKILL.md"
    story.monkeypatch.setenv("JOURNAL_UPDATE_REF", release)
    story.project_file_holding(skill, "old installed skill\n")
    story.project_file_holding("notes.md", "the user's dirty file\n")
    simulate_git(story, (skill, "notes.md"), staged_before=("notes.md",))

    result = story.user_types("setup")

    result.expect_command_passed()
    result.expect_command_lines_holding(f"update commit: Update the journal to {release}", 1)
    result.expect_command_text(f"update commit: Update the journal to {release} ({skill})")
    result.expect_command_text_without("notes.md")
    story.expect_project_file_without(skill, "old installed skill")
    story.expect_project_file_is("notes.md", "the user's dirty file\n")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_with_no_changed_installed_files_makes_no_commit(story):
    story.monkeypatch.setenv("JOURNAL_UPDATE_REF", "v4.8.2")
    story.project_file_holding("notes.md", "the user's dirty file\n")
    simulate_git(story, ("notes.md",))

    result = story.user_types("setup")

    result.expect_command_text_without("update commit:")
    story.expect_project_file_is("notes.md", "the user's dirty file\n")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_update_in_a_project_without_git_does_not_commit(story):
    story.monkeypatch.setenv("JOURNAL_UPDATE_REF", "v4.8.2")
    simulate_git(story, repository=False)

    result = story.user_types("setup")

    result.expect_command_text_without("update commit:")
    story.expect_stack(story.agents.subject, Ready)
