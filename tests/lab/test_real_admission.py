from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from journal.support.actor import Actor
from journal.support.caller import ACTOR_TOKEN
from tests.lab.real.batch_approval import BatchApproval
from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.isolation_evidence import IsolationEvidence
from tests.lab.real.manifest import Manifest
from tests.lab.real.real_run import RealRun
from tests.lab.real.run_caps import RunCaps
from tests.lab.real.run_record import RunRecord
from tests.lab.real.run_record_store import RunRecordStore


def run_caps(**changes):
    return {"state": "selected", "run_wall_minutes": 10, "run_sessions": 2, "run_concurrent_sessions": 1,
            "turns_per_session": 4, "run_turns": 6, "max_usd": "unknown", "unknown_cost_accepted": True, **changes}


def batch_caps(**changes):
    return {"state": "selected", "batch_run_count": 1, "batch_session_count": 2, "batch_turns": 6,
            "batch_run_minutes": 10, "batch_elapsed_minutes": 20, "batch_max_usd": "unknown",
            "unknown_cost_accepted": True, "approval_valid_until": 300, **changes}


def manifest(run=None, batch=None):
    selected = run or run_caps()
    resources = batch or batch_caps()
    return Manifest.build("batch-1", {"run_ids": ["run-1"], "runs": [{"id": "run-1", "scenario": "tracker_outage",
        "business_type": "fleet_operator", "design_digest": "design", "seed": 17, "journal_commit": "j1",
        "organization_commit": "o1", "provider": "claude", "model": "sonnet", "metric_schema_version": "1"}],
        "run_caps": {"run-1": selected}, "batch_caps": resources, "providers": [{"provider": "claude", "model": "sonnet"}]})


def watchdog(stop_result=True):
    armed, stopped = [], []
    return SimpleNamespace(armed=armed, stopped=stopped,
                           arm=lambda owner, deadline: armed.append((owner, deadline)) or True,
                           stop=lambda owner, reason: stopped.append((owner, reason)) or stop_result)


def boundary_for(run_id, denied_writes=0, escaped_writes=0):
    state = {}

    def evidence(paths, denied=0, escaped=0):
        writable = tuple(sorted(str(paths[key].resolve()) for key in ("project", "private_home", "runtime", "tmp")))
        return IsolationEvidence(run_id, str(paths["root"].resolve()), writable, f"scope-{run_id}", f"observer-{run_id}",
                                 True, True, True, True, denied, escaped)

    def verify(actual_run_id, paths):
        if actual_run_id != run_id:
            raise ValueError("boundary run id changed")
        state["paths"] = paths
        return evidence(paths)

    def observe(actual_run_id):
        if actual_run_id != run_id:
            raise ValueError("observer run id changed")
        return evidence(state["paths"], denied_writes, escaped_writes)

    return SimpleNamespace(verify=verify, observe=observe)


def test_real_caps_reserve_each_request_once_and_keep_unknown_cost_separate_from_resource_caps(tmp_path):
    pending = run_caps(state="owner_pending")
    with pytest.raises(ValueError, match="owner_pending"):
        RunCaps("run-1", pending, batch_caps(), tmp_path / "pending.json")

    watcher = watchdog()
    ledger = tmp_path / "batch.json"
    caps = RunCaps("run-1", run_caps(), batch_caps(), ledger, watcher, clock=lambda: 100)
    caps.reserve_run()
    caps.arm_watchdog()
    caps.start_session("session-1")
    first = caps.reserve_request("request-1", "session-1", input_tokens=20, output_tokens=10)
    resumed = RunCaps("run-1", run_caps(), batch_caps(), ledger, watcher, clock=lambda: 100)
    resumed.reserve_run()
    resumed.start_session("session-1")
    assert resumed.reserve_request("request-1", "session-1", 20, 10) == first
    assert len(resumed.read()["runs"]["run-1"]["requests"]) == 1, "a replayed request consumes no second turn"
    with pytest.raises(ValueError, match="cannot change its reservation"):
        resumed.reserve_request("request-1", "session-1", 21, 10)
    with pytest.raises(ValueError, match="reserved maximum charge"):
        resumed.reserve_request("request-1", "session-1", 20, 10, maximum_usd="0.25")
    assert len(watcher.armed) == 2, "the independent batch and run deadlines are armed"


def test_real_caps_stop_at_turn_limits_and_quarantine_when_the_owned_stop_is_unconfirmed(tmp_path):
    watcher = watchdog(stop_result=False)
    run = run_caps(run_turns=1, turns_per_session=1)
    caps = RunCaps("run-1", run, batch_caps(), tmp_path / "caps.json", watcher, clock=lambda: 100)
    caps.reserve_run()
    caps.arm_watchdog()
    caps.start_session("session-1")
    caps.reserve_request("request-1", "session-1")
    with pytest.raises(ValueError, match="provider turn cap reached"):
        caps.reserve_request("request-2", "session-1")
    state = caps.read()
    assert state["cap_reached"]["cap"] == "run_turns" and state["quarantined"], "an unconfirmed stop quarantines the batch"
    assert watcher.stopped == [("run-1", "provider turn cap reached")]


def test_watchdog_admission_rolls_back_partial_arms_and_quarantines_unconfirmed_cleanup(tmp_path):
    armed, stopped = [], []
    watcher = SimpleNamespace(
        arm=lambda owner, deadline: armed.append(owner) or (len(armed) == 1),
        stop=lambda owner, reason: stopped.append(owner) or False,
    )
    caps = RunCaps("run-1", run_caps(), batch_caps(), tmp_path / "watchdog.json", watcher, clock=lambda: 100)
    with pytest.raises(ValueError, match="did not confirm its deadline"):
        caps.arm_watchdog()
    state = caps.read()
    batch_owner = f"batch:{tmp_path.name}"
    assert armed == [batch_owner, "run-1"] and stopped == ["run-1", batch_owner]
    assert state["quarantined"] and "active_run" not in state, "partial watchdog startup is rolled back or quarantined"


def test_a_hard_dollar_cap_requires_a_provider_enforced_request_bound(tmp_path):
    caps = RunCaps("run-1", run_caps(max_usd="1.00"), batch_caps(batch_max_usd="2.00"), tmp_path / "caps.json", watchdog(), clock=lambda: 100)
    caps.reserve_run()
    caps.arm_watchdog()
    caps.start_session("session-1")
    with pytest.raises(ValueError, match="provider-enforced maximum charge"):
        caps.reserve_request("request-1", "session-1")
    assert caps.read()["quarantined"], "an unenforceable selected USD cap closes the batch"


def test_request_receipts_are_idempotent_and_cannot_change_after_settlement(tmp_path):
    caps = RunCaps("run-1", run_caps(max_usd="1.00"), batch_caps(batch_max_usd="2.00"),
                   tmp_path / "receipts.json", watchdog(), clock=lambda: 100)
    caps.reserve_run()
    caps.arm_watchdog()
    caps.start_session("session-1")
    caps.reserve_request("request-1", "session-1", maximum_usd="0.50")
    caps.settle_request("request-1", "0.40", "completed")
    caps.settle_request("request-1", "0.400", "completed")
    with pytest.raises(ValueError, match="cannot change its receipt"):
        caps.settle_request("request-1", "0.41", "completed")


def test_zero_dollar_provider_charge_is_a_valid_settlement(tmp_path):
    caps = RunCaps("run-1", run_caps(max_usd="1.00"), batch_caps(batch_max_usd="2.00"),
                   tmp_path / "zero-charge.json", watchdog(), clock=lambda: 100)
    caps.reserve_run()
    caps.arm_watchdog()
    caps.start_session("session-1")
    caps.reserve_request("request-1", "session-1", maximum_usd="0.50")

    caps.settle_request("request-1", "0.00", "completed")

    assert caps.read()["runs"]["run-1"]["requests"]["request-1"]["actual_usd"] == "0.00"


def test_a_provider_charge_over_its_reservation_stops_and_quarantines_the_batch(tmp_path):
    watcher = watchdog()
    caps = RunCaps("run-1", run_caps(max_usd="1.00"), batch_caps(batch_max_usd="2.00"),
                   tmp_path / "charge.json", watcher, clock=lambda: 100)
    caps.reserve_run()
    caps.arm_watchdog()
    caps.start_session("session-1")
    caps.reserve_request("request-1", "session-1", maximum_usd="0.50")
    with pytest.raises(ValueError, match="exceeded its reserved maximum"):
        caps.settle_request("request-1", "0.60", "completed")
    assert caps.read()["quarantined"] and watcher.stopped[-1][0] == "run-1"


def test_batch_approval_uses_authenticated_owner_identity_and_the_exact_manifest(tmp_path):
    key = b"owner signing key with at least thirty two bytes"
    approval = BatchApproval(1, key)
    batch = manifest()
    with pytest.raises(ValueError, match="only the authenticated owner"):
        approval.approve(batch, Actor.agent("worker-58"), 200, 100)
    receipt = approval.approve(batch, Actor.user(1), 200, 100)
    approval.verify(batch, receipt, "run-1", Actor.user(1), 150)
    with pytest.raises(ValueError, match="only the authenticated owner"):
        approval.verify(batch, receipt, "run-1", Actor.agent("worker-58"), 150)
    path = tmp_path / "approval.json"
    approval.save(receipt, path)
    assert path.stat().st_mode & 0o777 == 0o600 and key.decode() not in path.read_text(), "the receipt is private and contains no signing secret"
    changed = manifest(run=run_caps(run_turns=5))
    with pytest.raises(ValueError, match="does not match"):
        approval.verify(changed, receipt, "run-1", Actor.user(1), 150)
    with pytest.raises(ValueError, match="expired"):
        approval.verify(batch, receipt, "run-1", Actor.user(1), 201)


def test_owner_pending_caps_cannot_be_approved_even_by_the_owner():
    approval = BatchApproval(1, b"owner signing key with at least thirty two bytes")
    pending = manifest(run=run_caps(state="owner_pending"))
    with pytest.raises(ValueError, match="owner_pending"):
        approval.approve(pending, Actor.user(1), 200, 100)


def test_isolated_journal_refuses_overlapping_reused_and_symlink_roots(tmp_path):
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    overlapping = IsolatedJournal(checkout / "lab", checkout)
    with pytest.raises(ValueError, match="overlaps protected"):
        overlapping.run_root("batch-1", "run-1")

    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    isolated = IsolatedJournal(lab_home, checkout)
    boundary = boundary_for("run-1")
    isolated.prepare("batch-1", "run-1", boundary)
    with pytest.raises(ValueError, match="never reused"):
        isolated.prepare("batch-1", "run-1", boundary)

    alias = tmp_path / "lab-alias"
    alias.symlink_to(lab_home, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        IsolatedJournal(alias, checkout).run_root("batch-1", "run-2")


def test_isolated_journal_refuses_a_public_batch_parent(tmp_path):
    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    roots = lab_home / "roots"
    roots.mkdir(mode=0o700)
    roots.chmod(0o755)
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    with pytest.raises(ValueError, match="private to their owner"):
        IsolatedJournal(lab_home, checkout).prepare("batch-1", "run-1", boundary_for("run-1"))


def test_isolated_journal_refuses_a_boolean_instead_of_os_boundary_evidence(tmp_path):
    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    isolated = IsolatedJournal(lab_home, checkout)
    with pytest.raises(ValueError, match="structured isolation evidence"):
        isolated.prepare("batch-1", "run-1", SimpleNamespace(verify=lambda *_: True))


def test_isolated_journal_rejects_a_wrong_endpoint_challenge(tmp_path):
    root = tmp_path / "run"
    identity = {"root": str((root / "project" / ".journal").resolve()), "run_id": "run-1",
                "launch_id": "launch-1", "challenge": "challenge-1", "pid": 22,
                "host": "127.0.0.1", "port": 9100, "authenticated": True}
    IsolatedJournal.verify_identity(identity, root, "run-1", "launch-1", "challenge-1", 9100)
    with pytest.raises(ValueError, match="identity does not match"):
        IsolatedJournal.verify_identity(identity, root, "run-1", "launch-1", "different-challenge", 9100)


def test_isolated_child_environment_drops_parent_journal_identity_and_uses_private_paths(tmp_path):
    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    isolated = IsolatedJournal(lab_home, checkout)
    paths = isolated.prepare("batch-1", "run-1", boundary_for("run-1"))
    source = paths["project"] / "src"
    source.mkdir()
    (source / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    shim = isolated.install_journal_shim(paths, 9100)
    assert shim.is_file() and shim.stat().st_mode & 0o777 == 0o700
    host = {"LANG": "en_US.UTF-8", "JOURNAL_ROOT": "/parent", "JOURNAL_PORT": "8420",
            ACTOR_TOKEN: "parent-token", "CLAUDE_CODE_SESSION": "parent-session", "ANTHROPIC_API_KEY": "provider-key"}
    env = isolated.child_environment(paths, host, ("LANG", "JOURNAL_ROOT", "JOURNAL_PORT", ACTOR_TOKEN),
                                     ("CLAUDE_CODE_SESSION",), ("ANTHROPIC_API_KEY",), 9100,
                                     "worker:1", "fresh-token", ())
    assert env["JOURNAL_ROOT"] == str(paths["project"].resolve()) and env["JOURNAL_PORT"] == "9100"
    assert env[ACTOR_TOKEN] == "fresh-token" and env["HOME"] == str(paths["private_home"].resolve())
    assert "CLAUDE_CODE_SESSION" not in env and env["ANTHROPIC_API_KEY"] == "provider-key"


def test_isolated_environment_drops_shell_and_python_startup_injection_even_when_allowlisted(tmp_path):
    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    isolated = IsolatedJournal(lab_home, checkout)
    paths = isolated.prepare("batch-1", "run-1", boundary_for("run-1"))
    source = paths["project"] / "src"
    source.mkdir()
    (source / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    isolated.install_journal_shim(paths, 9100)
    host = {"BASH_ENV": "/tmp/host.sh", "PYTHONPATH": "/tmp/host-python", "LANG": "C"}
    env = isolated.child_environment(paths, host, ("BASH_ENV", "PYTHONPATH", "LANG"), (), (), 9100,
                                     "worker:1", "fresh-token", ())
    assert env["LANG"] == "C" and "BASH_ENV" not in env and "PYTHONPATH" not in env


def test_real_run_records_setup_failure_without_starting_a_provider_when_isolation_is_unproven(tmp_path):
    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    isolated = IsolatedJournal(lab_home, checkout)
    now = datetime.now(timezone.utc).timestamp()
    batch = manifest(batch=batch_caps(approval_valid_until=now + 3600))
    approvals = BatchApproval(1, b"owner signing key with at least thirty two bytes")
    receipt = approvals.approve(batch, Actor.user(1), now + 1800, now)
    driver = SimpleNamespace(calls=[])
    caps = RunCaps("run-1", run_caps(), batch_caps(approval_valid_until=now + 3600),
                   lab_home / "reservations.json", watchdog(), clock=lambda: 100)
    record = RealRun(isolated, approvals, driver, RunRecordStore()).run(batch, receipt, Actor.user(1), "run-1", 1, caps, None)
    evidence = lab_home / "roots" / "batch-1" / "run-1" / "evidence" / "setup-failed.json"
    assert record.terminal_reason == "setup_failed" and evidence.is_file(), "isolation refusal is retained as a setup result"
    assert (evidence.parent / "run-record.json").is_file(), "the full setup result is persisted for later reporting"
    assert driver.calls == [], "an unproven boundary blocks scenario loading and every provider launch"


@pytest.mark.parametrize(("escaped_writes", "terminal_reason"), ((0, "completed"), (1, "faulted")))
def test_real_run_persists_isolation_counts_journal_record_and_outside_worktree_delta(tmp_path, escaped_writes, terminal_reason):
    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    isolated = IsolatedJournal(lab_home, checkout)
    now = datetime.now(timezone.utc).timestamp()
    batch = manifest(batch=batch_caps(approval_valid_until=now + 3600))
    approvals = BatchApproval(1, b"owner signing key with at least thirty two bytes")
    receipt = approvals.approve(batch, Actor.user(1), now + 1800, now)
    records = RunRecordStore()
    changes = iter(((), ("outside.txt",)))
    base = RunRecord("run-1", 1, "tracker_outage", "fleet_operator", "design", 17, batch.digest,
                     "j1", "o1", "claude", "sonnet", "1", "completed", 0.0)
    def materialize_project(spec, paths):
        source = paths["project"] / "src"
        source.mkdir()
        (source / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        return {"journal_commit": spec["journal_commit"], "organization_commit": spec["organization_commit"],
                "journal_port": 9100}

    driver = SimpleNamespace(
        materialize_project=materialize_project,
        start_journal=lambda paths, shim, run_id, launch_id, challenge, port, _caps: {
            "root": str((paths["project"] / ".journal").resolve()), "run_id": run_id,
            "launch_id": launch_id, "challenge": challenge, "pid": 321, "host": "127.0.0.1",
            "port": port, "authenticated": True,
        },
        load_scenario=lambda _scenario, _paths: "scenario",
        outside_worktree_changes=lambda _paths: next(changes),
        start_plan=lambda _scenario, _paths, _caps: 41,
        wait_for_end_or_cap=lambda _run, _plan, _caps: "completed",
        stop_owned=lambda _run: True,
        read_record=lambda _run: base,
        plan_commits_reached_main=lambda _plan, _paths: True,
    )
    selected_batch_caps = batch_caps(approval_valid_until=now + 3600)
    caps = RunCaps("run-1", run_caps(), selected_batch_caps,
                   lab_home / "reservations.json", watchdog(), clock=lambda: 100)
    boundary = boundary_for("run-1", denied_writes=2, escaped_writes=escaped_writes)
    record = RealRun(isolated, approvals, driver, records).run(batch, receipt, Actor.user(1), "run-1", 1, caps, boundary)
    saved = records.read(lab_home / "roots" / "batch-1" / "run-1" / "evidence" / "run-record.json")
    assert record == saved and record.plan_commits_reached_main is True and record.terminal_reason == terminal_reason
    assert record.journal_pid == 321 and record.launch_id, "the record identifies the challenged journal endpoint"
    assert record.denied_write_count == 2 and record.escaped_write_count == escaped_writes
    assert record.isolation_verified is (escaped_writes == 0)
    shim = lab_home / "roots" / "batch-1" / "run-1" / "home" / "bin" / "journal"
    contents = shim.read_text()
    assert str(lab_home / "roots" / "batch-1" / "run-1" / "project") in contents and "JOURNAL_PORT=9100" in contents
    if escaped_writes:
        assert caps.read()["quarantined"], "an observed write escape quarantines the batch"
    assert record.outside_worktree_changes == ("outside.txt",), "only writes added during the run are reported"


def test_real_run_refuses_a_project_snapshot_with_different_approved_commits(tmp_path):
    lab_home = (tmp_path / "lab").resolve()
    lab_home.mkdir(mode=0o700)
    lab_home.chmod(0o700)
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    isolated = IsolatedJournal(lab_home, checkout)
    now = datetime.now(timezone.utc).timestamp()
    batch = manifest(batch=batch_caps(approval_valid_until=now + 3600))
    approvals = BatchApproval(1, b"owner signing key with at least thirty two bytes")
    receipt = approvals.approve(batch, Actor.user(1), now + 1800, now)
    calls = []
    driver = SimpleNamespace(
        materialize_project=lambda _spec, _paths: {"journal_commit": "wrong", "organization_commit": "o1", "journal_port": 9100},
        start_journal=lambda *_: calls.append("journal-start"),
        load_scenario=lambda *_: calls.append("scenario-load"),
        start_plan=lambda *_: calls.append("plan-start"),
        stop_owned=lambda _run: True,
    )
    selected_batch_caps = batch_caps(approval_valid_until=now + 3600)
    caps = RunCaps("run-1", run_caps(), selected_batch_caps,
                   lab_home / "reservations.json", watchdog(), clock=lambda: 100)
    record = RealRun(isolated, approvals, driver, RunRecordStore()).run(
        batch, receipt, Actor.user(1), "run-1", 1, caps, boundary_for("run-1"))
    assert record.terminal_reason == "setup_failed" and calls == [], "an unapproved source snapshot cannot start a journal or plan"


def test_manifest_rejects_provider_credentials_under_environment_variable_names():
    with pytest.raises(ValueError, match="credential field"):
        Manifest.build("batch-1", {"ANTHROPIC_API_KEY": "plaintext"})
