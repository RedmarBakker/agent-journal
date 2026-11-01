from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from tests.stories.fixtures.main.organization_shared_role_domain_seat_started import OrganizationSharedRoleDomainSeatStarted


class OrganizationSharedRoleGitProject(OrganizationSharedRoleDomainSeatStarted):
    """A shared Role project has a clean target Git checkout."""

    parent = OrganizationSharedRoleDomainSeatStarted

    def steps(self, story) -> None:
        root = story.app.config.root
        story.project_is_a_git_repository()
        story.git_in(root, "config", "user.name", "Story")
        story.git_in(root, "config", "user.email", "story@example.com")
        (root / ".gitignore").write_text(".journal/\n")
        story.git_in(root, "add", ".gitignore")
        story.git_in(root, "commit", "-q", "--amend", "--allow-empty", "-m", "start")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
