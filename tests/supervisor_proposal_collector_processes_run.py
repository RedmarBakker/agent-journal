# Starts the collector with a fake Docker CLI and never runs Docker.
import json
import os
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parents[1]
COLLECTOR = ROOT / "docs/supervisor/v1/collect-proposal-case.py"
FIXTURE = ROOT / "tests/fixtures/supervisor-proposal-evaluation/proposal-writer-rows.json"


def test_collector_records_proposal_after_launcher_stops_stack_without_bridge_file(tmp_path):
    docker_bin = tmp_path / "bin"
    docker_bin.mkdir()
    calls_path = tmp_path / "docker-arguments.json"
    fake_docker = docker_bin / "docker"
    fake_docker.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "from pathlib import Path\n"
        f"Path({str(calls_path)!r}).write_text(json.dumps(sys.argv[1:]))\n"
        f"fixture_path = __import__('os').environ.get('WRITER_ROWS_FIXTURE', {str(FIXTURE)!r})\n"
        "sys.stdout.write(json.dumps({'rows': json.loads(Path(fixture_path).read_text())}))\n"
    )
    fake_docker.chmod(0o755)
    gateway_state = tmp_path / "gateway-state"
    gateway_state.mkdir()
    env_file = tmp_path / "live-smoke.env"
    env_file.write_text(f"GATEWAY_STATE_PATH={gateway_state}\nPROFILE_REVISION=test-reviewed-revision\n")
    results = tmp_path / "results.jsonl"
    environment = {**os.environ, "PATH": f"{docker_bin}:{os.environ['PATH']}"}

    result = subprocess.run(
        [
            sys.executable,
            str(COLLECTOR),
            "PSU-02",
            "--env-file",
            str(env_file),
            "--results",
            str(results),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )

    bridge_state = gateway_state / "journal-supervisor-transport/bridge-state.json"
    assert result.returncode == 0, result.stderr
    assert not bridge_state.exists()
    assert "proposed" in result.stdout
    row = json.loads(results.read_text().splitlines()[0])
    assert row["outcome"]["result"] == "proposed"
    assert row["outcome"]["action_status"] == "proposed"
    assert row["outcome"]["owner_decision"] == "accepted"
    arguments = json.loads(calls_path.read_text())
    assert arguments[:2] == ["run", "--rm"]
    assert "--network" in arguments and arguments[arguments.index("--network") + 1] == "none"
    assert "type=volume,src=journal-supervisor-smoke_writer_state,dst=/data" in arguments
    assert "--entrypoint" in arguments
    assert arguments[arguments.index("--entrypoint") + 1] == "/usr/local/bin/supervisor-proposal-writer-rows"
    assert arguments[-1] == "agent-journal-supervisor-writer:test-reviewed-revision"
    assert "compose" not in arguments and "exec" not in arguments


def test_collector_uses_bridge_metering_for_an_unreceipted_run(tmp_path):
    docker_bin = tmp_path / "bin"
    docker_bin.mkdir()
    calls_path = tmp_path / "docker-arguments.json"
    fake_docker = docker_bin / "docker"
    fake_docker.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        f"Path({str(calls_path)!r}).write_text(json.dumps(sys.argv[1:]))\n"
        "sys.stdout.write(json.dumps({'rows': json.loads(Path(os.environ['WRITER_ROWS_FIXTURE']).read_text())}))\n"
    )
    fake_docker.chmod(0o755)
    writer_rows = tmp_path / "writer-rows.json"
    writer_rows.write_text(json.dumps([{
        "id": 80,
        "entry_type": "SupervisorRun",
        "created_at": "2026-11-06T12:00:00+00:00",
        "data": {"run_ref": "run-unreceipted", "wake_kind": "event", "event_kind": "failed_check"},
    }]))
    gateway_state = tmp_path / "gateway-state"
    transport = gateway_state / "journal-supervisor-transport"
    transport.mkdir(parents=True)
    bridge_state = transport / "bridge-state.json"
    bridge_state.write_text(json.dumps({
        "last_admission": "admitted",
        "last_error": "receipt_pending",
        "hook_status": "acknowledged",
        "active_run": {"run_id": "run-unreceipted"},
        "receipt": None,
        "metering": {
            "run_ref": {"run_id": "run-unreceipted"},
            "status": "known",
            "pending_request": None,
            "provider_requests": 4,
            "input_tokens": 100,
            "output_tokens": 20,
            "cache_creation_input_tokens": 50,
            "cache_read_input_tokens": 25,
        },
    }))
    finished_at = datetime.fromisoformat("2026-11-06T12:00:30+00:00").timestamp()
    os.utime(bridge_state, (finished_at, finished_at))
    env_file = tmp_path / "live-smoke.env"
    env_file.write_text(f"GATEWAY_STATE_PATH={gateway_state}\nPROFILE_REVISION=test-reviewed-revision\n")
    results = tmp_path / "results.jsonl"
    environment = {
        **os.environ,
        "PATH": f"{docker_bin}:{os.environ['PATH']}",
        "WRITER_ROWS_FIXTURE": str(writer_rows),
    }

    result = subprocess.run(
        [sys.executable, str(COLLECTOR), "PSU-05", "--env-file", str(env_file), "--results", str(results)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    row = json.loads(results.read_text().splitlines()[0])
    assert row["outcome"]["result"] == "abstained"
    assert row["outcome"]["wake_kind"] == "event"
    assert row["outcome"]["provider_requests"] == 4
    assert row["actual_cost_usd"] == "0.000605"
    assert row["latency_seconds"] == 30


def test_collector_labels_a_quiet_case_from_its_staged_wake(tmp_path):
    docker_bin = tmp_path / "bin"
    docker_bin.mkdir()
    fake_docker = docker_bin / "docker"
    fake_docker.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "json.dump({'rows': []}, sys.stdout)\n"
    )
    fake_docker.chmod(0o755)
    gateway_state = tmp_path / "gateway-state"
    transport = gateway_state / "journal-supervisor-transport"
    transport.mkdir(parents=True)
    (transport / "bridge-state.json").write_text(json.dumps({
        "last_admission": "quiet", "receipt": None, "metering": {"provider_requests": 0},
    }))
    env_file = tmp_path / "live-smoke.env"
    env_file.write_text(f"GATEWAY_STATE_PATH={gateway_state}\nPROFILE_REVISION=test-reviewed-revision\n")
    results = tmp_path / "results.jsonl"

    result = subprocess.run(
        [sys.executable, str(COLLECTOR), "PSU-23", "--env-file", str(env_file), "--results", str(results)],
        cwd=ROOT,
        env={**os.environ, "PATH": f"{docker_bin}:{os.environ['PATH']}"},
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    row = json.loads(results.read_text().splitlines()[0])
    assert row["outcome"]["wake_kind"] == "quiet"
    assert row["outcome"]["admission"] == "quiet"
