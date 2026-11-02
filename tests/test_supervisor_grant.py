import json

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
        "paused": False,
        "revoked": False,
    }
    data.update(changes)
    return data


def test_a_grant_stores_environment_scope_plans_capabilities_wakes_limits_and_lifetime():
    value = grant_data(watched_plans=[4, 9], wake_interval_minutes=60, paused=True, revoked=True)

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


def test_an_owner_can_allow_a_tier_three_capability_to_act():
    value = grant_data(capabilities={"plan approve": {"on": True, "mode": "act"}})

    grant = SupervisorGrant.parsed(value, CATALOGUE)

    assert grant.data() == value, "a tier three action can act only after the owner explicitly sets its grant mode"


def test_an_area_switch_does_not_choose_the_mode_of_each_verb():
    value = grant_data(capabilities={
        "area:plans-and-tasks": {"on": True, "mode": "act"},
        "task create": {"on": True, "mode": "propose"},
    })

    grant = SupervisorGrant.parsed(value, CATALOGUE)

    assert grant.data() == value, "an area switch may be on while each verb keeps its own safety tier and mode"


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


def test_a_database_migration_converts_each_version_one_grant_in_a_shared_environment(connection):
    from journal.db.migrations.supervisor_grants_version_two import SupervisorGrantsVersionTwo

    limits = dict.fromkeys(BUDGET_FIELDS, 3)
    limits["max_new_diagnostics_per_episode"] = 1
    grants = [
        {
            "grant_id": "first", "grant_version": 1, "owner_user_id": 7, "driver_environment_id": 12,
            "plan_id": 4, "capabilities": {"diagnostic_task": True, "plan_priorities": False,
                                             "check_interval": True},
            "mode": "shadow", "limits": limits, "valid_until_ms": 1000, "revoked": False,
        },
        {
            "grant_id": "second", "grant_version": 1, "owner_user_id": 7, "driver_environment_id": 12,
            "plan_id": 9, "capabilities": {"diagnostic_task": False, "plan_priorities": True,
                                             "check_interval": True},
            "mode": "bounded_write", "limits": limits, "valid_until_ms": 2000, "revoked": False,
        },
    ]
    for data in grants:
        connection.execute(
            "INSERT INTO entries (environment_id, entry_type, data, idempotency) VALUES (?, ?, ?, ?)",
            (12, "SupervisorGrant", json.dumps(data), data["grant_id"]),
        )

    SupervisorGrantsVersionTwo().apply(connection)

    migrated = [json.loads(row["data"]) for row in connection.all(
        "SELECT data FROM entries WHERE entry_type = 'SupervisorGrant' ORDER BY id"
    )]
    assert [grant["grant_v2"]["watched_plans"] for grant in migrated] == [[4], [9]], "each legacy grant keeps its own plan in the shared environment"
    assert [grant["grant_v2"]["environment_id"] for grant in migrated] == [12, 12], "each grant is bound to its environment"
    assert migrated[0]["grant_v2"]["capabilities"] == {
        "task create": {"on": True, "mode": "propose"},
        "plan priorities": {"on": False, "mode": "propose"},
        "check edit": {"on": True, "mode": "propose"},
    }, "the shadow grant maps the three version one capabilities to tier one proposals"
    assert migrated[1]["grant_v2"]["capabilities"] == {
        "task create": {"on": False, "mode": "act"},
        "plan priorities": {"on": True, "mode": "act"},
        "check edit": {"on": True, "mode": "act"},
    }, "the bounded write grant keeps its mode on each migrated capability"
    assert all(grant["grant_v2"]["limits"] == limits for grant in migrated), "the migration preserves every limit, including the daily cost cap"


def test_existing_version_two_grants_start_unpaused_after_the_pause_field_migration(connection):
    from journal.db.migrations.supervisor_grant_pause import SupervisorGrantPause

    grants = [
        {"grant_id": "before-pause-field", "grant_v2": {"environment_id": 12, "valid_until_ms": 1000}},
        {"grant_id": "already-paused", "grant_v2": {"environment_id": 12, "paused": True}},
    ]
    for index, data in enumerate(grants):
        connection.execute(
            "INSERT INTO entries (environment_id, entry_type, data, idempotency) VALUES (?, ?, ?, ?)",
            (12, "SupervisorGrant", json.dumps(data), str(index)),
        )

    SupervisorGrantPause().apply(connection)

    migrated = [json.loads(row["data"]) for row in connection.all(
        "SELECT data FROM entries WHERE entry_type = 'SupervisorGrant' ORDER BY id"
    )]
    assert [grant["grant_v2"]["paused"] for grant in migrated] == [False, True], "the migration enables existing grants but keeps an existing pause"
