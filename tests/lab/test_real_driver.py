import json
import os
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.production_boundary import ProductionBoundary, TMUX_SOCKET_PATH_LIMIT
from tests.lab.real import production_driver as production_driver_module
from tests.lab.real.production_driver import ProductionDriver
from tests.lab.real.production_watchdog import ProductionWatchdog
from tests.lab.real.provider_proxy import ProviderProxy


def test_provider_proxy_rejects_git_remote_hosts():
    assert ProviderProxy.allowed("api.anthropic.com")
    assert ProviderProxy.allowed("chatgpt.com")
    assert not ProviderProxy.allowed("github.com")
    assert not ProviderProxy.allowed("github.com.anthropic.com")


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
    provider_binary, rig_binary, tmux_binary = cli / "claude", cli / "rig", cli / "tmux"
    executables = {"claude": provider_binary, "rig": rig_binary, "tmux": tmux_binary}
    monkeypatch.setattr("tests.lab.real.production_driver.shutil.which",
                        lambda name: str(executables[name]) if name in executables else None)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(profile))
    monkeypatch.setenv("CLAUDE_CODE_TMPDIR", str(tmp_path / "host-claude-temp"))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-copy")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-copy")
    manifest = SimpleNamespace(digest="manifest-digest", data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, source, source,
                              ProductionWatchdog())
    paths["tmp"] = driver.boundary.tmux_tmpdir
    IsolatedJournal.install_journal_shim(paths, driver.journal_port)

    environment = driver.child_environment(paths, driver.journal_port)
    driver.env = environment

    assert environment["CLAUDE_CONFIG_DIR"] == str(profile)
    assert environment["HOME"] == environment["OPENRIG_HOME"]
    assert Path(environment["OPENRIG_DB"]).parent == Path(environment["OPENRIG_HOME"])
    assert "ANTHROPIC_API_KEY" not in environment
    assert "OPENAI_API_KEY" not in environment
    assert environment["TMUX_TMPDIR"] == str(driver.boundary.tmux_tmpdir)
    assert environment["CLAUDE_CODE_TMPDIR"] == str(paths["tmp"].resolve())



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
    tmux_bin = tmp_path / "tmux-bin"
    for directory in (host_bin, provider_bin, rig_bin, tmux_bin):
        directory.mkdir()
    global_dispatcher = host_bin / "journal"
    global_dispatcher.write_text("#!/bin/sh\n", encoding="utf-8")
    global_dispatcher.chmod(0o700)
    provider = provider_bin / "claude"
    rig = rig_bin / "rig"
    tmux = tmux_bin / "tmux"
    for binary in (provider, rig, tmux):
        binary.write_text("#!/bin/sh\n", encoding="utf-8")
        binary.chmod(0o700)
    (host_bin / "claude").symlink_to(provider)
    (host_bin / "rig").symlink_to(rig)
    (host_bin / "tmux").symlink_to(tmux)
    monkeypatch.setattr("tests.lab.real.production_driver.shutil.which",
                        lambda name: str(host_bin / name) if name in {"claude", "rig", "tmux"} else None)
    manifest = SimpleNamespace(digest="manifest-digest", data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, source, source,
                              ProductionWatchdog())
    paths["tmp"] = driver.boundary.tmux_tmpdir
    shim = IsolatedJournal.install_journal_shim(paths, driver.journal_port)

    environment = driver.child_environment(paths, driver.journal_port)
    path = tuple(Path(entry) for entry in environment["PATH"].split(os.pathsep))

    assert path[0] == paths["bin"].resolve()
    assert str(host_bin.resolve()) not in {str(entry) for entry in path}
    assert provider_bin.resolve() in path and rig_bin.resolve() in path and tmux_bin.resolve() in path
    assert path[0] / "journal" == shim
    assert environment["TMUX_TMPDIR"] == str(paths["tmp"].resolve())
    assert len(os.fsencode(str(driver.boundary.tmux_socket_path))) < TMUX_SOCKET_PATH_LIMIT
    assert (paths["bin"] / "claude").resolve() == provider
    assert (paths["bin"] / "rig").resolve() == rig
    assert (paths["bin"] / "tmux").resolve() == tmux
    assert not any((entry / "journal").exists() for entry in path[1:])


def test_production_driver_installs_cap_events_in_the_pinned_hook(tmp_path):
    project = tmp_path / "project"
    hooks = project / "src" / "journal" / "hooks"
    runtime = tmp_path / "runtime"
    hooks.mkdir(parents=True)
    runtime.mkdir(mode=0o700)
    (hooks / "hook.sh").write_text(
        "#!/bin/sh\nbody=$(mktemp)\nsent=$(mktemp)\nfiring=\"$$-$begun\"\n"
        "event=$(sed -n 's/.*\"hook_event_name\": *\"\\([A-Za-z]*\\)\".*/\\1/p' \"$sent\" | head -1)\n"
        "post() { :; }\n",
        encoding="utf-8",
    )
    manifest = SimpleNamespace(digest="manifest-digest", data=lambda: {"design": {"settings": {}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, tmp_path, tmp_path,
                              ProductionWatchdog())

    driver.install_cap_hook(project, {"runtime": runtime})

    hook = (hooks / "hook.sh").read_text(encoding="utf-8")
    forwarder = runtime / "cap-hook"
    assert 'body=$(mktemp "${TMPDIR%/}/journal-hook.XXXXXXXXXX")' in hook
    assert 'sent=$(mktemp "${TMPDIR%/}/journal-hook.XXXXXXXXXX")' in hook
    assert 'SessionStart|SessionEnd|UserPromptSubmit' in hook
    assert '"$sent" "$firing"' in hook
    assert str(forwarder) in hook
    assert '${JOURNAL_LAB_CAP_HOOK' not in hook
    assert "JOURNAL_LAB_CAP_URL=http://127.0.0.1:" in forwarder.read_text(encoding="utf-8")
    assert f"JOURNAL_LAB_CAP_TOKEN={driver.token}" in forwarder.read_text(encoding="utf-8")
    assert (runtime / "gitconfig").is_file()


def test_plan_start_uses_the_main_session_event_and_waits_for_the_plan_agent(tmp_path, monkeypatch):
    paths = {"bin": tmp_path / "bin", "project": tmp_path / "project"}
    paths["bin"].mkdir()
    paths["project"].mkdir()
    (paths["bin"] / "claude").touch(mode=0o700)
    manifest = SimpleNamespace(data=lambda: {"design": {"settings": {"plans.plan_agents": True}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, tmp_path, tmp_path,
                              ProductionWatchdog())
    paths["tmp"] = driver.boundary.tmux_tmpdir
    monkeypatch.setattr(driver.boundary, "tmux_directory_is_valid", lambda: True)
    driver.prepared_plan = {"plan_id": 17, "plan_agents": True, "plan_mode": "organization",
                            "plan_state": "approved"}
    calls = []
    monkeypatch.setattr(driver, "prepare_plan", lambda _scenario, _paths: "17")
    monkeypatch.setattr(driver, "install_agent_interpreters", lambda _paths: None)
    monkeypatch.setattr(driver, "preflight_tmux", lambda _paths: "ready")
    monkeypatch.setattr(driver, "start_openrig", lambda _paths: None)
    monkeypatch.setattr(driver, "start_main_session",
                        lambda _paths, _caps, socket: calls.append(("main session", socket)))
    monkeypatch.setattr(driver, "wait_for_agent_session", lambda _caps, count, _name="": calls.append(count))
    caps = object()

    plan_id = driver.start_plan({}, paths, caps)

    assert plan_id == "17"
    assert calls == [("main session", paths["tmp"] / "journal-main.sock"), 2]
    assert driver.plan_started


def test_plan_launch_preflight_rejects_missing_plan_agent_setup(tmp_path):
    paths = {"bin": tmp_path / "bin"}
    paths["bin"].mkdir()
    (paths["bin"] / "claude").touch(mode=0o700)
    manifest = SimpleNamespace(data=lambda: {"design": {"settings": {"plans.plan_agents": True}}})
    driver = ProductionDriver("run-1", {"provider": "claude"}, manifest, tmp_path, tmp_path,
                              ProductionWatchdog())
    driver.prepared_plan = {"plan_id": 17, "plan_agents": False, "plan_mode": "organization",
                            "plan_state": "approved"}

    with pytest.raises(ValueError, match="approved organization plan agent"):
        driver.preflight_plan_agent_launch("17", paths)


def test_production_boundary_policy_only_allows_run_storage_and_local_provider_proxy(tmp_path):
    root = tmp_path / "private-run"
    boundary = ProductionBoundary("run-1", (32001, 32002), ())

    policy = boundary.policy(root, ())

    assert f'(allow file-write* (subpath "{root}"))' in policy
    assert '(allow file-read* (literal "/"))' in policy
    assert '(allow file-read* (literal "/private/var/select/sh"))' in policy
    assert '(allow pseudo-tty)' in policy
    assert '(allow file-read* file-write* file-ioctl (literal "/dev/ptmx"))' in policy
    assert '(allow file-read* file-write* (require-all (regex #"^/dev/ttys[0-9]+") (extension "com.apple.sandbox.pty")))' in policy
    assert '(allow file-ioctl (regex #"^/dev/ttys[0-9]+"))' in policy
    socket_directory = json.dumps(str(boundary.tmux_tmpdir))
    assert '(allow system-socket (socket-domain AF_UNIX))' in policy
    assert f'(allow network-bind (local unix-socket (subpath {socket_directory})))' in policy
    assert f'(allow network-outbound (remote unix-socket (subpath {socket_directory})))' in policy
    assert '(allow network-bind (local unix-socket))' not in policy
    assert '(allow network-outbound (remote unix-socket))' not in policy
    assert "(allow file-write*)" not in policy
    assert '(allow signal (target same-sandbox))' in policy
    assert '(allow process-info* (target same-sandbox))' in policy
    assert f'(allow process-exec (literal {json.dumps(str(root / "home" / "bin" / "ps"))}))' in policy
    assert "(allow signal)" not in policy
    assert "(allow process-info*)" not in policy
    assert "(allow process-exec)" not in policy
    assert 'remote ip "localhost:32001"' in policy
    assert 'remote ip "localhost:32002"' in policy
    assert "github.com" not in policy


def test_tmux_socket_path_stays_below_the_unix_socket_limit():
    boundary = ProductionBoundary("run-1", (32001,), ())
    other_run = ProductionBoundary("run-1", (32002,), ())

    assert len(os.fsencode(str(boundary.tmux_socket_path))) < TMUX_SOCKET_PATH_LIMIT
    assert boundary.tmux_socket_path.is_relative_to(boundary.tmux_mount)
    assert other_run.tmux_mount != boundary.tmux_mount


def test_tmux_preflight_rejects_the_long_runtime_socket_directory_before_a_tmux_call(
        tmp_path, monkeypatch):
    driver = ProductionDriver("run-1", {"provider": "claude"}, None, tmp_path, tmp_path,
                              ProductionWatchdog())
    paths = IsolatedJournal.paths(tmp_path / "private-run", driver.boundary.tmux_tmpdir)
    driver.env = {"TMUX_TMPDIR": str(paths["runtime"] / "tmux")}

    def unexpected_tmux_call(*_args):
        raise AssertionError("tmux must not receive the long runtime socket directory")

    monkeypatch.setattr(driver, "command", unexpected_tmux_call)

    with pytest.raises(ValueError, match="private short temporary directory"):
        driver.preflight_tmux(paths)


def test_wait_identity_keeps_polling_a_journal_that_is_still_booting(tmp_path, monkeypatch):
    elapsed = 0
    health_phases = []

    def monotonic():
        nonlocal elapsed
        current = elapsed
        elapsed += 15
        return current

    def open_url(url, timeout):
        if url.endswith("/health"):
            phase = "booted" if len(health_phases) == 3 else "booting"
            health_phases.append(phase)
            return BytesIO(json.dumps({"phase": phase}).encode())
        identity = {"root": str((tmp_path / ".journal").resolve()), "pid": 411}
        return BytesIO(json.dumps(identity).encode())

    monkeypatch.setattr(production_driver_module.time, "monotonic", monotonic)
    monkeypatch.setattr(production_driver_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(production_driver_module, "urlopen", open_url)
    process = SimpleNamespace(pid=411, poll=lambda: None)

    identity = ProductionDriver.wait_identity(object.__new__(ProductionDriver), process,
                                              {"project": tmp_path}, "run-1", "launch-1", "challenge-1", 8123)

    assert health_phases == ["booting", "booting", "booting", "booted"]
    assert identity["root"] == str((tmp_path / ".journal").resolve())


