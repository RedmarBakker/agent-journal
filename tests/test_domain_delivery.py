import pytest

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.organization.support.definition_of_done import DefinitionOfDone
from journal.features.organization.support.evidence_requirement import EvidenceRequirement
from journal.features.organization.support.organization import Organization
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.delivery_records import DeliveryRecords
from journal.repositories.domain_rows import DOMAIN_LINK, DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import WORKED_LINK, Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from tests.organization_fixture import OrganizationFixture


def test_definition_of_done_digest_changes_with_its_criterion_evidence_or_target():
    original = DefinitionOfDone("Deploy the committed revision.", EvidenceRequirement.PRODUCTION_DEPLOYMENT, "production")
    same = DefinitionOfDone("Deploy the committed revision.", EvidenceRequirement.PRODUCTION_DEPLOYMENT, "production")
    changed_criterion = DefinitionOfDone("Deploy and smoke-test the revision.", EvidenceRequirement.PRODUCTION_DEPLOYMENT, "production")
    changed_evidence = DefinitionOfDone("Deploy the committed revision.", EvidenceRequirement.ACCEPTED_OUTPUT, "production")
    changed_target = DefinitionOfDone("Deploy the committed revision.", EvidenceRequirement.PRODUCTION_DEPLOYMENT, "eu-production")

    assert original.version == same.version
    assert original.version != changed_criterion.version
    assert original.version != changed_evidence.version
    assert original.version != changed_target.version


def test_task_handoffs_keep_the_planned_domain_and_append_each_domain_to_history(app):
    with app.container.get(Scope).environment(1):
        tasks, domains, links = app.container.get(Tasks), app.container.get(DomainRows), app.container.get(Links)
        task = tasks.save(Task(title="the release"), Actor.system())

        domains.task_tied(task, "development", Actor.system())
        domains.task_tied(task, "publishing", Actor.system())
        domains.task_tied(task, "operations", Actor.system())

        assert domains.planned_domain_name(task) == "development"
        assert domains.domain_names(task) == ["operations"]
        assert domains.domain_history(task) == ["development", "publishing", "operations"]

        legacy = tasks.save(Task(title="the older release"), Actor.system())
        existing_domain = domains.named("legacy-development", Actor.system())
        links.linked(Ref.build(legacy), Ref.build(existing_domain), DOMAIN_LINK, Actor.system())
        domains.task_tied(legacy, "publishing", Actor.system())

        assert domains.planned_domain_name(legacy) == "legacy-development"
        assert domains.domain_history(legacy) == ["legacy-development", "publishing"]


def test_worker_proposal_is_scoped_and_never_grants_delivery_acceptance(app, tmp_path):
    contract = OrganizationFixture(tmp_path / "organization").write()
    contract.domain("development", roles=[], definition_of_done={
        "criterion": "Deploy the committed revision successfully to production.",
        "evidence": "production_deployment",
        "target": "production",
    })
    settings = app.container.get(SettingRows)
    settings.set(OrganizationOptions.FOLDER.key, str(contract.root), Actor.system())
    settings.set(EstimatesOptions.MODE.key, "record", Actor.system())
    app.container.get(Organization).reload()
    with app.container.get(Scope).environment(1):
        plans, tasks, links, workers, domains, records = (
            app.container.get(kind) for kind in (Plans, Tasks, Links, Workers, DomainRows, DeliveryRecords)
        )
        owner = Actor.user(1)
        plan = plans.save(Plan(title="the release"), owner)
        task = tasks.save(Task(title="deploy the revision", brief="- production is updated", state=TaskState.COMPLETED), owner)
        links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), owner)
        domains.task_tied(task, "development", owner)
        worker = workers.save(Worker(name="Lady Lovelace", brief="Deploy the revision.", state=WorkerState.MERGED, merged_task=task.row_id), Actor.system())
        links.linked(Ref.build(worker), Ref.build(task), WORKED_LINK, Actor.system())
        evidence = {"kind": "production_deployment", "result": "succeeded", "reference": "release-42",
                    "source": "deployment pipeline", "artifact": "sha256:revision-42", "environment": "production",
                    "task_ids": [task.row_id], "occurred_at": "2026-10-30T10:00:00+00:00"}

        proposal = records.record(plan.row_id, {"action": "submit", "evidence": evidence}, Actor.worker(worker.row_id))
        assert records.record(plan.row_id, {"action": "submit", "evidence": evidence}, Actor.worker(worker.row_id)) == proposal
        delivery = records.show(plan.row_id)
        assert delivery["history"][0]["state"] == "proposed"
        assert delivery["delivered_task_ids"] == []
        with pytest.raises(Rejection, match="only the plan owner"):
            records.record(plan.row_id, {"action": "accept", "evidence": evidence}, Actor.user(2))
        with pytest.raises(Rejection, match="only the plan owner"):
            records.record(plan.row_id, {"action": "accept", "evidence": evidence}, Actor.worker(worker.row_id))
        accepted = records.record(plan.row_id, {"action": "accept", "evidence": evidence}, owner)
        assert accepted["state"] == "accepted"
        assert records.show(plan.row_id)["delivered_task_ids"] == [task.row_id]
        malformed = {**evidence, "source": 42}
        with pytest.raises(Rejection, match="fields must be non-empty text"):
            records.record(plan.row_id, {"action": "accept", "evidence": malformed}, owner)
        with pytest.raises(Rejection, match="assigned to every affected task"):
            records.record(plan.row_id, {"action": "submit", "evidence": evidence}, Actor.worker(worker.row_id + 1))
        assert len(records.plan_records(plan)) == 2
