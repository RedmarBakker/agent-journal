# Host integration tests start provider processes and local cap hooks; run by name.
import json
from pathlib import Path

import pytest

from tests.lab.real.manifest import Manifest
from tests.lab.real.run_record_store import RunRecordStore
from tests.lab.test_real_batch import batch_manifest, isolated_batch, owner_receipt, run_real_cli


def test_run_real_runs_three_approved_runs_in_isolated_roots_and_records_each_provider_cli(
        tmp_path, monkeypatch, capsys):
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
    service, batch_folder, factory_calls, profiles, _drivers = isolated_batch(tmp_path, monkeypatch, manifest, stand_in)
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
    service, batch_folder, _factory_calls, _profiles, _drivers = isolated_batch(tmp_path, monkeypatch, manifest, stand_in)
    _approval, receipt = owner_receipt(manifest)

    assert run_real_cli(service, batch_folder, manifest, receipt) == 1

    record = RunRecordStore().read(batch_folder / "roots" / manifest.batch_id / "run-1" / "evidence" / "run-record.json")
    assert record.terminal_reason == "capped"
    ledger = json.loads((batch_folder / "run-caps.json").read_text(encoding="utf-8"))
    assert ledger["cap_reached"]["cap"] == ("run_turns" if cap == "turn" else "run_wall_minutes")
    assert ledger["runs"]["run-1"]["finished"] is True


def test_run_real_records_a_cap_reached_by_live_stand_in_cli_hooks(tmp_path, monkeypatch):
    stand_in = tmp_path / "stand-in-provider.py"
    stand_in.write_text(
        "import json, os\n"
        "from pathlib import Path\n"
        "from urllib.request import Request, urlopen\n"
        "def post(event, firing):\n"
        " body=json.dumps({'event':event,'session_id':os.environ['SESSION_ID'],'firing':firing}).encode()\n"
        " request=Request(os.environ['CAP_URL'],data=body,headers={'X-Run-Cap-Token':os.environ['CAP_TOKEN']})\n"
        " with urlopen(request,timeout=2): pass\n"
        "post('SessionStart','session-start')\n"
        "Path(os.environ['LOG_PATH']).write_text('session started')\n"
        "post('UserPromptSubmit','turn-1')\n"
        "post('UserPromptSubmit','turn-2')\n",
        encoding="utf-8",
    )
    manifest = batch_manifest(run_count=1, run_limit_changes={"run_turns": 1})
    data = manifest.data()
    data["runs"][0]["simulate_live_hook_cap"] = True
    manifest = Manifest.build(manifest.batch_id, data)
    service, batch_folder, _factory_calls, _profiles, _drivers = isolated_batch(tmp_path, monkeypatch, manifest, stand_in)
    _approval, receipt = owner_receipt(manifest)

    assert run_real_cli(service, batch_folder, manifest, receipt) == 1

    root = batch_folder / "roots" / manifest.batch_id / "run-1"
    record = RunRecordStore().read(root / "evidence" / "run-record.json")
    ledger = json.loads((batch_folder / "run-caps.json").read_text(encoding="utf-8"))
    assert (root / "home" / "cli-observation.json").read_text(encoding="utf-8") == "session started"
    assert record.terminal_reason == "capped"
    assert ledger["cap_reached"]["cap"] == "run_turns"
    assert ledger["runs"]["run-1"]["finished"] is True
