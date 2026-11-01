from tests.stories.fixtures.main.organization_shared_role_domain_seat_started import OrganizationSharedRoleDomainSeatStarted


class OrganizationSharedRoleGitProject(OrganizationSharedRoleDomainSeatStarted):
    """A shared Role project has a clean target Git checkout."""

    parent = OrganizationSharedRoleDomainSeatStarted

    def steps(self, story) -> None:
        root = story.app.config.root
        story.project_is_a_git_repository()
        story.git_in(root, "config", "user.name", "Story")
        story.git_in(root, "config", "user.email", "story@example.com")
        (root / ".gitignore").write_text("/.journal/\n/.agents/\n/.claude/\n")
        (root / "OTHER.md").write_text("the starting file\n")
        story.git_in(root, "add", ".gitignore", "OTHER.md")
        story.git_in(root, "commit", "-q", "--amend", "--allow-empty", "-m", "start")

