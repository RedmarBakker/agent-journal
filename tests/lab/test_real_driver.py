# Host integration tests spawn isolated stand-ins and need macOS sandbox-exec.
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from tests.lab.real.cap_event_server import CapEventServer
from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.production_boundary import ProductionBoundary
from tests.lab.real.production_driver import ProductionDriver
from tests.lab.real.production_watchdog import ProductionWatchdog
from tests.lab.real.provider_proxy import ProviderProxy
from tests.lab.real.run_caps import RunCaps
from tests.lab.real.run_record import RunRecord
from tests.lab.real.run_record_store import RunRecordStore
from tests.lab.business_type import BusinessType
from tests.lab.lab_scenario import LabScenario


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


def test_provider_proxy_rejects_git_remote_hosts():
    assert ProviderProxy.allowed("api.anthropic.com")
    assert ProviderProxy.allowed("chatgpt.com")
    assert not ProviderProxy.allowed("github.com")
    assert not ProviderProxy.allowed("github.com.anthropic.com")


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
    assert not remotes.strip()


def test_default_organization_repository_is_the_main_checkout_sibling_from_a_worktree(tmp_path):
    checkout = tmp_path / "agent-journal"
    checkout.mkdir()
    (checkout / ".git").mkdir()
    worktree = checkout / ".journal" / "worktrees" / "worker"
    worktree.mkdir(parents=True)
    worktree_git = checkout / ".git" / "worktrees" / "worker"
    worktree_git.mkdir(parents=True)
    (worktree_git / "commondir").write_text("../..\n", encoding="utf-8")
    relative_git_dir = os.path.relpath(worktree_git, worktree)
    (worktree / ".git").write_text(f"gitdir: {relative_git_dir}\n", encoding="utf-8")

    assert ProductionDriver.default_organization_repository(checkout) == tmp_path / "agentic-organization-journal"
    assert ProductionDriver.default_organization_repository(worktree) == tmp_path / "agentic-organization-journal"


def test_production_environment_uses_signed_in_cli_profile_without_copying_api_keys(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir(mode=0o700)
    paths = IsolatedJournal.paths(root)
    for name in ("project", "private_home", "runtime", "evidence", "tmp", "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(mode=0o700)
    source = tmp_path / "checkout"
    source.mkdir()
    profile = tmp_path / "claude-profile"
    profile.mkdir(mode=0o700)
    paths["provider_config_claude"] = profile
    (paths["project"] / "src").mkdir()
    (paths["project"] / "src" / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    cli = tmp_path / "provider-bin"
    cli.mkdir()
    provider_binary, rig_binary = cli / "claude", cli / "rig"
    monkeypatch.setattr("tests.lab.real.production_driver.shutil.which",
                        lambda name: str(provider_binary if name == "claude" else rig_binary))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(profile))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-copy")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-copy")
    manifest = SimpleNamespace(digest="manifest-digest", data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, source, source,
                              ProductionWatchdog())
    IsolatedJournal.install_journal_shim(paths, driver.journal_port)

    environment = driver.child_environment(paths, driver.journal_port)

    assert environment["CLAUDE_CONFIG_DIR"] == str(profile)
    assert environment["HOME"] == str(paths["private_home"].resolve())
    assert "ANTHROPIC_API_KEY" not in environment
    assert "OPENAI_API_KEY" not in environment


def test_production_path_resolves_cli_symlinks_and_keeps_private_journal_dispatcher_first(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir(mode=0o700)
    paths = IsolatedJournal.paths(root)
    for name in ("project", "private_home", "runtime", "evidence", "tmp", "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(mode=0o700)
    source = tmp_path / "checkout"
    source.mkdir()
    (paths["project"] / "src").mkdir()
    (paths["project"] / "src" / "journal.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    host_bin = tmp_path / "host-bin"
    provider_bin = tmp_path / "provider-bin"
    rig_bin = tmp_path / "rig-bin"
    for directory in (host_bin, provider_bin, rig_bin):
        directory.mkdir()
    global_dispatcher = host_bin / "journal"
    global_dispatcher.write_text("#!/bin/sh\n", encoding="utf-8")
    global_dispatcher.chmod(0o700)
    provider = provider_bin / "claude"
    rig = rig_bin / "rig"
    for binary in (provider, rig):
        binary.write_text("#!/bin/sh\n", encoding="utf-8")
        binary.chmod(0o700)
    (host_bin / "claude").symlink_to(provider)
    (host_bin / "rig").symlink_to(rig)
    monkeypatch.setattr("tests.lab.real.production_driver.shutil.which",
                        lambda name: str(host_bin / name) if name in {"claude", "rig"} else None)
    manifest = SimpleNamespace(digest="manifest-digest", data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, source, source,
                              ProductionWatchdog())
    shim = IsolatedJournal.install_journal_shim(paths, driver.journal_port)

    environment = driver.child_environment(paths, driver.journal_port)
    path = tuple(Path(entry) for entry in environment["PATH"].split(os.pathsep))

    assert path[0] == paths["bin"].resolve()
    assert str(host_bin.resolve()) not in {str(entry) for entry in path}
    assert provider_bin.resolve() in path and rig_bin.resolve() in path
    assert path[0] / "journal" == shim
    assert (paths["bin"] / "claude").resolve() == provider
    assert (paths["bin"] / "rig").resolve() == rig
    assert not any((entry / "journal").exists() for entry in path[1:])


def test_production_driver_installs_cap_events_in_the_pinned_hook(tmp_path):
    project = tmp_path / "project"
    hooks = project / "src" / "journal" / "hooks"
    runtime = tmp_path / "runtime"
    hooks.mkdir(parents=True)
    runtime.mkdir(mode=0o700)
    (hooks / "hook.sh").write_text(
        "#!/bin/sh\nfiring=\"$$-$begun\"\n"
        "event=$(sed -n 's/.*\"hook_event_name\": *\"\\([A-Za-z]*\\)\".*/\\1/p' \"$sent\" | head -1)\n"
        "post() { :; }\n",
        encoding="utf-8",
    )
    manifest = SimpleNamespace(digest="manifest-digest", data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, tmp_path, tmp_path,
                              ProductionWatchdog())

    driver.install_cap_hook(project, {"runtime": runtime})

    hook = (hooks / "hook.sh").read_text(encoding="utf-8")
    assert 'SessionStart|SessionEnd|UserPromptSubmit' in hook
    assert '"$sent" "$firing"' in hook
    assert (runtime / "gitconfig").is_file()


def test_production_boundary_policy_only_allows_run_storage_and_local_provider_proxy(tmp_path):
    root = tmp_path / "private-run"
    boundary = ProductionBoundary("run-1", (32001, 32002), ())

    policy = boundary.policy(root, ())

    assert f'(allow file-write* (subpath "{root}"))' in policy
    assert '(allow file-read* (literal "/"))' in policy
    assert "(allow file-write*)" not in policy
    assert 'remote ip "localhost:32001"' in policy
    assert 'remote ip "localhost:32002"' in policy
    assert "github.com" not in policy


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production filesystem isolation uses macOS sandbox-exec")
def test_stand_in_cli_cannot_write_outside_its_private_run_root(tmp_path):
    root = tmp_path / "private-run"
    paths = {name: root / folder for name, folder in (
        ("root", ""), ("project", "project"), ("private_home", "home"),
        ("runtime", "runtime"), ("tmp", "tmp"),
    )}
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
    boundary = ProductionBoundary("run-1", (32001,),
                                  (Path(sys.executable).resolve().parent, Path(sys.prefix).resolve()))
    boundary.verify("run-1", paths)
    policy = boundary.profile.read_text(encoding="utf-8")
    assert "network-outbound)" not in policy
    assert 'remote ip "localhost:32001"' in policy

    environment = {**os.environ, "HOME": str(paths["private_home"]), "TMPDIR": str(paths["tmp"])}
    completed = subprocess.run(boundary.wrap(["/bin/sh", str(script), str(external), str(inside)]),
                               env=environment, capture_output=True, text=True, timeout=10, check=False)

    assert completed.returncode == 0, f"{completed.stderr}\n{policy}"
    assert not external.exists()
    assert inside.read_text(encoding="utf-8").removesuffix("\n") == "denied"
    assert boundary.observe("run-1").escaped_writes == 0


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production filesystem isolation uses macOS sandbox-exec")
def test_production_interpreter_starts_under_its_real_boundary(tmp_path):
    root = tmp_path / "private-run"
    paths = IsolatedJournal.paths(root)
    for name in ("root", "project", "private_home", "runtime", "tmp"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    driver = ProductionDriver("run-1", {"provider": "claude"}, None, tmp_path, tmp_path,
                              ProductionWatchdog())
    virtual_environment = Path(sys.prefix).resolve()
    python_framework = Path(sys.base_prefix).resolve()

    driver.boundary.verify("run-1", paths)
    policy = driver.boundary.profile.read_text(encoding="utf-8")
    assert f'(allow file-read-metadata (literal {json.dumps(str(root.resolve()))}))' in policy
    environment = {"HOME": str(paths["private_home"]), "TMPDIR": str(paths["tmp"]),
                   "PATH": "/usr/bin:/bin", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
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


@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production filesystem isolation uses macOS sandbox-exec")
def test_production_journal_server_answers_health_under_its_real_boundary(tmp_path):
    root = tmp_path / "private-run"
    paths = IsolatedJournal.paths(root)
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    checkout = Path(__file__).resolve().parents[2]
    shutil.copytree(checkout / "src", paths["project"] / "src")
    cli_bin = tmp_path / "stand-in-clis"
    cli_bin.mkdir(mode=0o700)
    executables = {}
    for name in ("claude", "rig"):
        executable = cli_bin / name
        executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        executable.chmod(0o700)
        executables[name] = executable
    driver = ProductionDriver("run-1", {"provider": "claude"}, None, checkout, tmp_path,
                              ProductionWatchdog())
    driver.executable = lambda name: executables[name]
    driver.boundary.verify("run-1", paths)
    policy = driver.boundary.profile.read_text(encoding="utf-8")
    assert f'(allow network-bind (local ip "localhost:{driver.share_port}"))' in policy
    shim = IsolatedJournal.install_journal_shim(paths, driver.journal_port)

    try:
        driver.start_journal(paths, shim, "run-1", "launch-1", "challenge-1", driver.journal_port, None)
        with urlopen(f"http://127.0.0.1:{driver.journal_port}/journal/health", timeout=3) as response:
            assert response.status == 200
        assert (paths["project"] / ".journal" / "journal.db").is_file()
        sharing = json.loads((paths["project"] / ".journal" / "sharing.json").read_text(encoding="utf-8"))
        assert sharing["port"] == driver.share_port
    finally:
        driver.stop_owned()


@pytest.mark.parametrize(("business_type", "scenario_name", "provider"), BATCH_SCENARIOS,
                         ids=lambda value: str(value))
@pytest.mark.skipif(platform.system() != "Darwin" or shutil.which("sandbox-exec") is None,
                    reason="production setup uses macOS sandbox-exec")
def test_every_batch_scenario_loads_as_an_organization_plan_before_agents_start(
        tmp_path, business_type, scenario_name, provider):
    paths = IsolatedJournal.paths(tmp_path / f"{business_type}-{scenario_name}")
    for name in ("root", "project", "private_home", "runtime", "evidence", "tmp",
                 "xdg_config", "xdg_cache", "bin"):
        paths[name].mkdir(parents=True, exist_ok=True, mode=0o700)
    checkout = Path(__file__).resolve().parents[2]

    stand_ins = paths["runtime"] / "stand-ins"
    stand_ins.mkdir(mode=0o700)
    started = paths["runtime"] / "provider-started"
    executables = {}
    for name in ("claude", "codex", "rig"):
        executable = stand_ins / name
        executable.write_text(
            f"#!{sys.executable}\nfrom pathlib import Path\n"
            f"Path({str(started)!r}).write_text('started', encoding='utf-8')\n",
            encoding="utf-8",
        )
        executable.chmod(0o700)
        executables[name] = executable

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
        harness_loader = paths["runtime"] / "driver-harness" / "tests" / "lab" / "scenario_loader.py"
        checkout_loader = checkout / "tests" / "lab" / "scenario_loader.py"
        business = BusinessType.read(checkout / "tests" / "lab" / "business_types" / f"{business_type}.toml")
        shown = driver.command([sys.executable, str(paths["project"] / "src" / "journal.py"),
                                "plan", "show", plan_id], paths)
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
        assert set(expected_domains) <= pinned_domains
        assert actual_domains == expected_domains
        assert harness_loader.read_bytes() == checkout_loader.read_bytes()
        assert len(driver.processes) == 1
        assert not driver.rig_started
        assert not started.exists()
    finally:
        driver.stop_owned()
