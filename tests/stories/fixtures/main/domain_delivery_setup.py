from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.workers.organization_options import OrganizationOptions
from tests.organization_fixture import OrganizationFixture


def setup_domain(story, fixture, folder_name: str, domain: str, definition: dict | None) -> None:
    folder = story.app.config.root / folder_name
    organization = OrganizationFixture(folder).write()
    organization.domain(domain, roles=["delivery"], **({"definition_of_done": definition} if definition else {}))
    organization.role(domain, "delivery", writes=True)
    story.user_sets(OrganizationOptions.FOLDER, str(folder))
    result = story.user_presses("/journal/organization/reload", {})
    result.expect_viewer_passed()
    story.user_sets(EstimatesOptions.MODE, "record")
    fixture.domain_folder = folder


def add_domain_plan(story, fixture, domain: str) -> None:
    fixture.plans.first = story.user_creates_plan(f"{domain} delivery", "a scoped delivery commitment")
    result = story.user_presses(f"/journal/plans/{fixture.plans.first}/tasks", {"title": "deliver the output", "brief": "- the output is ready", "domain": domain})
    result.expect_viewer_passed()
    fixture.tasks.first = result.viewer_answer["id"]


def report_worker(story, fixture) -> None:
    fixture.workers.first = story.agent_dispatches_worker_on_plan(story.agents.main, "Lady Lovelace", fixture.plans.first)
    story.agent_starts_a_session(story.agents.workers.first())
    story.agent_clocks_in(story.agents.workers.first())
    story.agent_proves(story.agents.workers.first(), 1, "src/release.py:4, the scoped output passes")
    story.agent_clocks_out(story.agents.workers.first(), "the scoped output is ready")
