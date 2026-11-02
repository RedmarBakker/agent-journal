import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from types import SimpleNamespace

import pytest

from journal.support.actor import Actor
from tests.lab.real.approval_receipt import ApprovalReceipt
from tests.lab.real.batch_approval import BatchApproval
from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.isolation_evidence import IsolationEvidence
from tests.lab.real.manifest import Manifest
from tests.lab.real.run_record import RunRecord
from tests.lab.real.run_record_store import RunRecordStore
from tests.lab.real.run_real_batch import RunRealBatch
from tests.lab.__main__ import main


OWNER_KEY = b"real lab owner signing key with at least thirty two bytes"
JOURNAL_COMMIT = "a" * 40
ORGANIZATION_COMMIT = "b" * 40
ACTIVE_RUNNER_SERVICE = None
RUNNER_FACTORY_CALLS = 0


def selected_caps(**changes):
    return {
        "state": "selected",
        "run_wall_minutes": 1,
        "run_sessions": 4,
        "run_concurrent_sessions": 2,
        "turns_per_session": 4,
        "run_turns": 8,
        **changes,
    }


def batch_manifest(run_count=3, run_limit_changes=None):
    run_ids = [f"run-{index}" for index in range(1, run_count + 1)]
    runs = []
    for index, run_id in enumerate(run_ids):
        provider = "claude" if index != 1 else "codex"
        model = "opus" if provider == "claude" else "gpt-6.1-sol"
        runs.append({
            "id": run_id,
            "scenario": f"scenario-{index + 1}",
            "business_type": "software_company",
            "design_digest": "design-digest",
            "seed": 1,
            "journal_commit": JOURNAL_COMMIT,
            "organization_commit": ORGANIZATION_COMMIT,
            "provider": provider,
            "model": model,
            "metric_schema_version": "business-plan-v1",
        })
    run_caps = {run_id: selected_caps(**(run_limit_changes or {})) for run_id in run_ids}
    batch_caps = {
        "state": "selected",
        "batch_run_count": run_count,
        "batch_session_count": run_count * 4,
        "batch_turns": run_count * 8,
        "batch_run_minutes": run_count,
        "batch_elapsed_minutes": run_count + 1,
        "approval_valid_until": time.time() + 3600,
    }
    return Manifest.build("batch-1", {
        "billing_mode": "subscription",
        "run_ids": run_ids,
        "runs": runs,
        "run_caps": run_caps,
        "batch_caps": batch_caps,
        "providers": [
            {"provider": "claude", "authentication": "signed_in_cli", "models": ["opus"]},
            {"provider": "codex", "authentication": "signed_in_cli", "models": ["gpt-6.1-sol"]},
        ],
    })


def owner_receipt(manifest):
    approval = BatchApproval(1, OWNER_KEY)
    now = time.time()
    receipt = approval.approve(manifest, Actor.user(1), now + 1800, now)
    return approval, receipt


def isolation_boundary(run_id, paths):
    writable = tuple(sorted(str(paths[key].resolve()) for key in ("project", "private_home", "runtime", "tmp")))
    evidence = IsolationEvidence(run_id, str(paths["root"].resolve()), writable,
                                 f"scope-{run_id}", f"observer-{run_id}", True, True, True, True)
    return evidence


def isolated_batch(tmp_path, monkeypatch, manifest, stand_in):
    batch_folder = tmp_path / "batch"
    batch_folder.mkdir(mode=0o700)
    profiles = {}
    for provider, variable in (("claude", "CLAUDE_CONFIG_DIR"), ("codex", "CODEX_HOME")):
        profile = tmp_path / f"{provider}-profile"
        profile.mkdir()
        monkeypatch.setenv(variable, str(profile))
        profiles[provider] = profile
    journal = IsolatedJournal(batch_folder, Path(__file__).resolve().parents[2])
    factory_calls = []
    drivers = {}
    active = SimpleNamespace(driver=None)

    def watchdog_arm(owner, deadline):
        driver = drivers.get(owner)
        if driver:
            driver.deadline = deadline
        return True

    def watchdog_stop(owner, reason):
        driver = active.driver if owner.startswith("batch:") else drivers.get(owner)
        return True if driver is None else driver.stop(driver.run_id, reason)

    watchdog = SimpleNamespace(arm=watchdog_arm, stop=watchdog_stop)

    def driver_factory(run_id, spec):
        driver = SimpleNamespace(run_id=run_id, spec=spec, process=None, session_id=f"session-{run_id}", caps=None,
                                 deadline=None, timer=None)
        drivers[run_id] = driver
        factory_calls.append(run_id)

        def materialize_project(selected, paths):
            source = paths["project"] / "src"
            source.mkdir()
            (source / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            return {"journal_commit": selected["journal_commit"],
                    "organization_commit": selected["organization_commit"], "journal_port": 9100}

        def start_journal(paths, shim, current_run_id, launch_id, challenge, port, caps):
            driver.caps = caps
            active.driver = driver
            return {"root": str((paths["project"] / ".journal").resolve()), "run_id": current_run_id,
                    "launch_id": launch_id, "challenge": challenge, "pid": os.getpid(),
                    "host": "127.0.0.1", "port": port, "authenticated": True}

        def start_plan(_scenario, paths, caps):
            caps.start_session(driver.session_id)
            child = journal.child_environment(
                paths,
                {"PATH": os.environ.get("PATH", ""), "LANG": "C", "ANTHROPIC_API_KEY": "must-not-pass",
                 "OPENAI_API_KEY": "must-not-pass"},
                ("PATH", "LANG", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"), (), 9100,
                "worker:1", "fresh-token", (),
            )
            log = paths["private_home"] / "cli-observation.json"
            child.update({"LOG_PATH": str(log), "RUN_ID": driver.run_id, "PROVIDER": driver.spec["provider"],
                         "SCENARIO": driver.spec["scenario"]})
            driver.process = subprocess.Popen([sys.executable, str(stand_in)], cwd=paths["project"], env=child,
                                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL, start_new_session=True)
            driver.log = log
            driver.paths = paths
            if driver.spec.get("simulate_time_cap"):
                def expire():
                    try:
                        caps.refuse_at_cap(caps.read(), "run_wall_minutes", "run wall-time cap reached")
                    except ValueError:
                        return

                driver.timer = threading.Timer(max(0.001, driver.deadline - time.monotonic()), expire)
                driver.timer.start()
            return f"plan-{driver.run_id}"

        def wait_for_end_or_cap(current_run_id, _plan_id, caps):
            try:
                caps.reserve_request(f"turn-{current_run_id}-1", driver.session_id, input_tokens=1, output_tokens=1)
                caps.settle_request(f"turn-{current_run_id}-1", None, "completed")
                if driver.spec.get("simulate_turn_cap"):
                    caps.reserve_request(f"turn-{current_run_id}-2", driver.session_id, input_tokens=1, output_tokens=1)
                driver.process.wait(timeout=2)
                caps.finish_session(driver.session_id)
                if caps.read().get("cap_reached"):
                    return "capped"
                return "completed"
            except ValueError as failure:
                if "cap reached" not in str(failure):
                    raise
                return "capped"

        def stop(owner, _reason):
            if driver.timer:
                driver.timer.cancel()
            if owner == run_id and driver.process and driver.process.poll() is None:
                os.killpg(driver.process.pid, 15)
                driver.process.wait(timeout=2)
            return True

        def read_record(current_run_id):
            return RunRecord(current_run_id, 1, spec["scenario"], spec["business_type"], spec["design_digest"],
                             spec["seed"], manifest.digest, spec["journal_commit"], spec["organization_commit"],
                             spec["provider"], spec["model"], spec["metric_schema_version"], "completed", 0.0)

        driver.materialize_project = materialize_project
        driver.start_journal = start_journal
        driver.load_scenario = lambda _scenario, _paths: spec
        driver.start_plan = start_plan
        driver.wait_for_end_or_cap = wait_for_end_or_cap
        driver.stop_owned = lambda current_run_id: stop(current_run_id, "run finished")
        driver.read_record = read_record
        driver.plan_commits_reached_main = lambda _plan, _paths: True
        driver.outside_worktree_changes = lambda _paths: ()
        driver.stop = stop
        return driver

    def boundary_factory(run_id):
        return SimpleNamespace(
            verify=lambda current_run_id, paths: isolation_boundary(current_run_id, paths),
            observe=lambda current_run_id: isolation_boundary(
                current_run_id, journal.paths(batch_folder / "roots" / manifest.batch_id / current_run_id)
            ),
        )

    approval, _receipt = owner_receipt(manifest)
    service = RunRealBatch(
        approval, journal, driver_factory, boundary_factory,
        RunRecordStore(), batch_folder / "run-caps.json", watchdog, clock=time.monotonic,
    )
    return service, batch_folder, factory_calls, profiles


def cli_runner_factory(manifest, approvals, lab_home):
    global ACTIVE_RUNNER_SERVICE, RUNNER_FACTORY_CALLS
    RUNNER_FACTORY_CALLS += 1
    if ACTIVE_RUNNER_SERVICE is None or lab_home != ACTIVE_RUNNER_SERVICE.journal.lab_home:
        raise ValueError("test real-run adapter does not match the approved batch folder")
    ACTIVE_RUNNER_SERVICE.approvals = approvals
    return ACTIVE_RUNNER_SERVICE


def run_real_cli(service, batch_folder, manifest, receipt, receipt_missing=False):
    global ACTIVE_RUNNER_SERVICE, RUNNER_FACTORY_CALLS
    ACTIVE_RUNNER_SERVICE = service
    RUNNER_FACTORY_CALLS = 0
    manifest_path = batch_folder / "manifest.json"
    manifest_document = manifest.data()
    manifest_document["batch_id"] = manifest.batch_id
    manifest_path.write_text(json.dumps(manifest_document), encoding="utf-8")
    manifest_path.chmod(0o600)
    receipt_path = batch_folder / "owner-receipt.json"
    if not receipt_missing:
        receipt_document = {
            "batch_id": receipt.batch_id,
            "manifest_digest": receipt.manifest_digest,
            "run_ids": list(receipt.run_ids),
            "resources_digest": receipt.resources_digest,
            "providers_digest": receipt.providers_digest,
            "expires_at": receipt.expires_at,
            "owner_id": receipt.owner_id,
            "signature": receipt.signature,
        }
        receipt_path.write_text(json.dumps(receipt_document), encoding="utf-8")
        receipt_path.chmod(0o600)
    key_path = batch_folder / "owner.key"
    key_path.write_bytes(OWNER_KEY)
    key_path.chmod(0o600)
    return main([
        "run-real", "--manifest", str(manifest_path), "--receipt", str(receipt_path),
        "--owner-key", str(key_path), "--runner", "tests.lab.test_real_batch:cli_runner_factory",
    ])


def test_run_real_runs_three_approved_runs_in_isolated_roots_and_records_each_provider_cli(tmp_path, monkeypatch, capsys):
    stand_in = tmp_path / "stand-in-provider.py"
    stand_in.write_text(
        "import json, os\n"
        "from pathlib import Path\n"
        "Path(os.environ['LOG_PATH']).write_text(json.dumps({\n"
        " 'run_id': os.environ['RUN_ID'], 'provider': os.environ['PROVIDER'],\n"
        " 'scenario': os.environ['SCENARIO'], 'cwd': os.getcwd(),\n"
        " 'claude_profile': os.environ.get('CLAUDE_CONFIG_DIR'),\n"
        " 'codex_profile': os.environ.get('CODEX_HOME'),\n"
        " 'api_key_present': any(name in os.environ for name in ('ANTHROPIC_API_KEY','OPENAI_API_KEY'))\n"
        "}))\n",
        encoding="utf-8",
    )
    manifest = batch_manifest()
    service, batch_folder, factory_calls, profiles = isolated_batch(tmp_path, monkeypatch, manifest, stand_in)
    _approval, receipt = owner_receipt(manifest)

    assert run_real_cli(service, batch_folder, manifest, receipt) == 0
    records = [RunRecordStore().read(batch_folder / "roots" / manifest.batch_id / run_id / "evidence" / "run-record.json")
               for run_id in manifest.data()["run_ids"]]
    assert [line for line in capsys.readouterr().out.splitlines() if line.endswith("run-record.json")] == [
        str(batch_folder / "roots" / manifest.batch_id / run_id / "evidence" / "run-record.json")
        for run_id in manifest.data()["run_ids"]
    ]

    assert [record.terminal_reason for record in records] == ["completed"] * 3
    assert factory_calls == ["run-1", "run-2", "run-3"]
    for record in records:
        root = batch_folder / "roots" / manifest.batch_id / record.run_id
        saved = RunRecordStore().read(root / "evidence" / "run-record.json")
        call = json.loads((root / "home" / "cli-observation.json").read_text(encoding="utf-8"))
        assert saved.terminal_reason == "completed" and saved.run_id == record.run_id
        assert call["cwd"] == str((root / "project").resolve())
        assert call["api_key_present"] is False
        if record.provider == "claude":
            assert call["claude_profile"] == str(profiles["claude"])
            assert call["codex_profile"] is None
        else:
            assert call["codex_profile"] == str(profiles["codex"])
            assert call["claude_profile"] is None


@pytest.mark.parametrize("cap", ("turn", "time"))
def test_run_real_stops_and_records_a_run_that_exceeds_its_turn_or_time_cap(tmp_path, monkeypatch, cap):
    stand_in = tmp_path / "stand-in-provider.py"
    stand_in.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
    limit_changes = {"run_turns": 1} if cap == "turn" else {"run_wall_minutes": 0.001}
    manifest = batch_manifest(run_count=1, run_limit_changes=limit_changes)
    data = manifest.data()
    data["runs"][0][f"simulate_{cap}_cap"] = True
    manifest = Manifest.build(manifest.batch_id, data)
    service, batch_folder, _factory_calls, _profiles = isolated_batch(tmp_path, monkeypatch, manifest, stand_in)
    _approval, receipt = owner_receipt(manifest)

    assert run_real_cli(service, batch_folder, manifest, receipt) == 1

    record = RunRecordStore().read(batch_folder / "roots" / manifest.batch_id / "run-1" / "evidence" / "run-record.json")
    assert record.terminal_reason == "capped"
    ledger = json.loads((batch_folder / "run-caps.json").read_text(encoding="utf-8"))
    assert ledger["cap_reached"]["cap"] == ("run_turns" if cap == "turn" else "run_wall_minutes")
    assert ledger["runs"]["run-1"]["finished"] is True


@pytest.mark.parametrize("receipt_state", ("missing", "expired"))
def test_run_real_refuses_a_missing_or_expired_receipt_before_any_provider_starts(tmp_path, monkeypatch, capsys, receipt_state):
    stand_in = tmp_path / "stand-in-provider.py"
    stand_in.write_text("raise SystemExit('provider must not start')\n", encoding="utf-8")
    manifest = batch_manifest(run_count=1)
    service, batch_folder, factory_calls, _profiles = isolated_batch(tmp_path, monkeypatch, manifest, stand_in)
    _approval, receipt = owner_receipt(manifest)
    provided = None if receipt_state == "missing" else ApprovalReceipt(
        receipt.batch_id, receipt.manifest_digest, receipt.run_ids, receipt.resources_digest,
        receipt.providers_digest, time.time() - 1, receipt.owner_id, receipt.signature,
    )

    status = run_real_cli(service, batch_folder, manifest, provided, receipt_missing=receipt_state == "missing")

    assert status == 2
    assert "approval" in capsys.readouterr().err.lower() or receipt_state == "missing"
    assert RUNNER_FACTORY_CALLS == 0
    assert factory_calls == []
    assert not (batch_folder / "roots").exists()
    assert not (batch_folder / "run-caps.json").exists()
