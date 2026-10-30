from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.organization import Organization
from tests.lab.business_type import BusinessType
from tests.lab.organization_builder import OrganizationBuilder
from tests.user_settings import USER_CALLER, user_set

BUSINESS_TYPES = Path(__file__).parent / "business_types"


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
