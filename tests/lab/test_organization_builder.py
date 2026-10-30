import hashlib
import tomllib
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.organization import Organization
from tests.lab.business_type import BusinessType
from tests.lab.organization_builder import OrganizationBuilder
from tests.test_features import booted
from tests.user_settings import USER_CALLER, user_set

BUSINESS_TYPES = Path(__file__).parent / "business_types"


@pytest.fixture(scope="module")
def boot():
    return booted


def test_software_company_generates_and_loads_with_the_journal_contract_reader(app, tmp_path):
    business_type = BusinessType.read(BUSINESS_TYPES / "software_company.toml")
    with pytest.raises(FrozenInstanceError):
        business_type.title = "Changed"
    with pytest.raises(TypeError):
        business_type.roles[0]["title"] = "Changed"

    folder = OrganizationBuilder().build(business_type, tmp_path / business_type.id)
    user_set(app, "workers.organization_folder", str(folder))
    result = app.console().run(["organization", "reload"], USER_CALLER)

    assert result.code == 0, result.error
    contracts = app.container.get(Organization).contracts()
    assert not contracts.problems
    assert len(contracts.domains) == 6
    assert len(contracts.roles) == 12
    assert {domain.id for domain in contracts.domains} == {domain["id"] for domain in business_type.domains}
    assert {role.id for role in contracts.roles} == {role["id"] for role in business_type.roles}
    assert {role.cardinality for role in contracts.roles} == {Cardinality.JOURNAL, Cardinality.PLAN, Cardinality.MANY}
    assert contracts.role("privacy_officer").approval_required == (ApprovalAction.PRIVACY_DECISION,)
    assert contracts.domain("product").routing[0].role == "product_manager"
    assert contracts.domain("product").edges[0].to == "engineering"
    assert contracts.role("product_manager").edge_targets() == ("product_analyst",)
    assert "Software company" in contracts.domain("product").guidance
    assert "Product manager" in contracts.role("product_manager").guidance


@pytest.mark.parametrize(
    ("name", "expected_approvals"),
    [
        (
            "accountancy_firm",
            frozenset({
                ApprovalAction.FINANCIAL_TRANSACTION,
                ApprovalAction.INVOICE_CORRECTION,
                ApprovalAction.EMPLOYMENT_TERMS_ACTION,
                ApprovalAction.PRIVACY_DECISION,
            }),
        ),
        (
            "dental_practice",
            frozenset({
                ApprovalAction.INVOICE_CORRECTION,
                ApprovalAction.PRIVACY_DECISION,
                ApprovalAction.DATA_BREACH_DECISION,
                ApprovalAction.PEOPLE_ACTION,
                ApprovalAction.EMPLOYMENT_TERMS_ACTION,
                ApprovalAction.FINANCIAL_TRANSACTION,
            }),
        ),
        (
            "sales_company",
            frozenset({
                ApprovalAction.CONTRACT_CHANGE,
                ApprovalAction.CUSTOMER_LIABILITY_COMMITMENT,
                ApprovalAction.PRIVACY_DECISION,
                ApprovalAction.FINANCIAL_TRANSACTION,
                ApprovalAction.INVOICE_CORRECTION,
            }),
        ),
        (
            "law_firm",
            frozenset({
                ApprovalAction.LEGAL_DECISION,
                ApprovalAction.CONTRACT_CHANGE,
                ApprovalAction.PRIVACY_DECISION,
                ApprovalAction.DATA_BREACH_DECISION,
                ApprovalAction.INVOICE_CORRECTION,
                ApprovalAction.FINANCIAL_TRANSACTION,
            }),
        ),
    ],
)
def test_other_business_types_generate_and_load_with_the_journal_contract_reader(
    app, tmp_path, name, expected_approvals
):
    business_type = BusinessType.read(BUSINESS_TYPES / f"{name}.toml")
    folder = OrganizationBuilder().build(business_type, tmp_path / business_type.id)
    user_set(app, "workers.organization_folder", str(folder))
    result = app.console().run(["organization", "reload"], USER_CALLER)

    assert result.code == 0, result.error
    contracts = app.container.get(Organization).contracts()
    assert not contracts.problems
    assert len(contracts.domains) >= 5
    assert len(contracts.roles) >= 12
    assert {domain.id for domain in contracts.domains} == {domain["id"] for domain in business_type.domains}
    assert {role.id for role in contracts.roles} == {role["id"] for role in business_type.roles}
    assert {role.cardinality for role in contracts.roles} == set(Cardinality)
    assert all(domain.routing for domain in contracts.domains)
    assert any(domain.edges for domain in contracts.domains)
    assert any(role.edges for role in contracts.roles)
    assert {action for role in contracts.roles for action in role.approval_required} == expected_approvals


def test_fleet_operator_matches_the_pinned_source_and_loads_with_the_journal_contract_reader(
    app, tmp_path
):
    path = BUSINESS_TYPES / "fleet_operator.toml"
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    source = raw["source"]
    business_type = BusinessType.read(path)
    manifest = "\n".join(
        f"{role['domain']}/{role['id']}"
        for role in sorted(business_type.roles, key=lambda item: (item["domain"], item["id"]))
    )

    assert source["repository"] == "agentic-organization-journal"
    assert source["commit"] == "d53649b71ad1c0faf536d6299ec95de159ed6c4f"
    assert source["role_manifest_sha256"] == hashlib.sha256(manifest.encode()).hexdigest()

    folder = OrganizationBuilder().build(business_type, tmp_path / business_type.id)
    user_set(app, "workers.organization_folder", str(folder))
    result = app.console().run(["organization", "reload"], USER_CALLER)

    assert result.code == 0, result.error
    contracts = app.container.get(Organization).contracts()
    assert not contracts.problems
    assert len(contracts.domains) == 13
    assert len(contracts.roles) == 50
    assert {domain.id for domain in contracts.domains} == {domain["id"] for domain in business_type.domains}
    assert {role.id for role in contracts.roles} == {role["id"] for role in business_type.roles}
    actual_roles = sorted(
        (
            role.domain,
            role.id,
            role.cardinality.value,
            role.writes,
            tuple(sorted(action.value for action in role.approval_required)),
        )
        for role in contracts.roles
    )
    expected_roles = sorted(
        (
            role["domain"],
            role["id"],
            role["cardinality"],
            role["writes"],
            tuple(sorted(role["approval_required"])),
        )
        for role in business_type.roles
    )
    assert actual_roles == expected_roles
    assert {role.cardinality for role in contracts.roles} == set(Cardinality)
