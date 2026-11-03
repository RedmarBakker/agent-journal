# Host integration tests start real processes, sandbox-exec and the pinned journal server; run by name.
import json
import os
from pathlib import Path
import platform
import signal
import shlex
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace
from urllib.request import urlopen

import pytest

from tests.lab.business_type import BusinessType
from tests.lab.lab_scenario import LabScenario
from tests.lab.real.cap_event_server import CapEventServer
from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.production_boundary import ProductionBoundary, TMUX_SOCKET_PATH_LIMIT
from tests.lab.real import production_driver as production_driver_module
from tests.lab.real.production_driver import ProductionDriver
from tests.lab.real.production_watchdog import ProductionWatchdog
from tests.lab.real.run_caps import RunCaps
from tests.lab.real.run_record import RunRecord
from tests.lab.real.run_record_store import RunRecordStore


PINNED_BATCH_JOURNAL_COMMIT = "74d5a705f258e5ea8241c4f65125ed100b23d14e"
PINNED_BATCH_ORGANIZATION_COMMIT = "d53649b71ad1c0faf536d6299ec95de159ed6c4f"
BATCH_SCENARIOS = (
    ("software_company", "production_incident", "claude"),
    ("accountancy_firm", "payroll_tax_change", "codex"),
    ("dental_practice", "patient_records_breach", "claude"),
)


def real_caps(tmp_path, watchdog, **limits):
    ledger = tmp_path / "run-caps.json"
    run_caps = {
        "state": "selected", "run_wall_minutes": 1, "run_sessions": 2,
        "run_concurrent_sessions": 1, "turns_per_session": 1, "run_turns": 1,
        **limits,
    }
    batch_caps = {
        "state": "selected", "batch_run_count": 1, "batch_session_count": 2,
        "batch_turns": 2, "batch_run_minutes": 1, "batch_elapsed_minutes": 2,
    }
    caps = RunCaps("run-1", run_caps, batch_caps, ledger, watchdog, billing_mode="subscription")
    caps.reserve_run()
    caps.arm_watchdog()
    return caps, ledger


def test_stand_in_cli_session_and_turn_hooks_stop_at_cap_and_record_the_run(tmp_path):
    stop_reasons = []
    watchdog = SimpleNamespace(arm=lambda _owner, _deadline: True,
                               stop=lambda _owner, reason: stop_reasons.append(reason) or True)
    caps, ledger_path = real_caps(tmp_path, watchdog)
    server = CapEventServer(caps, "cap-token")
    port = server.start()
    stand_in = tmp_path / "stand-in-cli.py"
    outcome = tmp_path / "stand-in-result.json"
    stand_in.write_text(
        "import json, os\n"
        "from pathlib import Path\n"
        "from urllib.error import HTTPError\n"
        "from urllib.request import Request, urlopen\n"
        "def post(event, firing):\n"
        " body=json.dumps({'event':event,'session_id':'session-1','firing':firing}).encode()\n"
        " request=Request(os.environ['CAP_URL'],data=body,headers={'X-Run-Cap-Token':os.environ['CAP_TOKEN']})\n"
        " with urlopen(request,timeout=2): pass\n"
        "post('SessionStart','session-start')\n"
        "post('UserPromptSubmit','turn-1')\n"
        "try: post('UserPromptSubmit','turn-2')\n"
        "except HTTPError as error: Path(os.environ['OUTCOME']).write_text(str(error.code))\n",
        encoding="utf-8",
    )
    environment = {**os.environ, "CAP_URL": f"http://127.0.0.1:{port}/event",
                   "CAP_TOKEN": "cap-token", "OUTCOME": str(outcome)}
    try:
        completed = subprocess.run([sys.executable, str(stand_in)], env=environment, capture_output=True,
                                   text=True, timeout=10, check=False)
    finally:
        server.close()
    assert completed.returncode == 0, completed.stderr
    assert outcome.read_text(encoding="utf-8") == "409"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["cap_reached"]["cap"] == "run_turns"
    assert len(ledger["runs"]["run-1"]["requests"]) == 1
    assert stop_reasons == ["provider turn cap reached"]

    record = RunRecord("run-1", 1, "scenario", "business", "design", 1, "manifest", "a" * 40,
                       "b" * 40, "claude", "opus", "business-plan-v1", "capped", 0.1,
                       evidence=("provider turn cap reached",))
    evidence = tmp_path / "evidence"
    evidence.mkdir(mode=0o700)
    store = RunRecordStore()
    store.write(evidence, record)
    assert store.read(evidence / "run-record.json") == record


def test_pinned_source_snapshot_has_the_approved_commit_and_no_remote(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    subprocess.run(["git", "init", "--quiet", str(source)], check=True)
    subprocess.run(["git", "-C", str(source), "config", "user.name", "Lab test"], check=True)
    subprocess.run(["git", "-C", str(source), "config", "user.email", "lab@example.invalid"], check=True)
    (source / "pinned.txt").write_text("approved source\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(source), "add", "pinned.txt"], check=True)
    subprocess.run(["git", "-C", str(source), "commit", "--quiet", "-m", "pinned"], check=True)
    commit = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], capture_output=True,
                            text=True, check=True).stdout.strip()
    target = tmp_path / "private-snapshot"

    ProductionDriver.git_snapshot(source, target, commit)

    remotes = subprocess.run(["git", "-C", str(target), "remote", "-v"], capture_output=True,
                             text=True, check=True).stdout
    assert ProductionDriver.head(target) == commit
    assert (target / "pinned.txt").read_text(encoding="utf-8") == "approved source\n"
    assert (target / ".git" / "shallow").read_text(encoding="utf-8").strip() == commit
    assert not remotes.strip()


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production filesystem isolation uses macOS sandbox-exec")
def test_stand_in_cli_cannot_write_outside_its_private_run_root(tmp_path):
    root = tmp_path / "private-run"
    boundary = ProductionBoundary("run-1", (32001,),
                                  (Path(sys.executable).resolve().parent, Path(sys.prefix).resolve()))
    paths = {name: root / folder for name, folder in (
        ("root", ""), ("project", "project"), ("private_home", "home"),
        ("runtime", "runtime"), ("tmp", "tmp"),
    )}
    paths["tmp"] = boundary.tmux_tmpdir
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
    external = tmp_path / "user-project-write.txt"
    inside = paths["runtime"] / "stand-in-write.txt"
    script = paths["runtime"] / "stand-in-cli.sh"
    script.write_text(
        "#!/bin/sh\n"
        "if echo escaped > \"$1\" 2>/dev/null; then exit 2; fi\n"
        "echo denied > \"$2\"\n",
        encoding="utf-8",
    )
    boundary.verify("run-1", paths)
    policy = boundary.profile.read_text(encoding="utf-8")
    assert "network-outbound)" not in policy
    assert 'remote ip "localhost:32001"' in policy
    assert '(allow file-read* (literal "/private/var/select/sh"))' in policy

    environment = {**os.environ, "HOME": str(paths["private_home"]), "TMPDIR": str(paths["tmp"])}
    try:
        completed = subprocess.run(boundary.wrap(["/bin/sh", str(script), str(external), str(inside)]),
                                   env=environment, capture_output=True, text=True, timeout=10, check=False)

        assert completed.returncode == 0, f"{completed.stderr}\n{policy}"
        assert not external.exists()
        assert inside.read_text(encoding="utf-8").removesuffix("\n") == "denied"
        assert boundary.observe("run-1").escaped_writes == 0
    finally:
        assert boundary.close()


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production filesystem isolation uses macOS sandbox-exec")
def test_production_interpreter_starts_under_its_real_boundary(tmp_path):
    root = tmp_path / "private-run"
    driver = ProductionDriver("run-1", {"provider": "claude"}, None, tmp_path, tmp_path,
                              ProductionWatchdog())
    paths = IsolatedJournal.paths(root, driver.boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "tmp"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    virtual_environment = Path(sys.prefix).resolve()
    python_framework = Path(sys.base_prefix).resolve()

    driver.boundary.verify("run-1", paths)
    policy = driver.boundary.profile.read_text(encoding="utf-8")
    assert f'(allow file-read-metadata (literal {json.dumps(str(root.resolve()))}))' in policy
    environment = {"HOME": str(paths["private_home"]), "TMPDIR": str(paths["tmp"]),
                   "PATH": "/usr/bin:/bin", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        completed = subprocess.run(
            driver.boundary.wrap([sys.executable, "-c", "import sys; print(sys.prefix)"]),
            cwd=paths["project"], env=environment, capture_output=True, text=True, timeout=10, check=False,
        )

        assert f'(allow file-read* (literal {json.dumps(str(virtual_environment / "bin"))}))' in policy
        assert f'(allow file-read* (subpath {json.dumps(str(python_framework))}))' in policy
        assert f'(allow file-read-metadata (literal {json.dumps(str(Path.home()))}))' in policy
        assert f'(allow file-read* (literal {json.dumps(str(Path.home()))}))' not in policy
        assert f'(allow file-read* (subpath {json.dumps(str(Path.home()))}))' not in policy
        assert completed.returncode == 0, f"{completed.stderr}\n{policy}"
        assert completed.stdout.strip() == sys.prefix
    finally:
        assert driver.boundary.close()


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="process liveness isolation uses macOS sandbox-exec")
def test_sandbox_can_signal_and_inspect_its_own_child_process(tmp_path):
    root = tmp_path / "private-run"
    boundary = ProductionBoundary("run-1", (32001,),
                                  (Path(sys.executable).resolve().parent, Path(sys.prefix).resolve()))
    paths = IsolatedJournal.paths(root, boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "tmp", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    ProductionDriver.install_process_inspector(paths)
    code = (
        "import os, subprocess, sys\n"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], "
        "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
        "try:\n"
        "    os.kill(child.pid, 0)\n"
        "    result = subprocess.run(['ps', '-o', 'state=', '-p', str(child.pid)], "
        "capture_output=True, text=True, check=True)\n"
        "    if not result.stdout.strip() or result.stdout.strip().startswith('Z'):\n"
        "        raise SystemExit('the child process state was not readable')\n"
        "    print('alive')\n"
        "finally:\n"
        "    if child.poll() is None:\n"
        "        child.terminate()\n"
        "        child.wait(timeout=5)\n"
    )

    environment = {**os.environ, "HOME": str(paths["private_home"]), "TMPDIR": str(paths["tmp"]),
                   "PATH": f"{paths['bin']}:/usr/bin:/bin", "PYTHONNOUSERSITE": "1",
                   "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        boundary.verify("run-1", paths)
        policy = boundary.profile.read_text(encoding="utf-8")
        completed = subprocess.run(boundary.wrap([sys.executable, "-c", code]), cwd=paths["project"],
                                   env=environment, capture_output=True, text=True, timeout=10, check=False)

        assert '(allow signal (target same-sandbox))' in policy
        assert '(allow process-info* (target same-sandbox))' in policy
        assert completed.returncode == 0, f"{completed.stderr}\n{policy}"
        assert completed.stdout.strip() == "alive"
    finally:
        assert boundary.close()


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None
                    or shutil.which("node") is None,
                    reason="OpenRig child liveness uses macOS sandbox-exec and Node")
def test_stand_in_openrig_confirms_detached_child_liveness_under_its_real_boundary(
        tmp_path, monkeypatch):
    root = tmp_path / "private-run"
    source = Path(__file__).resolve().parents[2]
    cli_directory = tmp_path / "agent-clis"
    cli_directory.mkdir(mode=0o700)
    provider = cli_directory / "claude"
    provider.write_text(
        "#!/usr/bin/env node\n"
        "if (process.argv.includes('--version')) console.log('stand-in-claude 1.0');\n"
        "else process.exit(7);\n",
        encoding="utf-8",
    )
    provider.chmod(0o700)
    rig = cli_directory / "rig"
    rig.write_text(
        "#!/usr/bin/env node\n"
        "const fs = require('node:fs');\n"
        "const { execFileSync, spawn } = require('node:child_process');\n"
        "const path = require('node:path');\n"
        "async function start() {\n"
        "  const childCode = `process.on('SIGTERM', () => { "
        "require('node:fs').writeFileSync(process.env.OPENRIG_HOME + '/signal-received', 'stopped'); "
        "process.exit(0); }); setTimeout(() => {}, 2500)`;\n"
        "  const child = spawn(process.execPath, ['-e', childCode], "
        "{ detached: true, stdio: 'ignore' });\n"
        "  child.unref();\n"
        "  try {\n"
        "    process.kill(child.pid, 0);\n"
        "    const state = execFileSync('ps', ['-o', 'state=', '-p', String(child.pid)], "
        "{ encoding: 'utf8' }).trim();\n"
        "    if (!state || state.startsWith('Z')) throw new Error('daemon child state was not readable');\n"
        "    fs.writeFileSync(path.join(process.env.OPENRIG_HOME, 'liveness-proof'), 'alive ' + state);\n"
        "    fs.writeFileSync(path.join(process.env.OPENRIG_HOME, 'daemon.pid'), String(child.pid));\n"
        "  } finally {\n"
        "    if (!fs.existsSync(path.join(process.env.OPENRIG_HOME, 'daemon.pid'))) child.kill('SIGKILL');\n"
        "  }\n"
        "}\n"
        "async function stop() {\n"
        "  const pid = Number(fs.readFileSync(path.join(process.env.OPENRIG_HOME, 'daemon.pid'), 'utf8'));\n"
        "  process.kill(pid, 'SIGTERM');\n"
        "  let alive = true;\n"
        "  for (let attempt = 0; attempt < 100 && alive; attempt++) {\n"
        "    try {\n"
        "      process.kill(pid, 0);\n"
        "      let state = '';\n"
        "      try { state = execFileSync('ps', ['-o', 'state=', '-p', String(pid)], "
        "{ encoding: 'utf8' }).trim(); } catch { state = ''; }\n"
        "      alive = Boolean(state) && !state.startsWith('Z');\n"
        "    } catch (error) {\n"
        "      if (error.code !== 'ESRCH') throw error;\n"
        "      alive = false;\n"
        "    }\n"
        "    if (alive) await new Promise(resolve => setTimeout(resolve, 20));\n"
        "  }\n"
        "  if (alive) throw new Error('daemon child did not stop');\n"
        "  for (let attempt = 0; attempt < 100 && !fs.existsSync(path.join(process.env.OPENRIG_HOME, 'signal-received')); attempt++) "
        "await new Promise(resolve => setTimeout(resolve, 20));\n"
        "  if (!fs.existsSync(path.join(process.env.OPENRIG_HOME, 'signal-received'))) "
        "throw new Error('daemon child did not receive the stop signal');\n"
        "  fs.writeFileSync(path.join(process.env.OPENRIG_HOME, 'daemon-stopped'), 'stopped');\n"
        "}\n"
        "if (process.argv[2] !== 'daemon') process.exit(8);\n"
        "if (process.argv[3] === 'start') start().catch(error => { console.error(error); process.exitCode = 1; });\n"
        "else if (process.argv[3] === 'stop') stop().catch(error => { "
        "fs.writeFileSync(path.join(process.env.OPENRIG_HOME, 'stop-error'), String(error)); "
        "console.error(error); process.exitCode = 1; });\n"
        "else process.exit(9);\n",
        encoding="utf-8",
    )
    rig.chmod(0o700)
    tmux = cli_directory / "tmux"
    tmux.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    tmux.chmod(0o700)
    node = Path(shutil.which("node")).resolve()
    executables = {"claude": provider, "rig": rig, "tmux": tmux}
    monkeypatch.setattr(ProductionDriver, "executable", staticmethod(lambda name: executables.get(name)))
    manifest = SimpleNamespace(data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, source, source,
                              ProductionWatchdog())
    paths = IsolatedJournal.paths(root, driver.boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copytree(source / "src", paths["project"] / "src")
    (paths["project"] / "src" / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    stopped = False
    interrupted = False
    try:
        driver.boundary.verify("run-1", paths)
        IsolatedJournal.install_journal_shim(paths, driver.journal_port)
        driver.env = driver.child_environment(paths, driver.journal_port)
        assert driver.probe_agent_cli(paths) == {"provider": "claude", "version": "stand-in-claude 1.0"}
        driver.install_sigterm_handler()
        driver.start_openrig(paths)

        proof = Path(driver.env["OPENRIG_HOME"]) / "liveness-proof"
        process_inspector = paths["bin"] / "ps"
        assert proof.read_text(encoding="utf-8").startswith("alive ")
        assert (paths["bin"] / "node").resolve() == node
        assert process_inspector.is_file()
        assert process_inspector.read_text(encoding="utf-8").startswith(f"#!{sys.executable}\n")
        assert "proc_pidinfo" in process_inspector.read_text(encoding="utf-8")
        assert f'(allow process-exec (literal {json.dumps(str(process_inspector))}))' in (
            driver.boundary.profile.read_text(encoding="utf-8")
        )
        assert driver.rig_started
    finally:
        if driver.sigterm_handler is None:
            stopped = driver.stop_owned()
        elif not driver.stopped:
            try:
                handler = signal.getsignal(signal.SIGTERM)
                assert handler == driver.sigterm_handler
                handler(signal.SIGTERM, None)
            except InterruptedError:
                interrupted = True
        stopped = driver.stopped or driver.stop_owned()
        if not stopped:
            driver.boundary.close()

    assert stopped, (Path(driver.env["OPENRIG_HOME"]) / "stop-error").read_text(encoding="utf-8")
    assert interrupted
    assert (Path(driver.env["OPENRIG_HOME"]) / "daemon-stopped").read_text(encoding="utf-8") == "stopped"


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None
                    or shutil.which("node") is None,
                    reason="Node CLI probe uses macOS sandbox-exec and the installed Node interpreter")
def test_node_agent_cli_version_probe_runs_under_the_real_boundary(tmp_path, monkeypatch):
    root = tmp_path / "private-run"
    source = Path(__file__).resolve().parents[2]
    cli_directory = tmp_path / "agent-clis"
    cli_directory.mkdir()
    provider = cli_directory / "claude"
    provider.write_text(
        "#!/usr/bin/env node\n"
        "if (process.argv.includes('--version')) console.log('stand-in-node-cli 1.0');\n"
        "else process.exit(7);\n",
        encoding="utf-8",
    )
    provider.chmod(0o700)
    rig = cli_directory / "rig"
    rig.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    rig.chmod(0o700)
    tmux = cli_directory / "tmux"
    tmux.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    tmux.chmod(0o700)
    node = Path(shutil.which("node")).resolve()
    executables = {"claude": provider, "rig": rig, "tmux": tmux, "node": node}
    monkeypatch.setattr(ProductionDriver, "executable", staticmethod(lambda name: executables.get(name)))
    manifest = SimpleNamespace(data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, source, source,
                              ProductionWatchdog())
    paths = IsolatedJournal.paths(root, driver.boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copytree(source / "src", paths["project"] / "src")
    (paths["project"] / "src" / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    driver.boundary.verify("run-1", paths)
    IsolatedJournal.install_journal_shim(paths, driver.journal_port)
    driver.env = driver.child_environment(paths, driver.journal_port)

    try:
        result = driver.probe_agent_cli(paths)

        policy = driver.boundary.profile.read_text(encoding="utf-8")
        assert result == {"provider": "claude", "version": "stand-in-node-cli 1.0"}
        assert len(driver.processes) == 1
        assert (paths["runtime"] / "main-session-launcher.py").is_file()
        launch_log = paths["project"] / ".journal" / "runtime" / "supervisor.log"
        assert "ended: the supervisor's loop exited with 0" in launch_log.read_text(encoding="utf-8")
        assert (paths["bin"] / "node").resolve() == node
        assert f'(allow file-read* (literal {json.dumps(str(node))}))' in policy
        assert f'(allow file-read* (literal {json.dumps(str(Path.home()))}))' not in policy
        assert f'(allow file-read* (subpath {json.dumps(str(Path.home()))}))' not in policy
    finally:
        assert driver.stop_owned()
        assert all(process.poll() is not None for process in driver.processes)


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="tmux socket isolation uses macOS sandbox-exec")
def test_tmux_preflight_uses_a_short_run_scoped_socket_path_under_the_real_boundary(
        tmp_path, monkeypatch):
    stand_ins = tmp_path / "stand-ins"
    stand_ins.mkdir(mode=0o700)
    provider = stand_ins / "claude"
    provider.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    provider.chmod(0o700)
    rig = stand_ins / "rig"
    rig.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    rig.chmod(0o700)
    tmux = stand_ins / "tmux"
    tmux.write_text(
        "#!/bin/sh\n"
        "[ \"$1\" = -S ] && [ \"$3\" = kill-server ] && exit 0\n"
        "[ \"$1\" = -S ] && [ \"$3\" = list-sessions ] || exit 8\n"
        "physical_tmp=$(cd \"$TMUX_TMPDIR\" && pwd -P) || exit 9\n"
        "expected=\"$physical_tmp/tmux-$(id -u)/default\"\n"
        "[ \"$2\" = \"$expected\" ] || exit 10\n"
        f"socket_bytes=$(printf '%s' \"$2\" | wc -c | tr -d ' ')\n"
        f"[ \"$socket_bytes\" -lt {TMUX_SOCKET_PATH_LIMIT} ] || exit 11\n"
        "printf '%s\\n' \"$@\" > \"$TMUX_TMPDIR/preflight-argv\"\n"
        "printf '%s\\n' \"$expected\" > \"$TMUX_TMPDIR/socket-path\"\n"
        "if printf 'escaped\\n' > \"$OUTSIDE\" 2>/dev/null; then exit 12; fi\n"
        "printf 'preflight ran\\n' > \"$TMUX_TMPDIR/preflight-marker\"\n",
        encoding="utf-8",
    )
    tmux.chmod(0o700)
    executables = {"claude": provider, "rig": rig, "tmux": tmux}
    monkeypatch.setattr(ProductionDriver, "executable", staticmethod(lambda name: executables.get(name)))
    driver = ProductionDriver("run-1", {"provider": "claude"}, None, tmp_path, tmp_path,
                              ProductionWatchdog())
    paths = IsolatedJournal.paths(tmp_path / "private-run", driver.boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    (paths["project"] / "src").mkdir()
    (paths["project"] / "src" / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    driver.boundary.verify("run-1", paths)
    IsolatedJournal.install_journal_shim(paths, driver.journal_port)
    driver.env = driver.child_environment(paths, driver.journal_port)
    outside = tmp_path / "outside-write.txt"
    driver.env["OUTSIDE"] = str(outside)

    try:
        result = driver.preflight_tmux(paths)

        assert result == "ready"
        assert len(os.fsencode(str(driver.boundary.tmux_socket_path))) < TMUX_SOCKET_PATH_LIMIT
        assert driver.boundary.tmux_tmpdir == paths["tmp"]
        assert not paths["tmp"].is_symlink()
        assert (paths["tmp"] / "socket-path").read_text(encoding="utf-8").strip() == str(
            driver.boundary.tmux_socket_path
        )
        assert (paths["tmp"] / "preflight-argv").read_text(encoding="utf-8") == (
            f"-S\n{driver.boundary.tmux_socket_path}\nlist-sessions\n"
        )
        assert (paths["tmp"] / "preflight-marker").read_text(encoding="utf-8") == "preflight ran\n"
        assert not outside.exists()
        policy = driver.boundary.profile.read_text(encoding="utf-8")
        assert '(allow file-read* (literal "/private/var/select/sh"))' in policy
        runtime_tmux = paths["runtime"] / "tmux"
        runtime_tmux.mkdir()
        driver.env["TMUX_TMPDIR"] = str(runtime_tmux)
        with pytest.raises(ValueError, match="private short temporary directory"):
            driver.preflight_tmux(paths)
        assert (paths["tmp"] / "preflight-argv").read_text(encoding="utf-8") == (
            f"-S\n{driver.boundary.tmux_socket_path}\nlist-sessions\n"
        )
    finally:
        assert driver.stop_owned()
    assert not driver.boundary.tmux_mount.exists()


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production filesystem isolation uses macOS sandbox-exec")
def test_production_journal_server_answers_health_under_its_real_boundary(tmp_path, monkeypatch):
    root = tmp_path / "private-run"
    checkout = Path(__file__).resolve().parents[2]
    cli_bin = tmp_path / "stand-in-clis"
    cli_bin.mkdir(mode=0o700)
    provider = cli_bin / "claude"
    provider.write_text("#!/usr/bin/env node\n", encoding="utf-8")
    provider.chmod(0o700)
    rig = cli_bin / "rig"
    rig.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    rig.chmod(0o700)
    tmux = cli_bin / "tmux"
    tmux.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    tmux.chmod(0o700)
    node = cli_bin / "node"
    node.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    node.chmod(0o700)
    executables = {"claude": provider, "rig": rig, "tmux": tmux}
    host_which = shutil.which
    monkeypatch.setattr(production_driver_module.shutil, "which",
                        lambda name: str(node) if name == "node" else host_which(name))
    monkeypatch.setattr(ProductionDriver, "executable", staticmethod(lambda name: executables.get(name)))
    driver = ProductionDriver("run-1", {"provider": "claude"}, None, checkout, tmp_path,
                              ProductionWatchdog())
    monkeypatch.setattr(driver, "prepare_run_plan", lambda _paths: None)
    assert driver.cli_interpreters == {"node": node.resolve()}
    paths = IsolatedJournal.paths(root, driver.boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copytree(checkout / "src", paths["project"] / "src")
    driver.boundary.verify("run-1", paths)
    policy = driver.boundary.profile.read_text(encoding="utf-8")
    assert f'(allow network-bind (local ip "localhost:{driver.share_port}"))' in policy
    shim = IsolatedJournal.install_journal_shim(paths, driver.journal_port)
    interrupted = False

    try:
        driver.start_journal(paths, shim, "run-1", "launch-1", "challenge-1", driver.journal_port, None)
        assert not (paths["bin"] / "node").exists()
        with urlopen(f"http://127.0.0.1:{driver.journal_port}/journal/health", timeout=3) as response:
            assert response.status == 200
        assert (paths["project"] / ".journal" / "journal.db").is_file()
        sharing = json.loads((paths["project"] / ".journal" / "sharing.json").read_text(encoding="utf-8"))
        assert sharing["port"] == driver.share_port
    finally:
        if driver.sigterm_handler is None:
            driver.stop_owned()
        else:
            try:
                handler = signal.getsignal(signal.SIGTERM)
                assert handler == driver.sigterm_handler
                handler(signal.SIGTERM, None)
            except InterruptedError:
                interrupted = True
    assert interrupted
    assert driver.journal_process is not None and driver.journal_process.poll() is not None


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production plan-agent launch uses macOS sandbox-exec")
def test_stand_in_main_session_starts_the_approved_plan_agent_and_records_both_sessions(tmp_path, monkeypatch):
    monkeypatch.setattr(production_driver_module, "OPENRIG_STARTUP_SECONDS", 30)
    root = tmp_path / "private-run"
    checkout = Path(__file__).resolve().parents[2]
    cli_directory = tmp_path / "agent-clis"
    cli_directory.mkdir(mode=0o700)
    provider_script = cli_directory / "stand-in-provider.py"
    provider_script.write_text(
        "import json, os, signal, subprocess, sys, time\n"
        "from pathlib import Path\n"
        "if any(key in os.environ for key in ('JOURNAL_LAB_CAP_HOOK', 'JOURNAL_LAB_CAP_URL', 'JOURNAL_LAB_CAP_TOKEN')): raise SystemExit('cap token leaked into provider environment')\n"
        "if '--version' in sys.argv: print('stand-in-claude 1.0'); raise SystemExit(0)\n"
        "root = Path(os.environ['JOURNAL_ROOT'])\n"
        "temporary = Path(os.environ.get('TMPDIR', ''))\n"
        "if temporary.parent != Path('/private/tmp') or not temporary.name.startswith('jl-'): raise SystemExit('main session temp path escaped the run boundary')\n"
        "environment = os.environ['JOURNAL_ENV']\n"
        "session = 'main-stand-in-session' if environment == 'main' else 'plan-stand-in-session'\n"
        "settings = json.loads((root / '.claude' / 'settings.local.json').read_text(encoding='utf-8'))\n"
        "events = ('SessionStart',) if environment == 'main' else ('SessionStart', 'UserPromptSubmit', 'SessionEnd')\n"
        "for event in events:\n"
        " payload = json.dumps({'hook_event_name': event, 'session_id': session, 'source': 'startup'})\n"
        " command = settings['hooks'][event][0]['hooks'][0]['command']\n"
        " result = subprocess.run(['/bin/sh', '-c', command], input=payload, text=True, env=os.environ.copy(), capture_output=True, timeout=20, check=False)\n"
        " if result.returncode: raise SystemExit(result.stderr or f'hook failed: {event}')\n"
        "(root / '.journal' / 'runtime' / f'{environment}-provider-started').write_text('started', encoding='utf-8')\n"
        "if environment == 'main':\n"
        " def stop(*_):\n"
        "  (root / '.journal' / 'runtime' / 'main-provider-stopped').write_text('stopped', encoding='utf-8')\n"
        "  raise SystemExit(0)\n"
        " signal.signal(signal.SIGTERM, stop)\n"
        " while True: time.sleep(1)\n",
        encoding="utf-8",
    )
    provider = cli_directory / "claude"
    provider.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = --version ]; then echo 'stand-in-claude 1.0'; exit 0; fi\n"
        f"exec {shlex.quote(sys.executable)} {shlex.quote(str(provider_script))} \"$@\"\n",
        encoding="utf-8",
    )
    provider.chmod(0o700)
    daemon_server = (
        "from http.server import BaseHTTPRequestHandler, HTTPServer\n"
        "class Handler(BaseHTTPRequestHandler):\n"
        " def do_GET(self):\n"
        "  self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(b'{\"semver\":\"0.7.6\"}')\n"
        " def log_message(self, *_args): pass\n"
        "import sys\nHTTPServer(('127.0.0.1', int(sys.argv[1])), Handler).serve_forever()\n"
    )
    rig = cli_directory / "rig"
    rig.write_text(
        f"#!{sys.executable}\n"
        "import json, os, shutil, signal, subprocess, sys, time\n"
        "from pathlib import Path\n"
        "home = Path(os.environ['OPENRIG_HOME'])\n"
        "arguments = sys.argv[1:]\n"
        "if arguments[:2] == ['daemon', 'start']:\n"
        " port = arguments[arguments.index('--port') + 1]\n"
        f" child = subprocess.Popen([sys.executable, '-c', {daemon_server!r}, port], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)\n"
        " (home / 'daemon.pid').write_text(str(child.pid), encoding='utf-8')\n"
        "elif arguments[:2] == ['daemon', 'stop']:\n"
        " for name in ('daemon.pid', 'agent.pid'):\n"
        "  if (home / name).is_file():\n"
        "   try: os.kill(int((home / name).read_text(encoding='utf-8')), signal.SIGTERM)\n"
        "   except ProcessLookupError: pass\n"
        " time.sleep(0.1)\n"
        "elif arguments and arguments[0] == 'up':\n"
        " spec = json.loads(Path(arguments[1]).read_text(encoding='utf-8'))\n"
        " member = next(member for pod in spec['pods'] for member in pod['members'] if member['runtime'] == 'claude-code')\n"
        " environment = dict(os.environ); environment.update(member['env'])\n"
        " cli = shutil.which('claude', path=environment['PATH'])\n"
        " log = (home / 'agent.log').open('ab')\n"
        " child = subprocess.Popen([cli, '--stand-in-session', member['cwd']], cwd=member['cwd'], env=environment, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)\n"
        " log.close(); (home / 'agent.pid').write_text(str(child.pid), encoding='utf-8')\n"
        "else:\n raise SystemExit('unexpected stand-in rig arguments: ' + repr(arguments))\n",
        encoding="utf-8",
    )
    rig.chmod(0o700)
    tmux = cli_directory / "tmux"
    tmux.write_text("#!/bin/sh\n[ \"$3\" = list-sessions ] && exit 0\n[ \"$3\" = kill-server ] && exit 0\nexit 9\n", encoding="utf-8")
    tmux.chmod(0o700)
    executables = {"claude": provider, "rig": rig, "tmux": tmux}
    monkeypatch.setattr(ProductionDriver, "executable", staticmethod(lambda name: executables.get(name)))
    settings = {
        "plans.plan_agents": True,
        "workers.cost_cap_dollars": 0,
        "workers.default_plan_mode": "organization",
        "workers.domain_agent_model_tier": "contract",
        "workers.hub_route_strategy": "containment",
        "workers.organization_plan_effort": "xhigh",
        "workers.organization_plan_profile": "organization-plan-review",
        "workers.seat_cap": 4,
        "workers.shared_role_queue_order": "plans_in_turn",
    }
    manifest = SimpleNamespace(digest="stand-in-manifest", data=lambda: {"design": {"settings": settings}})
    spec = {
        "provider": "claude", "business_type": "software_company", "scenario": "production_incident",
        "journal_commit": PINNED_BATCH_JOURNAL_COMMIT,
        "organization_commit": PINNED_BATCH_ORGANIZATION_COMMIT,
        "design_digest": "stand-in-design", "seed": 1, "model": "opus",
        "metric_schema_version": "business-plan-v1",
    }
    organization_repository = ProductionDriver.default_organization_repository(checkout)
    watchdog = ProductionWatchdog()
    driver = ProductionDriver("run-1", spec, manifest, checkout, organization_repository, watchdog)
    caps, ledger_path = real_caps(tmp_path, watchdog, run_wall_minutes=1,
                                  run_concurrent_sessions=2, run_turns=2, turns_per_session=2)
    paths = IsolatedJournal.paths(root, driver.boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    interrupted = False
    try:
        driver.boundary.verify("run-1", paths)
        driver.materialize_project(spec, paths)
        shim = IsolatedJournal.install_journal_shim(paths, driver.journal_port)
        driver.start_journal(paths, shim, "run-1", "launch-1", "challenge-1", driver.journal_port, caps)
        scenario = driver.load_scenario("production_incident", paths)

        plan_id = driver.start_plan(scenario, paths, caps)

        runtime = paths["project"] / ".journal" / "runtime"
        main_marker = runtime / "main-provider-started"
        plan_marker = runtime / "plan-1-provider-started"
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not (main_marker.is_file() and plan_marker.is_file()):
            time.sleep(0.1)
        assert main_marker.read_text(encoding="utf-8") == "started"
        assert plan_marker.read_text(encoding="utf-8") == "started"
        run = caps.read()["runs"]["run-1"]
        assert run["sessions"]["main-stand-in-session"] == {"active": True, "turns": 0}
        assert run["sessions"]["plan-stand-in-session"] == {"active": False, "turns": 1}
        assert len(run["requests"]) == 1
        assert driver.plan_started and plan_id == "1"
        record = driver.read_record("run-1")
        record_store = RunRecordStore()
        record_store.write(paths["evidence"], record)
        assert record_store.read(paths["evidence"] / "run-record.json") == record
        assert json.loads(ledger_path.read_text(encoding="utf-8"))["runs"]["run-1"]["sessions"]
    finally:
        if driver.sigterm_handler is None:
            stopped = driver.stop_owned("stand-in test finished")
        else:
            try:
                handler = signal.getsignal(signal.SIGTERM)
                assert handler == driver.sigterm_handler
                handler(signal.SIGTERM, None)
            except InterruptedError:
                interrupted = True
            stopped = driver.stopped
        caps.finish_run(stopped)
    assert interrupted
    assert stopped
    assert driver.main_session_process is not None and driver.main_session_process.poll() is not None
    assert (root / "project" / ".journal" / "runtime" / "main-provider-stopped").is_file()
    assert all(process.poll() is not None for process in driver.processes)
    assert driver.rig_stop_confirmation.is_file()


@pytest.mark.parametrize(("business_type", "scenario_name", "provider"), BATCH_SCENARIOS,
                         ids=lambda value: str(value))
@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production setup uses macOS sandbox-exec")
def test_every_batch_scenario_loads_as_an_organization_plan_before_agents_start(
        tmp_path, business_type, scenario_name, provider):
    root = tmp_path / f"{business_type}-{scenario_name}"
    checkout = Path(__file__).resolve().parents[2]
    settings = {
        "plans.plan_agents": True,
        "workers.cost_cap_dollars": 0,
        "workers.default_plan_mode": "organization",
        "workers.domain_agent_model_tier": "contract",
        "workers.hub_route_strategy": "containment",
        "workers.organization_plan_effort": "xhigh",
        "workers.organization_plan_profile": "organization-plan-review",
        "workers.seat_cap": 4,
        "workers.shared_role_queue_order": "plans_in_turn",
    }
    manifest = SimpleNamespace(data=lambda: {"design": {"settings": settings}})
    spec = {
        "provider": provider, "business_type": business_type, "scenario": scenario_name,
        "journal_commit": PINNED_BATCH_JOURNAL_COMMIT,
        "organization_commit": PINNED_BATCH_ORGANIZATION_COMMIT,
    }
    organization_repository = ProductionDriver.default_organization_repository(checkout)
    driver = ProductionDriver("run-1", spec, manifest, checkout, organization_repository, ProductionWatchdog())
    paths = IsolatedJournal.paths(root, driver.boundary.tmux_tmpdir)
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    stand_ins = paths["runtime"] / "stand-ins"
    stand_ins.mkdir(mode=0o700)
    started = paths["runtime"] / "provider-started"
    executables = {}
    for name in ("claude", "codex", "rig", "tmux"):
        executable = stand_ins / name
        executable.write_text(
            f"#!{sys.executable}\nfrom pathlib import Path\n"
            f"Path({str(started)!r}).write_text('started', encoding='utf-8')\n",
            encoding="utf-8",
        )
        executable.chmod(0o700)
        executables[name] = executable
    driver.executable = lambda name: executables[name]
    driver.boundary.verify("run-1", paths)
    snapshot = driver.materialize_project(spec, paths)
    pinned_loader = paths["project"] / "tests" / "lab" / "scenario_loader.py"
    assert snapshot["journal_commit"] == PINNED_BATCH_JOURNAL_COMMIT
    assert snapshot["organization_commit"] == PINNED_BATCH_ORGANIZATION_COMMIT
    assert "--domain" not in pinned_loader.read_text(encoding="utf-8")
    shim = IsolatedJournal.install_journal_shim(paths, driver.journal_port)

    try:
        driver.start_journal(paths, shim, "run-1", "launch-1", "challenge-1", driver.journal_port, None)
        scenario = driver.load_scenario(scenario_name, paths)
        plan_id = driver.prepare_plan(scenario, paths)
        with urlopen(f"http://127.0.0.1:{driver.journal_port}/journal/settings", timeout=3) as response:
            live_settings = json.load(response)
        harness_loader = paths["runtime"] / "driver-harness" / "tests" / "lab" / "scenario_loader.py"
        checkout_loader = checkout / "tests" / "lab" / "scenario_loader.py"
        business = BusinessType.read(checkout / "tests" / "lab" / "business_types" / f"{business_type}.toml")
        launch_preflight = driver.preflight_plan_agent_launch(str(plan_id), paths)
        shown = driver.journal_command(["plan", "show", plan_id], paths)
        expected = LabScenario.read(scenario["path"])
        expected_domains = [business.organization_domain_map[task["domain"]]
                            for phase in expected.phases for task in phase["tasks"]]
        pinned_organization = paths["runtime"] / "organization"
        pinned_domains = {folder.name for folder in (pinned_organization / "domains").iterdir()
                          if folder.is_dir() and (folder / "domain.toml").is_file()}
        actual_domains = [line.partition("domain:")[2].split()[0]
                          for line in shown.stdout.splitlines() if "domain:" in line]

        assert shown.returncode == 0, shown.stderr
        assert shown.stdout.splitlines()[0].startswith(f"plan {plan_id} approved:")
        assert launch_preflight["plan_agents"] is True
        assert launch_preflight["plan_mode"] == "organization"
        assert Path(launch_preflight["main_session_launcher"]).is_file()
        assert launch_preflight["supervisor_socket"] == str(paths["tmp"] / "journal-main.sock")
        assert live_settings["plans"]["plan_agents"] is True
        assert live_settings["workers"]["organization_folder"] == str(pinned_organization)
        assert (paths["project"] / ".claude" / "settings.local.json").is_file()
        assert (paths["project"] / ".claude" / "skills" / "journal" / "SKILL.md").is_file()
        assert set(expected_domains) <= pinned_domains
        assert actual_domains == expected_domains
        assert harness_loader.read_bytes() == checkout_loader.read_bytes()
        assert len(driver.processes) == 1
        assert not driver.rig_started
        assert not started.exists()
    finally:
        driver.stop_owned()
