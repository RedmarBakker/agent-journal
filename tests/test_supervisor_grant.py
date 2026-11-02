import pytest

from journal.models.supervisor_grant import BUDGET_FIELDS, SupervisorGrant


CATALOGUE = {
    "task create": ("plans-and-tasks", 1),
    "task start": ("plans-and-tasks", 2),
    "plan approve": ("plans-and-tasks", 3),
    "check create": ("checks", 1),
    "check remove": ("checks", 3),
    "secret delete": ("secrets", "never"),
}


def grant_data(**changes):
    data = {
        "owner_user_id": 7,
        "environment_id": 12,
        "watched_plans": "all",
        "capabilities": {
            "task create": {"on": True, "mode": "act"},
            "area:checks": {"on": False, "mode": "propose"},
        },
        "wake_interval_minutes": 15,
        "event_wakeups": ["failed_check", "stalled_task"],
        "limits": dict.fromkeys(BUDGET_FIELDS, 1),
        "valid_until_ms": 1000,
        "revoked": False,
    }
    data.update(changes)
    return data


def test_a_grant_stores_environment_scope_plans_capabilities_wakes_limits_and_lifetime():
    value = grant_data(watched_plans=[4, 9], wake_interval_minutes=60, revoked=True)

    grant = SupervisorGrant.parsed(value, CATALOGUE)

    assert grant.data() == value, "the frozen grant stores its watched plans, capability switches, wake settings, limits, expiry and revoked state"


def test_a_version_one_grant_migrates_to_one_version_two_environment_grant():
    legacy = {
        "owner_user_id": 7,
        "driver_environment_id": 12,
        "plan_id": 4,
        "capabilities": {
            "diagnostic_task": True, "plan_priorities": True, "check_interval": True,
            "sequence": False, "phrase_nudge": False, "project_reminder": False,
        },
        "mode": "shadow",
        "limits": dict.fromkeys(BUDGET_FIELDS, 1),
        "valid_until_ms": 1000,
        "revoked": False,
    }

    grant = SupervisorGrant.from_version_one(legacy)

    assert grant.environment_id == 12 and grant.watched_plans == (4,), "migration binds the old plan to its driver environment"
    assert grant.capabilities == (
        ("check edit", True, "propose"), ("plan priorities", True, "propose"), ("task create", True, "propose"),
    ), "the three version 1 capabilities convert to their catalogue commands with the same mode"


def test_a_grant_refuses_a_capability_mode_above_its_safety_tier():
    value = grant_data(capabilities={"plan approve": {"on": True, "mode": "act"}})

    with pytest.raises(ValueError, match="tier"):
        SupervisorGrant.parsed(value, CATALOGUE)


def test_a_grant_refuses_unknown_or_never_capabilities_when_enabled():
    for selector in ("task imaginary", "secret delete"):
        value = grant_data(capabilities={selector: {"on": True, "mode": "propose"}})
        with pytest.raises(ValueError):
            SupervisorGrant.parsed(value, CATALOGUE)


def test_a_grant_refuses_unknown_areas_and_unsupported_wakeups():
    with pytest.raises(ValueError, match="area"):
        SupervisorGrant.parsed(grant_data(capabilities={"area:unlisted": {"on": False, "mode": "propose"}}), CATALOGUE)
    with pytest.raises(ValueError, match="wake"):
        SupervisorGrant.parsed(grant_data(event_wakeups=["task_changed"]), CATALOGUE)


def test_a_grant_refuses_wake_intervals_outside_the_three_choices():
    for interval in (5, 20, 90):
        with pytest.raises(ValueError, match="wake"):
            SupervisorGrant.parsed(grant_data(wake_interval_minutes=interval), CATALOGUE)


def test_a_grant_requires_one_daily_cost_limit_and_unique_plan_ids():
    duplicate_cost = grant_data(limits={**dict.fromkeys(BUDGET_FIELDS, 1), "daily_cost_usd": 1})
    duplicate_plans = grant_data(watched_plans=[4, 4])

    with pytest.raises(ValueError, match="limit"):
        SupervisorGrant.parsed(duplicate_cost, CATALOGUE)
    with pytest.raises(ValueError, match="plan"):
        SupervisorGrant.parsed(duplicate_plans, CATALOGUE)
