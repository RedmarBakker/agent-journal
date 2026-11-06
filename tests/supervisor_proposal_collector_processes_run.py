# Starts the collector with a fake Docker CLI and never runs Docker.
import json
import os
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
        f"fixture_path = {str(FIXTURE)!r}\n"
        "sys.stdout.write(json.dumps({'rows': json.loads(Path(fixture_path).read_text())}))\n"
    )
    fake_docker.chmod(0o755)
    gateway_state = tmp_path / "gateway-state"
    gateway_state.mkdir()
    env_file = tmp_path / "live-smoke.env"
    env_file.write_text(f"GATEWAY_STATE_PATH={gateway_state}\n")
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
    assert arguments[0] == "compose"
    assert "run" in arguments
    assert "--rm" in arguments and "--no-deps" in arguments
    assert "--network" in arguments and arguments[arguments.index("--network") + 1] == "none"
    assert "--entrypoint" in arguments
    assert arguments[arguments.index("--entrypoint") + 1] == "/usr/local/bin/supervisor-proposal-writer-rows"
    assert arguments[-1] == "writer"
    assert "exec" not in arguments and "up" not in arguments
