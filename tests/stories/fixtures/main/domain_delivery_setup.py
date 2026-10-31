from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.organization_fixture import OrganizationFixture


def setup_domain(story, fixture, folder_name: str, domain: str, definition: dict | None) -> None:
    folder = story.app.config.root / folder_name
    write_domain(folder, domain, definition)
    load_domain(story, folder)
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


def merge_worker(story) -> None:
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1")
    result = story.agent_runs(story.agents.subject, f"worker merge {worker}")
    result.expect_command_passed()
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)


def production_record(task: int, reference: str, artifact: str) -> dict:
    return {"action": "accept", "evidence": {"kind": "production_deployment", "result": "succeeded", "reference": reference,
            "source": "deployment pipeline", "artifact": artifact, "environment": "production", "task_ids": [task], "occurred_at": "2026-10-30T10:00:00+00:00"}}


def write_domain(folder, domain: str, definition: dict | None) -> None:
    organization = OrganizationFixture(folder).write()
    organization.domain(domain, roles=["delivery"], **({"definition_of_done": definition} if definition else {}))
    organization.role(domain, "delivery", writes=True)


def load_domain(story, folder) -> None:
    story.user_sets(OrganizationOptions.FOLDER, str(folder))
    result = story.user_presses("/journal/organization/reload", {})
    result.expect_viewer_passed()


def replace_domain_definition(story, folder_name: str, domain: str, definition: dict) -> None:
    folder = story.app.config.root / folder_name
    write_domain(folder, domain, definition)
    load_domain(story, folder)
