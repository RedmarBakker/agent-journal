"""Checks for the supervisor v1 deployment package and setup script."""

import ast
import importlib.util
import json
import re
import stat
from types import SimpleNamespace
from pathlib import Path

from journal.models.supervisor_grant import SupervisorGrant
from journal.models.task_state import TaskState
from journal.supervisor_failure import SupervisorFailure
from plugins.supervisor_v1 import bridge_service
from supervisor_bridge.contracts import OPENCLAW_TOOL_NAMES
from supervisor_bridge.proposal_evaluation import load_case, seed_case
from tests.test_supervisor_authority import admitted, seeded


ROOT = Path(__file__).parents[1]
PROFILE = ROOT / "docs" / "supervisor" / "v1"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def journal_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names if alias.name == "journal" or alias.name.startswith("journal."))
        if isinstance(node, ast.ImportFrom) and node.module and (node.module == "journal" or node.module.startswith("journal.")):
            imported.add(node.module)
    return imported


def live_setup_function_source(name: str) -> str:
    path = PROFILE / "live-smoke-setup.py"
    source = path.read_text()
    tree = ast.parse(source)
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.get_source_segment(source, function)


def live_setup_module():
    spec = importlib.util.spec_from_file_location("supervisor_live_setup", PROFILE / "live-smoke-setup.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_profile_is_single_tenant_and_off_by_default():
    manifest = read_json(PROFILE / "manifest.json")
    compose = read_json(PROFILE / "compose.json")

    assert manifest["tenant_model"].startswith("one dedicated Linux VM")
    topology = {service["name"]: service for service in manifest["topology"]}
    assert "uid 10001" in topology["journal-writer"]["identity"]
    assert "uid 1000" in topology["openclaw-gateway-and-stdio-client"]["identity"]
    assert "uid 10001" in topology["journal-plugin-bridge"]["identity"]
    assert compose["services"]["gateway"]["user"] == "1000:1000"
    assert compose["services"]["gateway"]["group_add"] == ["10030"]
    assert compose["services"]["backup"]["user"] == "10005:10005"
    assert manifest["launch"]["default_enabled"] is False
    assert manifest["launch"]["plugin_installed"] is False
    assert manifest["launch"]["enrollment_enabled"] is False
    assert all(service["profiles"] == ["authorized-staging"] for service in compose["services"].values())
    assert "writer_state" in compose["volumes"] and "gateway_state" in compose["volumes"]
    assert "codex_driver_state" in compose["volumes"]
    assert "/var/lib/journal-codex" in manifest["backup"]["excluded_from_backup"]
    assert compose["services"]["writer"]["restart"] == "unless-stopped"
    assert compose["services"]["gateway"]["restart"] == "unless-stopped"
    assert compose["services"]["writer"]["healthcheck"]["test"] == ["CMD-SHELL", "curl -fsS http://127.0.0.1:8421/journal/health"]
    assert compose["services"]["gateway"]["healthcheck"]["test"] == [
        "CMD",
        "node",
        "-e",
        "fetch('http://127.0.0.1:18789/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))",
    ]
    assert compose["services"]["writer"]["ports"] == ["127.0.0.1:18440:8423"]
    assert compose["services"]["writer"]["expose"] == ["8422"]
    assert compose["services"]["writer"]["environment"]["JOURNAL_ROOT"] == "/data/project"
    assert compose["services"]["writer"]["environment"]["JOURNAL_HOST"] == "127.0.0.1"
    assert compose["services"]["writer"]["environment"]["JOURNAL_PORT"] == "8421"
    assert compose["services"]["writer"]["environment"]["JOURNAL_SUPERVISOR_PORT"] == "8422"
    assert compose["services"]["writer"]["environment"]["JOURNAL_OWNER_ACCESS_HOST"] == "10.76.10.10"
    assert compose["services"]["writer"]["environment"]["JOURNAL_OWNER_ACCESS_PORT"] == "8423"
    assert compose["services"]["writer"]["environment"]["JOURNAL_SUPERVISOR_HOST"] == "10.76.20.10"
    assert compose["services"]["writer"]["environment"]["JOURNAL_SUPERVISOR_TLS_CERT_FILE"] == "/run/secrets/writer_supervisor_tls_cert"
    assert compose["services"]["writer"]["environment"]["JOURNAL_SUPERVISOR_TLS_KEY_FILE"] == "/run/secrets/writer_supervisor_tls_key"
    assert manifest["topology"][0]["login_page"].startswith("none;")
    assert manifest["launch_gates"]["reviewed_writer_image_digest_recorded"] is False
    assert manifest["backup_runtime"]["version"] == "0.17.3"
    assert manifest["backup_runtime"]["digest_pinned"] is True
    assert compose["services"]["backup"]["image"].startswith("restic/restic@sha256:")
    assert compose["services"]["writer"]["image"] == "agent-journal-supervisor-writer:${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed source commit}"
    assert "build" not in compose["services"]["writer"]
    gateway = topology["openclaw-gateway-and-stdio-client"]
    assert gateway["image"] == "agent-journal-supervisor-gateway:${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed source commit}"
    assert gateway["base_image"] == "ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5"
    assert gateway["supervisor_admission"] == {
        "url": "https://writer:8422",
        "network": "gateway_link",
        "token_secret": "journal_supervisor_credential",
        "token_environment": "JOURNAL_SUPERVISOR_ADMISSION_TOKEN",
        "tls_ca_secret": "writer_supervisor_tls_ca",
        "listener": "TLS handler admits only SERVICE_PATHS; every request still passes SupervisorRequestAuth token validation",
    }


def test_gateway_has_no_writer_data_or_host_socket_mounts():
    compose = read_json(PROFILE / "compose.json")
    gateway = compose["services"]["gateway"]
    mounts = gateway["volumes"]
    mount_text = " ".join(mounts)

    assert set(mounts) == {"gateway_state:/home/node/.openclaw", "supervisor_hints:/var/lib/journal-supervisor/hints:ro"}
    assert not any("writer_state" in mount or "/data" in mount or "worker" in mount or "sock" in mount for mount in mounts)
    assert not gateway.get("ports")
    assert set(gateway["networks"]) == {"gateway_link", "provider_egress"}
    assert gateway["image"] == "agent-journal-supervisor-gateway:${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed source commit}"
    assert "supervisor_hints:/var/lib/journal-supervisor/hints:ro" in mounts
    assert "journal_management" not in gateway["networks"]
    assert set(compose["services"]["backup"]["networks"]) == {"backup_egress"}
    assert compose["volumes"]["gateway_state"]["driver_opts"]["device"].endswith("gid 10030 mode 0750}")


def test_secret_mounts_match_the_receiving_service():
    compose = read_json(PROFILE / "compose.json")
    secrets = compose["secrets"]
    gateway_secrets = {secret["source"] for secret in compose["services"]["gateway"]["secrets"]}
    writer_secrets = {secret["source"] for secret in compose["services"]["writer"].get("secrets", [])}
    backup_secrets = {secret["source"] for secret in compose["services"]["backup"]["secrets"]}

    assert gateway_secrets == {"supervisor_anthropic_api_key", "openclaw_hook_token", "journal_supervisor_credential", "writer_supervisor_tls_ca"}
    assert writer_secrets == {"writer_supervisor_tls_cert", "writer_supervisor_tls_key"}
    assert backup_secrets == {"restic_password", "restic_repository", "backup_object_store_credentials"}
    assert set(secrets) == gateway_secrets | writer_secrets | backup_secrets
    assert secrets["writer_supervisor_tls_cert"]["file"].endswith("/writer_supervisor_tls_cert")
    assert secrets["writer_supervisor_tls_key"]["file"].endswith("/writer_supervisor_tls_key")
    assert secrets["writer_supervisor_tls_ca"]["file"].endswith("/writer_supervisor_tls_ca")
    assert all("TENANT_SECRET_SOURCE_DIR" in secrets[name]["file"] for name in writer_secrets | {"writer_supervisor_tls_ca"})
    assert {secret["target"] for secret in compose["services"]["writer"]["secrets"]} == writer_secrets
    manifest_secrets = {secret["name"]: secret for secret in read_json(PROFILE / "manifest.json")["secrets"]}
    assert {manifest_secrets[name]["host_owner"] for name in gateway_secrets} == {"root:1000"}
    assert {manifest_secrets[name]["host_owner"] for name in backup_secrets} == {"root:10005"}
    assert {manifest_secrets[name]["host_mode"] for name in gateway_secrets | backup_secrets} == {"0440"}
    assert {manifest_secrets[name]["host_mode"] for name in writer_secrets} == {"0440"}
    assert {manifest_secrets[name]["host_owner"] for name in writer_secrets} == {"root:10001"}
    assert manifest_secrets["writer_supervisor_tls_ca"]["host_owner"] == "root:1000"
    assert "codex_driver_credentials" not in manifest_secrets
    assert "codex_driver_state:/var/lib/journal-codex" in compose["services"]["writer"]["volumes"]
    assert "codex_driver_state" not in " ".join(compose["services"]["gateway"]["volumes"])
    assert "codex_driver_state" not in " ".join(compose["services"]["backup"]["volumes"])
    assert compose["volumes"]["codex_driver_state"] == {}


def test_network_policy_is_default_deny_and_refuses_unisolated_workers():
    manifest = read_json(PROFILE / "manifest.json")
    firewall = read_json(PROFILE / "firewall-policy.fixture.json")
    execution = manifest["execution_identity_contract"]
    worker = manifest["worker_identity_contract"]
    plan_driver = next(item for item in manifest["topology"] if item["name"] == "normal-plan-driver")

    assert manifest["network_policy_fixture"] == "firewall-policy.fixture.json"
    assert firewall["is_applied_firewall_config"] is False
    assert set(firewall["default_policy"].values()) == {"deny", True}
    assert any(rule["ports"] == [8422] and rule["action"] == "allow" for rule in firewall["rules"])
    assert any(
        rule["destination"] == "10.76.20.10 (writer)" and rule["ports"] == [8421] and rule["action"] == "deny"
        for rule in firewall["rules"]
    )
    assert any(
        rule["destination"] == "10.76.10.10 (writer management)" and rule["ports"] == [8423] and rule["action"] == "deny"
        for rule in firewall["rules"]
    )
    assert any(rule["ports"] == [5432, 3306, 6379] and rule["action"] == "deny" for rule in firewall["rules"])
    assert any(rule["destination"] == "api.anthropic.com" and rule["ports"] == [443] for rule in firewall["rules"])
    assert any(rule["destination"] == "api.openai.com" and rule["ports"] == [443] for rule in firewall["rules"])
    assert any("refuse enrollment" in rule["action"] for rule in firewall["rules"])
    assert manifest["launch_gates"]["active_worker_restricted_profile_verified_or_enrollment_refused"] is False
    assert manifest["launch"]["enrollment_enabled"] is False
    assert execution["uid"] == 10003 and execution["gid"] == 10003
    assert execution["root_filesystem"] == "read-only"
    assert execution["capabilities"] == [] and execution["no_new_privileges"] is True
    assert execution["status"] == "packaged; dedicated-VM B10 process identity, capability, worktree write-scope and designated-route probes remain pending"
    assert "routed through the fixed uid10003 broker by AgentLauncher" in plan_driver["status"]
    assert "B10 must still prove" in plan_driver["status"]
    assert worker["uid"] == 10004 and worker["gid"] == 10004
    assert worker["root_filesystem"] == "read-only"
    assert worker["capabilities"] == [] and worker["no_new_privileges"] is True
    assert worker["secret_mounts"] == []
    assert "refuse enrollment" in worker["enrollment_rule"]


def test_seed_script_requires_a_clean_matching_commit_and_excludes_runtime_state():
    script = (PROFILE / "seed-project.sh").read_text()

    assert "status --porcelain --untracked-files=all" in script
    assert "rev-parse HEAD" in script
    assert "git -C \"$PROJECT_EXPORT\" archive --format=tar HEAD" in script
    assert "(exclude).journal/**" in script
    assert "(exclude).codex/**" in script
    assert "(exclude).claude/**" in script
    assert "PROJECT_EXPORT HEAD must equal PROJECT_REVISION" in script
    assert "--user 10001:10001" in script
    assert "--network none" in script
    assert "writer project folder is not empty" in script


def test_seeded_project_is_committed_on_main_as_the_project_owner():
    script = (PROFILE / "seed-project.sh").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()

    assert "--user 10001:10001" in script
    assert '--env "PROJECT_REVISION=$PROJECT_REVISION"' in script
    assert script.index("tar -xf /seed.tar -C /data/project") < script.index(
        "git -C /data/project init --initial-branch=main"
    )
    assert script.index("git -C /data/project init --initial-branch=main") < script.index(
        "git -C /data/project add --all"
    ) < script.index('commit --message "Seed project at $PROJECT_REVISION"')
    assert script.count("commit --message") == 1
    assert '-c user.name="Journal project owner"' in script
    assert '-c user.email="journal-project-owner@localhost"' in script
    assert "a `main` Git repository" in runbook
    assert "first commit as uid/gid 10001 with `PROJECT_REVISION` in the message" in runbook


def test_writer_build_uses_a_sanitized_commit_matched_context():
    script = (PROFILE / "build-writer.sh").read_text()

    assert "RUNTIME_SOURCE HEAD must equal PROFILE_REVISION" in script
    assert "status --porcelain --untracked-files=all" in script
    assert 'git -C "$RUNTIME_SOURCE" archive --format=tar "$PROFILE_REVISION"' in script
    assert "docker/Dockerfile" in script
    assert "docker/entrypoint.sh" in script
    assert "docker/hosted-journal" in script
    assert "install.sh" in script
    assert "update_steps.json" in script
    assert "install.py" not in script
    assert "docker/supervisor-codex-login" in script
    assert "docker/supervisor-codex-ready" in script
    assert "docker/supervisor-codex-plan-launcher.py" in script
    assert "docs/supervisor/v1/live-smoke-setup.py" in script
    assert 'tar -xf "$BUILD_CONTEXT/runtime.tar"' in script
    assert '"$BUILD_CONTEXT/src/commit"' in script
    assert '"$PROFILE_REVISION" > "$BUILD_CONTEXT/src/commit"' in script
    assert '"$BUILD_CONTEXT"' in script


def test_writer_image_archives_and_copies_every_runtime_script():
    build = (PROFILE / "build-writer.sh").read_text()
    dockerfile = (ROOT / "docker" / "Dockerfile").read_text()
    entrypoint = (ROOT / "docker" / "entrypoint.sh").read_text()
    hosted = (ROOT / "docker" / "hosted-journal").read_text()
    plan_launcher = (ROOT / "docker" / "supervisor-codex-plan-launcher.py").read_text()
    setup_path = PROFILE / "live-smoke-setup.py"
    setup = setup_path.read_text()
    archive = build.split(
        'git -C "$RUNTIME_SOURCE" archive --format=tar "$PROFILE_REVISION" --', 1
    )[1].split('> "$BUILD_CONTEXT/runtime.tar"', 1)[0]
    sources = (
        "src",
        "install.sh",
        "update_steps.json",
        "docker/Dockerfile",
        "docker/entrypoint.sh",
        "docker/hosted-journal",
        "docker/supervisor-codex-login",
        "docker/supervisor-codex-ready",
        "docker/supervisor-codex-plan-launcher.py",
        "docs/supervisor/v1/live-smoke-setup.py",
        "docs/supervisor/v1/supervisor-proposal-writer-rows.py",
    )
    copies = (
        "COPY --chown=root:root src /opt/agent-journal/src",
        "COPY --chown=root:root install.sh update_steps.json /opt/agent-journal/",
        "COPY --chown=root:root --chmod=755 docker/entrypoint.sh docker/hosted-journal /usr/local/bin/",
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-login docker/supervisor-codex-ready /usr/local/bin/",
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-plan-launcher.py /usr/local/bin/supervisor-codex-plan-launcher",
        "COPY --chown=root:root --chmod=755 docs/supervisor/v1/live-smoke-setup.py /usr/local/bin/supervisor-live-setup",
        "COPY --chown=root:root --chmod=755 docs/supervisor/v1/supervisor-proposal-writer-rows.py /usr/local/bin/supervisor-proposal-writer-rows",
    )

    assert all(source in archive for source in sources)
    assert all(copy in dockerfile for copy in copies)
    old_installer = ROOT / "install.py"
    assert not old_installer.exists() and not old_installer.is_symlink()
    assert (ROOT / "install.sh").is_file() and (ROOT / "update_steps.json").is_file()
    assert "3.14.10-slim-bookworm@sha256:9974e24551f9e7ca172cf284d85b8ab3e031d22d945f7026ede7a8279118c9f1" in dockerfile
    assert "JOURNAL_ROOT=/data/project" in dockerfile
    assert "JOURNAL_PORT=8421" in dockerfile
    assert "EXPOSE 8421" in dockerfile
    assert "EXPOSE 8421 8440" not in dockerfile


    assert "127.0.0.1:8421/journal/health" in dockerfile
    install_script = (ROOT / "install.sh").read_text()
    assert 'if [ -d "$HERE/src/journal" ]; then' in install_script
    local_source = install_script.split('if [ -d "$HERE/src/journal" ]; then', 1)[1].split("else", 1)[0]
    assert 'SRC="$HERE/src"' in local_source and "git clone" not in local_source
    assert '"$SRC/commit"' in install_script and "journal.py setup" in install_script
    assert 'AGENT_JOURNAL_YES=1 sh /opt/agent-journal/install.sh' in entrypoint
    assert '"$ROOT/bin/journal" serve' in entrypoint
    assert "JOURNAL_ROOT=\"$PROJECT\" JOURNAL_PORT=8421" in entrypoint
    assert "commands.login_apart" not in entrypoint
    assert "8440" not in entrypoint and "/ready" not in entrypoint
    assert 'exec "$PROJECT/.journal/bin/journal" "$@"' in hosted
    assert 'PROGRAM = "/opt/agent-journal/src/journal.py"' in plan_launcher
    assert 'sys.path.insert(0, "/opt/agent-journal/src")' in setup
    assert 'ROOT = Path("/data/project")' in setup
    assert 'API = "http://127.0.0.1:8421"' in setup
    assert 'CHECK_TITLE = "Supervisor live smoke failure"' in setup
    assert 'CHECK_BRIEF = "This smoke check intentionally fails so the supervisor has one current failure to diagnose."' in setup
    assert 'TEMPLATE_BRIEF = "Read the deliberately failing smoke check' in setup
    assert 'CHECK_COMMAND = "false"' in setup
    assert 'This smoke check intentionally fails' in setup
    assert '"supervisor_reserved": True' in setup
    assert 'WAIT_SECONDS = 300' in setup
    assert '"X-Journal-Env": "main"' in setup
    assert '"max_turns_per_day": 1' in setup

    project_command = (ROOT / "src" / "journal" / "support" / "project_command.py").read_text()
    installed_parts = ("journal", "supervisor", "sync_server", "journal.py", "journal.sh")
    assert all((ROOT / "src" / part).exists() for part in installed_parts)
    assert 'for name in journal supervisor sync_server journal.py journal.sh; do' in install_script
    runtime_scripts = (
        ROOT / "docker" / "entrypoint.sh",
        ROOT / "docker" / "hosted-journal",
        ROOT / "docker" / "supervisor-codex-login",
        ROOT / "docker" / "supervisor-codex-ready",
        ROOT / "docker" / "supervisor-codex-plan-launcher.py",
        PROFILE / "live-smoke-setup.py",
        PROFILE / "supervisor-proposal-writer-rows.py",
        ROOT / "src" / "hosted_login.py",
    )
    assert all(script.is_file() for script in runtime_scripts)
    assert (ROOT / "src" / "login_throttle.py").is_file()
    assert 'exec "$PROJECT/.journal/bin/journal" "$@"' in hosted
    assert 'return self.root / ".journal" / "bin" / "journal"' in project_command
    assert (ROOT / "src" / "journal.py").is_file()

    setup_command = (ROOT / "src" / "journal" / "console" / "commands" / "setup_command.py").read_text()
    journal_cli = (ROOT / "src" / "journal.py").read_text()
    config = (ROOT / "src" / "journal" / "config.py").read_text()
    server = (ROOT / "src" / "journal" / "http" / "server.py").read_text()
    health_route = (ROOT / "src" / "journal" / "http" / "routes" / "routes.py").read_text()
    health_controller = (ROOT / "src" / "journal" / "http" / "controllers" / "journal.py").read_text()
    assert "self.shim()" in setup_command
    assert 'if argv[:1] == ["serve"]:' in journal_cli and "app.runtime().run()" in journal_cli
    assert 'port = int(os.environ.get("JOURNAL_PORT", "8420"))' in config
    assert 'span = 1 if "JOURNAL_PORT" in os.environ else 20' in config
    assert 'os.environ.get("JOURNAL_HOST", "127.0.0.1")' in config
    assert "ThreadingServer((self.config.host, port), handler)" in server
    assert '("health", journal.health)' in health_route and "def health(" in health_controller
    assert (ROOT / "src" / "journal" / "http" / "server.py").is_file()
    assert (ROOT / "src" / "journal.sh").is_file()
    hosted_login = ROOT / "src" / "hosted_login.py"
    assert hosted_login.is_file()
    python_scripts = (
        ROOT / "src" / "journal.py",
        ROOT / "docker" / "supervisor-codex-plan-launcher.py",
        setup_path,
        hosted_login,
    )
    for script in python_scripts:
        for module in journal_imports(script):
            module_path = ROOT / "src" / Path(*module.split("."))
            module_exists = module_path.with_suffix(".py").is_file() or (module_path / "__init__.py").is_file()
            assert module_exists, (script, module)


def test_proposal_case_harness_resets_only_the_project_and_collects_writer_rows():
    stage = (PROFILE / "stage-proposal-case.sh").read_text()
    setup = (PROFILE / "setup-live-smoke.sh").read_text()
    entrypoint = (PROFILE / "gateway-entrypoint.sh").read_text()
    reconcile = (PROFILE / "journal-supervisor-reconcile").read_text()
    collector = (PROFILE / "collect-proposal-case.py").read_text()
    writer_rows = (PROFILE / "supervisor-proposal-writer-rows.py").read_text()
    setup_program = (PROFILE / "live-smoke-setup.py").read_text()
    writer_build = (PROFILE / "build-writer.sh").read_text()
    dockerfile = (ROOT / "docker" / "Dockerfile").read_text()
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()

    assert "VOLUME=journal-supervisor-smoke_writer_state" in stage
    assert "'rm -rf /data/project && mkdir -p /data/project'" in stage
    assert "down --volumes" not in stage
    assert all("/data/home" not in line for line in stage.splitlines() if "rm -rf" in line)
    assert "seed-project.sh" in stage and "setup-live-smoke.sh" in stage
    assert "cat > /run/journal-proposal-case-seed.json' < \"$SEED_DIR/case-seed.json\"" in stage
    assert "docs/supervisor/v2/proposal-evaluation-cases.json" in stage
    assert "wake_target(load_seed" in stage
    assert stage.index('"$ROOT/docs/supervisor/v1/setup-live-smoke.sh"') < stage.index('clear_hints\nprintf \'%s\\n\' "$CASE_WAKE"')
    assert 'journal-supervisor-case-wake' in stage and 'chmod 0444' in stage
    assert 'if [ ! -r "$case_wake_file" ]; then' in entrypoint
    assert 'watch-events' in entrypoint
    assert 'scheduled|quiet)' in reconcile
    assert 'event:*:PSU-[0-9][0-9])' in reconcile
    assert 'reconcile event "$event_kind" "$event_id"' in reconcile
    assert 'case_wake=$1' in reconcile
    assert "read_case_wake(gateway_state, case_wake" in launcher
    assert '"/opt/journal-supervisor/bin/journal-supervisor-reconcile", case_wake, NULL' in launcher
    assert "JOURNAL_SUPERVISOR_CASE_ID" in setup and "/usr/local/bin/supervisor-live-setup" in setup
    assert "load_seed(CASE_SEED_FILE, case_id)" in setup_program
    assert "case_task_specs(seed)" in setup_program
    assert "case_check_marker(seed[\"case_id\"])" in setup_program
    assert "marker.parent.rmdir()" in setup_program
    assert "configure_v2_grant" in setup_program
    assert '"watched_plans": settings["watched_plans"]' in setup_program
    assert "proposal-evaluation-cases-v1.json" not in dockerfile
    assert "proposal-evaluation-cases-v1.json" not in writer_build
    assert "journal-supervisor-transport" in collector
    assert "supervisor-proposal-writer-rows" in collector
    assert '"docker", "run", "--rm", "--network", "none"' in collector
    assert "journal-supervisor-smoke_writer_state" in collector
    assert '"--entrypoint"' in collector
    assert '"exec"' not in collector
    assert '"SupervisorActionReceipt"' in writer_rows and '"SupervisorUsage"' in writer_rows
    assert all(f'"{entry_type}"' in writer_rows for entry_type in (
        "SupervisorProposalReceipt", "SupervisorProposalDecision", "SupervisorWakeup",
    ))
    assert "proposal-evaluation-results.jsonl" in collector and "supervisor/v2" in collector
    assert "SupervisorCredential" not in writer_rows


def test_live_setup_configures_an_enrollment_for_its_driver_environment(app, monkeypatch):
    fixture = seeded(app)
    monkeypatch.setattr(type(fixture.authority.agents), "is_running", lambda _self, _environment: True)
    try:
        grant, _token, _principal = admitted(fixture)
        setup = live_setup_module()
        request_body = {}

        def apply_change(path, body):
            request_body.update(path=path, body=body)
            try:
                changed, _token = fixture.authority.change(fixture.owner, body)
            except SupervisorFailure as failure:
                return failure.status, {}, {"error": str(failure)}
            return 200, {}, changed

        monkeypatch.setattr(setup, "request", apply_change)
        settings = SupervisorGrant.from_version_one(grant).data()
        version = setup.configure_v2_grant(grant, {"grant_v2": settings})
        configured = fixture.authority.owner_control(fixture.owner, fixture.owner_environment.row_id)["grant"]

        assert fixture.owner_environment.row_id != grant["driver_environment_id"]
        assert request_body["path"] == "/_supervisor/v1/enrollment/change"
        assert request_body["body"]["change"]["grant"]["environment_id"] == grant["driver_environment_id"]
        assert version == grant["grant_version"] + 1
        assert configured["environment_id"] == fixture.driver_environment.row_id
    finally:
        fixture.authority.secrets_store.drop(fixture.credentials)


def test_live_setup_keeps_the_failure_reason_after_revoking_the_grant():
    main = live_setup_function_source("main")

    assert 'raise SetupFailure(f"{error}; the grant was revoked") from error' in main


def test_hosted_compose_requires_a_private_login_before_publishing_caddy():
    compose = (ROOT / "docker" / "compose.yaml").read_text()
    caddyfile = (ROOT / "docker" / "Caddyfile").read_text()
    updater = (ROOT / "docker" / "update.sh").read_text()
    journal = compose.split("  journal:\n", 1)[1].split("\n  hosted-login:", 1)[0]
    login = compose.split("  hosted-login:\n", 1)[1].split("\n  caddy:", 1)[0]
    caddy = compose.split("  caddy:\n", 1)[1].split("\n  backup:", 1)[0]

    assert "JOURNAL_HOST: 0.0.0.0" in journal and 'JOURNAL_PORT: "8421"' in journal
    assert 'expose:\n      - "8421"' in journal and "ports:" not in journal
    assert "JOURNAL_HOSTED_PASSWORD" not in journal
    assert 'JOURNAL_HOSTED_PASSWORD: ${JOURNAL_HOSTED_PASSWORD:?set JOURNAL_HOSTED_PASSWORD in .env}' in login
    assert 'user: "10002:10001"' in login
    assert 'entrypoint: ["python3", "-P", "/opt/agent-journal/src/hosted_login.py"]' in login
    assert 'expose:\n      - "8440"' in login and "ports:" not in login
    assert "read_only: true" in login and "cap_drop: [ALL]" in login
    assert "volumes:" not in login and "JOURNAL_HOSTED_UPSTREAM: http://journal:8421" in login
    assert "ports:" in caddy and 'reverse_proxy hosted-login:8440' in caddyfile
    assert 'JOURNAL_IMAGE="$ref" docker compose --profile journal up -d --no-deps --pull always journal hosted-login' in updater
    assert "JOURNAL_REVISION or src/commit is required" in (ROOT / "docker" / "Dockerfile").read_text()
    assert "JOURNAL_REVISION=$PROFILE_REVISION" in (PROFILE / "build-writer.sh").read_text()
    assert "build-args: JOURNAL_REVISION=${{ github.sha }}" in (ROOT / ".github" / "workflows" / "docker-image.yml").read_text()


def test_codex_plan_driver_is_pinned_device_auth_and_uses_the_owner_plan_lifecycle():
    compose = read_json(PROFILE / "compose.json")
    manifest = read_json(PROFILE / "manifest.json")
    runbook = (PROFILE / "RUNBOOK.md").read_text()
    writer = compose["services"]["writer"]
    gateway = compose["services"]["gateway"]
    backup = compose["services"]["backup"]
    dockerfile = (ROOT / "docker" / "Dockerfile").read_text()
    entrypoint = (ROOT / "docker" / "entrypoint.sh").read_text()
    driver_launcher = (ROOT / "docker" / "supervisor-codex-plan-launcher.py").read_text()
    agent_launcher = (ROOT / "src" / "journal" / "engine" / "agent_launcher.py").read_text()
    grant_model = (ROOT / "src" / "journal" / "models" / "supervisor_grant.py").read_text()
    setup = (PROFILE / "live-smoke-setup.py").read_text()
    host_setup = (PROFILE / "setup-live-smoke.sh").read_text()
    login = (ROOT / "docker" / "supervisor-codex-login").read_text()
    ready = (ROOT / "docker" / "supervisor-codex-ready").read_text()
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()
    assert (PROFILE / "setup-live-smoke.sh").stat().st_mode & stat.S_IXUSR

    assert "npm install -g @openai/codex@0.165.0" in dockerfile
    assert "CODEX_HOME" not in dockerfile and "CODEX_API_KEY" not in dockerfile
    assert writer["environment"]["JOURNAL_CODEX_HOME"] == "/var/lib/journal-codex"
    assert writer["environment"]["JOURNAL_PLAN_DRIVER_SOCKET"] == "/run/journal-plan-driver.sock"
    assert writer["cap_add"] == ["SETUID", "SETGID", "SETPCAP"]
    assert writer["read_only"] is True
    assert "no-new-privileges:true" in writer["security_opt"]
    assert writer["tmpfs"] == ["/tmp", "/run:mode=1777"]
    assert gateway["tmpfs"] == ["/tmp", "/home/node/.cache:uid=1000,gid=1000,mode=0700"]
    assert gateway["extra_hosts"] == ["writer:10.76.20.10"]
    assert "codex_driver_state:/var/lib/journal-codex" in writer["volumes"]
    assert "codex_driver_state" in compose["volumes"]
    assert "codex_driver_state" not in " ".join(gateway["volumes"] + backup["volumes"])
    assert "codex_driver_credentials" not in json.dumps(compose)
    assert "supervisor-codex-ready" in entrypoint
    assert "setpriv --reuid 10003 --regid 10003 --clear-groups supervisor-codex-ready" in entrypoint
    assert "supervisor-codex-plan-launcher" in entrypoint
    assert "complete supervisor-codex-login before starting the writer" in entrypoint
    assert "/run/journal-plan-driver-server.pid" in entrypoint
    assert "setfacl" in agent_launcher and "u:10003:rwX" in agent_launcher
    assert "JOURNAL_PLAN_DRIVER_SOCKET" in agent_launcher and "plan_launched" in agent_launcher
    assert "peer_uid != JOURNAL_UID" in driver_launcher
    assert "peer_pid != server_pid" in driver_launcher
    assert "only a numbered Plan environment" in driver_launcher
    assert "os.setgid(DRIVER_GID)" in driver_launcher and "os.setuid(DRIVER_UID)" in driver_launcher
    assert "PR_CAPBSET_DROP" in driver_launcher and "PR_SET_NO_NEW_PRIVS" in driver_launcher
    assert '"CODEX_HOME": CODEX_HOME' in driver_launcher
    assert '"JOURNAL_CODEX_HOME": CODEX_HOME' in driver_launcher
    assert '"PATH": "/usr/local/bin:/usr/bin:/bin"' in driver_launcher
    assert "codex login --device-auth" in login
    assert "--with-api-key" not in login + entrypoint
    assert "stat -c %u" in ready and "stat -c %a" in ready
    assert '"/usr/local/bin/supervisor-codex-ready"' in launcher
    assert '"10003:10003"' in launcher
    assert '"down"' in launcher and '"-v"' not in launcher
    assert "if len(sys.argv) != 1" in setup
    assert "start the owner's real Codex session on the designated writer" in setup
    assert "PlanMode.SOLO" in setup and "plans.plan_agents" in setup
    assert '"plan", "ready"' in setup and '"plan", "approve"' in setup and '"plan", "start"' in setup
    assert "SupervisorLink" in setup and "plan_agents.is_running(environment)" in setup
    assert '"/_supervisor/v1/enrollment"' in setup
    assert '"max_input_tokens_per_turn": 80000' in setup
    assert '"max_output_tokens_per_turn": 16000' in setup
    assert '"max_provider_requests_per_turn": 12' in setup
    assert '"max_turns_per_day": 1' in setup
    assert '"max_cost_microusd_per_day": 1000000' in setup
    contract = read_json(PROFILE / "contract.schema.json")
    budget_limits = contract["$defs"]["BudgetLimits"]["properties"]
    input_limit = budget_limits["max_input_tokens_per_turn"]
    assert input_limit == {"type": "integer", "minimum": 1, "maximum": 80000}
    assert [field for field in budget_limits if "cost" in field] == ["max_cost_microusd_per_day"]
    assert budget_limits["max_cost_microusd_per_day"]["description"] == (
        "The grant's only daily cost cap, expressed in micro-USD."
    )
    assert "MAX_INPUT_TOKENS_PER_TURN = 80_000" in grant_model
    assert "80,000 input tokens" in (PROFILE / "STAGING-REPORT.md").read_text()
    assert "$0.48 per run" in (PROFILE / "STAGING-REPORT.md").read_text()
    assert "active_workers = workers.global_matching(state=WorkerState.DISPATCHED)" in setup and "if active_workers:" in setup
    assert '"mode": "bounded_write"' in setup
    assert '"/run/journal_supervisor_credential"' in setup
    assert "except (OSError, SetupFailure) as error:" in setup and "revoke(grant_id)" in setup
    assert "STAGING_AUTHORIZED" in host_setup and "compose cp writer:/run/journal_supervisor_credential" in host_setup
    assert "normal_driver_separate_execution_identity" in manifest["launch_gates"]
    assert manifest["launch"]["enrollment_enabled"] is False
    assert manifest["topology"][0]["codex_driver"]["permissions"].startswith("the Dockerfile pre-creates /var/lib/journal-codex as uid/gid 10003 mode 0700")
    assert manifest["volumes"]["codex_driver_state"]["owner"] == "10003:10003"
    assert manifest["execution_identity_contract"]["status"].startswith("packaged; dedicated-VM B10")
    assert manifest["launch_gates"]["normal_driver_separate_execution_identity"] is False
    assert "uid/gid 10003" in runbook and "B10 remains false" in runbook


def test_live_provider_request_cap_is_persisted_in_the_owner_grant():
    setup = (PROFILE / "live-smoke-setup.py").read_text()
    bridge_environment = (PROFILE / "journal-supervisor-bridge-environment.sh").read_text()
    bridge = (ROOT / "src" / "supervisor_bridge" / "bridge.py").read_text()
    bridge_state = (ROOT / "src" / "supervisor_bridge" / "state.py").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()
    report = (PROFILE / "STAGING-REPORT.md").read_text()

    assert '"max_provider_requests_per_turn": 12' in setup
    assert setup.count('"limits": GRANT_LIMITS') == 2
    assert "authority.has_enrollment_grant()" in setup
    assert 'grant_token_limits(observed["snapshot"], run)' in bridge
    assert 'state["provider_requests"] + count <= state["limits"]["max_provider_requests_per_turn"]' in bridge_state
    assert "JOURNAL_SUPERVISOR_ADMISSION_URL" in bridge_environment
    assert "max_provider_requests_per_turn" not in bridge_environment
    assert "12 request, one-turn" in runbook
    assert "already enrolled 8-request grant stays at 8" in runbook
    assert "No Gateway or OpenClaw tool-list rebuild changes an existing grant" in runbook
    assert "12 requests" in report
    assert "journal__journal_supervisor-observe" in report
    assert "journal__journal_supervisor-run_or_propose" in report
    assert "no tool arguments were inspected" in report


def test_live_output_budget_covers_the_observed_turn_under_the_daily_cost_cap():
    setup = (PROFILE / "live-smoke-setup.py").read_text()
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()
    report = (PROFILE / "STAGING-REPORT.md").read_text()
    contract = (PROFILE / "contract.md").read_text()

    assert '"max_output_tokens_per_turn": 16000' in setup
    assert '"max_provider_requests_per_turn": 12' in setup
    assert '\\\"max_output_tokens_per_turn\\\": 16000' in launcher
    assert 'all_values_equal(compact, "maxTokens", "8000")' in launcher
    assert "5,260 with `journal__journal_supervisor-run_or_propose`" in report
    assert "They total the 8,000-token turn cap" in report
    assert "twice measured use over four generations" in report
    assert "12 requests allowing up to six generations" in report
    assert "16,000 output" in runbook
    assert "OpenClaw `maxTokens` remains 8,000 per generation" in runbook
    assert "conservative token charge is $0.48" in contract
    assert "below the $1.00 daily cap" in contract


def test_plan_driver_socket_uses_a_server_and_driver_only_group():
    manifest = read_json(PROFILE / "manifest.json")
    dockerfile = (ROOT / "docker" / "Dockerfile").read_text()
    entrypoint = (ROOT / "docker" / "entrypoint.sh").read_text()
    driver = (ROOT / "docker" / "supervisor-codex-plan-launcher.py").read_text()
    inbox = (ROOT / "src" / "supervisor" / "inbox.py").read_text()
    launch_file = (ROOT / "src" / "supervisor" / "launch_file.py").read_text()
    agent_launcher = (ROOT / "src" / "journal" / "engine" / "agent_launcher.py").read_text()
    launch = (ROOT / "src" / "journal" / "launcher" / "launch.py").read_text()
    provider = (ROOT / "src" / "journal" / "providers" / "provider.py").read_text()
    hook_script = (ROOT / "src" / "journal" / "hooks" / "hook.sh").read_text()
    socket_source = (ROOT / "src" / "journal" / "support" / "supervisor_socket.py").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()

    assert "groupadd --gid 10031 plan-supervisor-socket" in dockerfile
    assert "usermod --append --groups plan-supervisor-socket journal" in dockerfile
    assert "setpriv --reuid 0 --regid plan-supervisor-socket --clear-groups mkdir -m 2770 -p /run/journal-plan-driver-supervisors" in entrypoint
    assert 'stat -c %g /run/journal-plan-driver-supervisors' in entrypoint and 'stat -c %a /run/journal-plan-driver-supervisors' in entrypoint
    assert "SUPERVISOR_SOCKET_GID = 10031" in driver and "os.setgroups([SUPERVISOR_SOCKET_GID])" in driver
    assert '"supervisor_socket": str(supervisor_socket)' in agent_launcher
    assert '"protocol": 1' in agent_launcher and '"runtime" / "inboxes" / environment' in agent_launcher
    assert "JOURNAL_PLAN_DRIVER_SUPERVISOR_SOCKET" in driver
    assert 'PLAN_DRIVER_SUPERVISOR_SOCKET_DIRECTORY = Path("/run/journal-plan-driver-supervisors")' in socket_source
    assert "PLAN_DRIVER_SUPERVISOR_SOCKET_GROUP = 10031" in socket_source
    assert "shared_group" in inbox and "0o2770" in inbox and "0o660" in inbox
    assert 'Inbox(Path(self.data["socket"]), Path(self.data["announce"]), self.data.get("socket_group"))' in launch_file
    assert "PLAN_DRIVER_SUPERVISOR_SOCKET_GROUP" in launch and '"socket_group"' in launch
    assert "/run/journal-plan-driver-supervisors/plan-<n>.sock" in manifest["topology"][0]["codex_driver"]["supervisor_socket"]
    assert "root:10031 mode 2770" in runbook and "journal uid 10001 and Plan driver uid 10003" in runbook
    assert 'PLAN_DRIVER_HOOK_SCRIPT = Path("/opt/agent-journal/src/journal/hooks/hook.sh")' in launch
    assert "self.provider.wire_hooks(folder, PLAN_DRIVER_HOOK_SCRIPT" in launch
    assert "def hook_command(self, root: Path, script: Path = HOOK_SCRIPT)" in provider
    driver_hook_environment = (
        'if [ -n "${JOURNAL_HOOK_RUNTIME:-}" ]; then\n'
        "    runtime=$JOURNAL_HOOK_RUNTIME\n"
        "    port=${JOURNAL_PORT:-}\nelse"
    )
    assert driver_hook_environment in hook_script
    assert '"$(dirname "$0")/../version.py"' in hook_script
    assert "COPY --chown=root:root src /opt/agent-journal/src" in dockerfile


def test_live_setup_checks_driver_login_as_uid10003_before_owner_setup():
    setup = (PROFILE / "live-smoke-setup.py").read_text()
    host_setup = (PROFILE / "setup-live-smoke.sh").read_text()
    driver_check = "compose exec --user 10003:10003 -T writer /usr/local/bin/supervisor-codex-ready"
    owner_setup = "compose exec --user journal -T writer /usr/local/bin/supervisor-live-setup"

    assert "/var/lib/journal-codex" not in setup and "auth.json" not in setup and "CODEX_HOME" not in setup
    assert "os.geteuid()" not in setup and ".stat()" not in setup
    assert driver_check in host_setup and owner_setup in host_setup
    assert host_setup.index(driver_check) < host_setup.index(owner_setup)
    assert 'os.environ.get("JOURNAL_ROOT") != str(ROOT)' in setup
    assert "if TOKEN_FILE.exists():" in setup


def test_live_setup_reads_plan_and_child_rows_inside_the_main_environment_scope():
    resume = live_setup_function_source("resume_plan")
    wait = live_setup_function_source("wait_for_codex_plan")
    command = live_setup_function_source("command")
    runtime = live_setup_function_source("require_runtime")

    assert "with scope.environment(main.row_id):\n        owner_agent = agents.environment_main_agent(main.row_id)" in runtime
    assert "with scope.environment(main.row_id):\n        plan = plans.find(plan_id)\n        phases = plans.plan_phases(plan)\n        tasks = plans.plan_tasks(plan)" in resume
    assert "with scope.environment(environment_id):\n            plan = plans.find(plan_id)" in wait
    assert wait.index("while time.monotonic() < deadline:") < wait.index("app.container.get(Connection).cache.cleared()") < wait.index("agent = plan_agents.agent(plan)")
    assert '"env": "main"' in command


def test_live_setup_resumes_only_its_started_unenrolled_plan():
    signature = live_setup_function_source("setup_plan_matches")
    smoke_tasks = live_setup_function_source("smoke_tasks_match")
    resume = live_setup_function_source("resume_plan")
    require_runtime = live_setup_function_source("require_runtime")
    make_plan = live_setup_function_source("make_plan")
    authority = (ROOT / "src" / "journal" / "supervisor_authority.py").read_text()

    assert "plan.title == PLAN_TITLE" in signature and "plan.brief == PLAN_BRIEF" in signature
    assert "plan.state == PlanState.STARTED" in signature
    assert "plan.mode == PlanMode.SOLO" in signature and "plan.mode_chosen" in signature
    assert "phases[0].title == PHASE_TITLE" in signature
    assert "smoke_tasks_match(tasks)" in signature
    assert "task.title == TASK_TITLE" in smoke_tasks and "task.brief == TASK_BRIEF" in smoke_tasks
    assert "case_task_specs(seed)" in smoke_tasks
    assert "task.supervisor_reserved == spec[\"supervisor_reserved\"]" in smoke_tasks
    assert "task.state in {TaskState.OPEN, TaskState.STARTED}" in smoke_tasks
    assert "if not setup_plan_matches(plan, phases, tasks):" in resume
    assert "if authority.has_enrollment_grant():" in resume
    assert "def has_enrollment_grant(self) -> bool:" in authority
    assert "return bool(self._latest_entries())" in authority
    assert 'if TOKEN_FILE.exists():' in require_runtime
    assert "if plan_id := existing_plan_id(existing):\n        return resume_plan(app, main, plan_id)" in make_plan
    assert "check_id = setup_check_id(app, seed)" in resume
    assert "return plan_id, check_id, setup_template_id(app)" in resume
    assert resume.count("return ") == 1


def test_live_setup_leaves_one_open_task_and_records_its_failure_after_enrollment():
    make_plan = live_setup_function_source("make_plan")
    main = live_setup_function_source("main")
    command = live_setup_function_source("command")
    ensure_task = live_setup_function_source("ensure_smoke_task")
    run_check = live_setup_function_source("run_bound_check")

    assert make_plan.index('"supervisor_reserved": True') < make_plan.index('command("plan", "ready"')
    assert main.index("wait_for_codex_plan") < main.index("ensure_smoke_task")
    assert main.index("ensure_smoke_task") < main.index('request("/_supervisor/v1/enrollment"')
    assert main.index('request("/_supervisor/v1/enrollment"') < main.index("run_bound_check(check_id)")
    assert 'smoke_tasks_match(tasks)' in ensure_task and 'tasks[0].supervisor_reserved' in ensure_task
    refresh = ensure_task.index("app.container.get(Connection).cache.cleared()")
    reread = ensure_task.index("plan = plans.find(plan_id)")
    assert refresh < reread
    assert 'tasks[0].state == TaskState.OPEN' in ensure_task and 'tasks_repo.holder(tasks[0]) is None' in ensure_task
    assert 'not tasks_repo.unavailable_task_ids(tasks)' in ensure_task and 'not tasks[0].delegated' in ensure_task
    assert 'plans.started_task(plan) is None' in ensure_task
    assert 'command("check", "run", str(check_id), expected_code=1)' in run_check
    assert 'output.startswith(f"check {check_id} failed:")' in run_check
    assert main.index("run_bound_check(check_id)") < main.index("write_token(token)")
    assert main.count("run_bound_check(check_id)") == 1
    assert "answer.get(\"code\") != expected_code" in command


def test_psu04_live_setup_accepts_only_a_started_diagnostic_and_open_reserved_anchor():
    setup = live_setup_module()
    seed = seed_case(load_case(ROOT / "docs/supervisor/v2/proposal-evaluation-cases.json", "PSU-04"))
    diagnostic = SimpleNamespace(
        title=seed["tasks"]["title"], brief=seed["tasks"]["brief"], state=TaskState.STARTED,
        supervisor_reserved=False,
    )
    anchor = seed["tasks"]["eligibility_anchor"]
    enrollment_task = SimpleNamespace(
        title=anchor["title"], brief=anchor["brief"], state=TaskState.OPEN, supervisor_reserved=True,
    )

    assert setup.smoke_tasks_match([diagnostic, enrollment_task], seed)
    enrollment_task.state = TaskState.STARTED
    assert not setup.smoke_tasks_match([diagnostic, enrollment_task], seed)


def test_latest_run_passed_setup_controls_failure_then_pass_and_removes_its_run_state(tmp_path, monkeypatch):
    setup = live_setup_module()
    seed = seed_case(load_case(ROOT / "docs/supervisor/v2/proposal-evaluation-cases.json", "PSU-06"))
    marker = tmp_path / "private-check-state" / "PSU-06-passed"
    observed = []

    monkeypatch.setattr(setup, "case_check_marker", lambda case_id: marker)

    def run_check(_noun, _verb, check_id, *, expected_code):
        verdict = "failed" if expected_code == 1 else "passed"
        observed.append((verdict, marker.exists()))
        return f"check {check_id} {verdict}: synthetic result"

    monkeypatch.setattr(setup, "command", run_check)
    setup.run_case_checks(73, seed)

    assert observed == [("failed", False), ("passed", True)]
    assert not marker.exists()


def test_plan_driver_launch_writes_logs_only_to_its_own_home(tmp_path, monkeypatch):
    import json
    import tomllib
    from types import SimpleNamespace

    import journal.launcher.launch as launch_module
    from journal.providers.codex import Codex
    from journal.launcher.launch import PLAN_DRIVER_HOOK_SCRIPT
    from journal.support.supervisor_socket import PLAN_DRIVER_SUPERVISOR_SOCKET_GROUP, SupervisorSocket

    project = tmp_path / "project"
    project.mkdir()
    worktree = project / ".claude" / "worktrees" / "plan-1"
    worktree.mkdir(parents=True)
    hooks_file = worktree / ".codex" / "hooks.json"
    driver_home = tmp_path / "driver-home"
    driver_home.mkdir()
    launch_files = []
    launch_data = []

    def run_supervisor(command, **kwargs):
        launch_files.append(Path(command[-1]))
        launch_data.append(json.loads(Path(command[-1]).read_text()))
        return SimpleNamespace(returncode=0)

    def owner_port_read(*args, **kwargs):
        raise AssertionError("the Plan driver cannot read the owner's journal port")

    monkeypatch.setattr(launch_module.os, "getuid", lambda: 10003)
    monkeypatch.delenv("JOURNAL_PLAN_DRIVER_SOCKET", raising=False)
    monkeypatch.setenv("HOME", str(driver_home))
    monkeypatch.setenv("CODEX_HOME", str(driver_home))
    monkeypatch.setenv("JOURNAL_CODEX_HOME", str(driver_home))
    monkeypatch.setenv("JOURNAL_PORT", "8421")
    monkeypatch.setenv("JOURNAL_PLAN_DRIVER_SUPERVISOR_SOCKET", str(SupervisorSocket.plan_driver_path("plan-1")))
    monkeypatch.setattr(launch_module.Launch, "health_numbers", owner_port_read)
    monkeypatch.setattr(launch_module.Menu, "journal", owner_port_read)
    monkeypatch.setattr(launch_module.PageWait, "start", owner_port_read)
    monkeypatch.setattr(launch_module.subprocess, "run", run_supervisor)

    launch = launch_module.Launch.parse(
        ["codex", "--env", "plan-1", "--worktree", "plan-1", "--no-journal"], project
    )

    assert launch.run() == 0
    assert (driver_home / "journal-runtime" / "supervisor.log").is_file()
    assert launch_files == [driver_home / "journal-runtime" / "launches" / "plan-1.json"]
    assert launch_data[0]["socket"] == str(SupervisorSocket.plan_driver_path("plan-1"))
    assert launch_data[0]["socket_group"] == PLAN_DRIVER_SUPERVISOR_SOCKET_GROUP
    assert launch_data[0]["front"]["env"]["JOURNAL_PORT"] == "8421"
    assert launch_data[0]["front"]["env"]["JOURNAL_HOOK_RUNTIME"] == str(driver_home / "journal-runtime")
    assert launch_data[0]["front"]["env"]["JOURNAL_ROOT"] == str(project)
    assert launch_data[0]["front"]["env"]["JOURNAL_ENV"] == "plan-1"
    assert launch_data[0]["front"]["env"]["JOURNAL_LAUNCH"] == launch_data[0]["launch"]
    assert launch_data[0]["front"]["command"][-1] == "you lead plan 1 in this worktree; work its tasks here"
    assert str(project / ".journal") not in launch_data[0]["front"]["env"]["PATH"]
    hooks = json.loads(hooks_file.read_text())["hooks"]
    commands = [
        handler["command"]
        for groups in hooks.values()
        for group in groups
        for handler in group["hooks"]
    ]
    expected_hook = Codex().hook_command(project, PLAN_DRIVER_HOOK_SCRIPT)
    assert commands and set(commands) == {expected_hook}
    assert all(str(project / ".journal") not in command for command in commands)
    trusted = tomllib.loads((driver_home / "config.toml").read_text())["hooks"]["state"]
    assert trusted and all(key.startswith(f"{hooks_file.resolve()}:") for key in trusted)
    assert all(state["enabled"] and state["trusted_hash"].startswith("sha256:") for state in trusted.values())
    assert not (project / ".journal" / "runtime").exists()
    assert not (project / ".journal").exists()


def test_plan_driver_codex_config_trusts_only_its_worktree_and_journal_hooks_before_command(tmp_path, monkeypatch):
    import json
    import tomllib

    import journal.launcher.launch as launch_module
    from journal.providers.codex import Codex
    from journal.providers.support.status_line import StatusLine
    from journal.support.choice import Choice
    from journal.support.supervisor_socket import SupervisorSocket

    project = tmp_path / "project"
    worktree = project / ".claude" / "worktrees" / "plan-1"
    worktree.mkdir(parents=True)
    driver_home = tmp_path / "driver-home"
    driver_home.mkdir()
    hooks_file = worktree / ".codex" / "hooks.json"
    hooks_file.parent.mkdir()
    hooks = Codex().hook_block("sh /opt/agent-journal/src/journal/hooks/hook.sh")
    first_event = next(iter(hooks))
    hooks[first_event][0]["hooks"].append({"type": "command", "command": "/opt/customer/custom-hook"})
    hooks_file.write_text(json.dumps({"hooks": hooks}))
    config = driver_home / "config.toml"
    config.write_text('model = "gpt-6-luna"\n')

    monkeypatch.setattr(launch_module.os, "getuid", lambda: 10003)
    monkeypatch.setenv("HOME", str(driver_home))
    monkeypatch.setenv("CODEX_HOME", str(driver_home))
    monkeypatch.setenv("JOURNAL_CODEX_HOME", str(driver_home))
    monkeypatch.setenv("JOURNAL_PORT", "8421")
    monkeypatch.setenv("JOURNAL_PLAN_DRIVER_SUPERVISOR_SOCKET", str(SupervisorSocket.plan_driver_path("plan-1")))
    monkeypatch.setattr(launch_module.Menu, "journal", lambda self, *args: "")

    def command_after_config(self, choice, status):
        settings = tomllib.loads(config.read_text())
        assert settings["check_for_update_on_startup"] is False
        assert settings["model"] == "gpt-6-luna"
        assert settings["projects"] == {str(worktree.resolve()): {"trust_level": "trusted"}}
        states = settings["hooks"]["state"]
        journal_handlers = {
            (event, group_index, handler_index)
            for event, groups in hooks.items()
            for group_index, group in enumerate(groups)
            for handler_index, handler in enumerate(group["hooks"])
            if Codex.journal_paths(handler)
        }
        expected_keys = {
            f"{worktree.resolve()}/.codex/hooks.json:{Codex.state_name(event)}:{group_index}:{handler_index}"
            for event, group_index, handler_index in journal_handlers
        }
        assert set(states) == expected_keys
        assert all(state["enabled"] and state["trusted_hash"].startswith("sha256:") for state in states.values())
        return ["codex", "--headless"]

    monkeypatch.setattr(launch_module.Launch, "agent_command", command_after_config)
    launch = launch_module.Launch.parse(["codex", "--env", "plan-1", "--worktree", "plan-1"], project)
    result = launch.launch_file(Choice("plan-1"), StatusLine(project))

    assert result["front"]["command"] == ["codex", "--headless"]


def test_codex_home_volume_is_precreated_for_uid10003_and_login_refuses_wrong_owner():
    dockerfile = (ROOT / "docker" / "Dockerfile").read_text()
    login = (ROOT / "docker" / "supervisor-codex-login").read_text()
    ready = (ROOT / "docker" / "supervisor-codex-ready").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()

    assert "groupadd --gid 10003 codex-driver" in dockerfile
    assert "useradd --uid 10003 --gid codex-driver" in dockerfile
    assert "/var/lib/journal-codex" in dockerfile
    assert "chown codex-driver:codex-driver /var/lib/journal-codex" in dockerfile
    assert "chmod 700 /data/home /data/secrets /data/gateway /data/vault /var/lib/journal-codex" in dockerfile
    assert "supervisor-codex-login must run as uid/gid 10003" in login
    assert "Codex driver home must be pre-created as uid/gid 10003 with mode 0700" in login
    assert "stat -c %u" in login and "stat -c %g" in login and "stat -c %a" in login
    assert "chown" not in login
    assert "supervisor-codex-ready must run as uid/gid 10003" in ready
    assert "--user 10003:10003" in runbook
    assert "There is no separate login page" in runbook


def test_codex_device_login_is_fixed_and_operator_approved_before_the_smoke():
    login = (ROOT / "docker" / "supervisor-codex-login").read_text()
    ready = (ROOT / "docker" / "supervisor-codex-ready").read_text()
    compose = read_json(PROFILE / "compose.json")
    manifest = read_json(PROFILE / "manifest.json")
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()
    report = (PROFILE / "STAGING-REPORT.md").read_text()

    assert "supervisor-codex-login accepts no arguments" in login
    assert "codex login --device-auth" in login
    assert "CODEX_HOME" in login and "codex login --device-auth" in login
    assert "supervisor-codex-login must run as uid/gid 10003" in login
    assert "auth.json" in ready and "stat -c %g" in ready and "stat -c %a" in ready
    assert "codex_driver_state" in compose["services"]["writer"]["volumes"][1]
    assert "codex_driver_credentials" not in json.dumps(compose) + json.dumps(manifest)
    assert not (ROOT / "src" / "supervisor_bridge" / "codex_driver_secret_stage.c").exists()
    assert not (ROOT / "src" / "supervisor_bridge" / "build-driver-secret-stage.sh").exists()
    assert "docker compose" in runbook and "supervisor-codex-login" in runbook
    assert "codex login --device-auth" in runbook
    assert "docker compose down" in runbook and "codex_driver_state" in runbook
    assert "refresh tokens" in runbook.lower()
    assert "revoke the provisional grant" in runbook
    assert "codex_driver_credentials" not in launcher
    assert "build-driver-secret-stage" not in runbook
    assert "refresh tokens" in report.lower()
    assert "device-auth" in report
    assert "uid10003" in runbook and "read-only" in runbook
    assert "uid10003" in report and "read-only" in report


def test_gateway_build_packages_the_bridge_into_the_pinned_openclaw_image():
    script = (PROFILE / "build-gateway.sh").read_text()
    dockerfile = (PROFILE / "Dockerfile.gateway").read_text()
    wrapper = (PROFILE / "journal-supervisor-bridge").read_text()
    mcp_wrapper = (PROFILE / "journal-supervisor-mcp").read_text()
    bridge_environment = (PROFILE / "journal-supervisor-bridge-environment.sh").read_text()

    assert "RUNTIME_SOURCE HEAD must equal PROFILE_REVISION" in script
    assert "status --porcelain --untracked-files=all" in script
    assert 'git -C "$RUNTIME_SOURCE" archive --format=tar "$PROFILE_REVISION"' in script
    assert "src/supervisor_bridge" in script
    gateway_journal_files = (
        "src/journal/__init__.py",
        "src/journal/features/__init__.py",
        "src/journal/features/supervisor/capability_catalogue.py",
        "src/journal/features/supervisor/support/supervisor_operation_commands.py",
    )
    for source in gateway_journal_files:
        target = source.removeprefix("src/")
        assert source in script
        assert f"COPY {source} /opt/journal-supervisor/lib/{target}" in dockerfile
    assert "docs/supervisor/v1/Dockerfile.gateway" in script
    assert "docs/supervisor/v1/journal-supervisor-bridge" in script
    assert "docs/supervisor/v1/contract.schema.json" in script
    assert "COPY docs/supervisor/v1/contract.schema.json /opt/journal-supervisor/docs/supervisor/v1/contract.schema.json" in dockerfile
    assert "docs/supervisor/v1/journal-supervisor-environment.sh" in script
    assert "docs/supervisor/v1/journal-supervisor-bridge-environment.sh" in script
    assert "docs/supervisor/v1/journal-supervisor-mcp" in script
    assert "docs/supervisor/v1/journal-supervisor-reconcile" in script
    assert 'tar -xf "$BUILD_CONTEXT/runtime.tar"' in script
    assert '--tag "agent-journal-supervisor-gateway:$PROFILE_REVISION"' in script
    assert "--pull" in script
    assert "FROM ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5" in dockerfile
    assert "apt-get install -y --no-install-recommends python3" in dockerfile
    assert "COPY src/supervisor_bridge /opt/journal-supervisor/lib/supervisor_bridge" in dockerfile
    assert "COPY docs/supervisor/v1/journal-supervisor-bridge /opt/journal-supervisor/bin/journal-supervisor-bridge" in dockerfile
    assert "COPY docs/supervisor/v1/journal-supervisor-environment.sh /opt/journal-supervisor/bin/journal-supervisor-environment" in dockerfile
    assert "COPY docs/supervisor/v1/journal-supervisor-bridge-environment.sh /opt/journal-supervisor/bin/journal-supervisor-bridge-environment" in dockerfile
    assert "COPY docs/supervisor/v1/journal-supervisor-mcp /opt/journal-supervisor/bin/journal-supervisor-mcp" in dockerfile
    assert "COPY docs/supervisor/v1/journal-supervisor-reconcile /opt/journal-supervisor/bin/journal-supervisor-reconcile" in dockerfile
    assert "journal-supervisor-mcp" in dockerfile.split("RUN chmod 0555 ", 1)[1]
    assert "ENV PYTHONPATH=/opt/journal-supervisor/lib" in dockerfile
    assert "USER 1000:1000" in dockerfile
    assert 'exec env PYTHONPATH=/opt/journal-supervisor/lib python3 -m supervisor_bridge "$@"' in wrapper
    assert '. /opt/journal-supervisor/bin/journal-supervisor-bridge-environment' in mcp_wrapper
    assert 'exec /opt/journal-supervisor/bin/journal-supervisor-bridge mcp' in mcp_wrapper
    assert "ANTHROPIC_API_KEY" not in mcp_wrapper
    assert "JOURNAL_SUPERVISOR_ADMISSION_TOKEN=$(cat /run/secrets/journal_supervisor_credential)" in bridge_environment
    assert "JOURNAL_SUPERVISOR_ADMISSION_URL=https://writer:8422" in bridge_environment
    assert "JOURNAL_SUPERVISOR_TLS_CA_FILE" in bridge_environment
    assert "JOURNAL_SUPERVISOR_TLS_CA_FILE=/run/secrets/writer_supervisor_tls_ca" in bridge_environment
    assert "JOURNAL_SUPERVISOR_STATE_DIR" in bridge_environment
    assert "ANTHROPIC_API_KEY" not in bridge_environment


def test_gateway_entrypoint_and_reconcile_share_one_secret_environment():
    entrypoint = (PROFILE / "gateway-entrypoint.sh").read_text()
    environment = (PROFILE / "journal-supervisor-environment.sh").read_text()
    bridge_environment = (PROFILE / "journal-supervisor-bridge-environment.sh").read_text()
    reconcile = (PROFILE / "journal-supervisor-reconcile").read_text()

    environment_script = ". /opt/journal-supervisor/bin/journal-supervisor-environment"
    assert environment_script in entrypoint
    assert environment_script in reconcile
    assert '/opt/journal-supervisor/bin/journal-supervisor-bridge proxy &' in entrypoint
    assert '/opt/journal-supervisor/bin/journal-supervisor-bridge wait-for-proxy' in entrypoint
    assert 'node dist/index.js gateway run --port "${OPENCLAW_GATEWAY_PORT:-18789}" &' in entrypoint
    assert entrypoint.index(environment_script) < entrypoint.index("journal-supervisor-bridge proxy &")
    assert entrypoint.index("journal-supervisor-bridge proxy &") < entrypoint.index("journal-supervisor-bridge wait-for-proxy")
    assert entrypoint.index("journal-supervisor-bridge wait-for-proxy") < entrypoint.index("node dist/index.js gateway run")
    assert "trap stop_children EXIT" in entrypoint
    assert "exec /opt/journal-supervisor/bin/journal-supervisor-bridge reconcile" in reconcile
    assert "ANTHROPIC_API_KEY=$(cat /run/secrets/supervisor_anthropic_api_key)" in environment
    assert "OPENCLAW_HOOK_TOKEN=$(cat /run/secrets/openclaw_hook_token)" in environment
    assert "JOURNAL_SUPERVISOR_ADMISSION_TOKEN=$(cat /run/secrets/journal_supervisor_credential)" in bridge_environment
    assert "JOURNAL_SUPERVISOR_STATE_DIR=/home/node/.openclaw/journal-supervisor-transport" in bridge_environment
    assert "OPENCLAW_CONFIG_PATH=/home/node/.openclaw/openclaw.json" in environment
    assert "export ANTHROPIC_API_KEY OPENCLAW_HOOK_TOKEN OPENCLAW_GATEWAY_TOKEN OPENCLAW_CONFIG_PATH" in environment
    assert ". /opt/journal-supervisor/bin/journal-supervisor-bridge-environment" in environment
    assert "export JOURNAL_SUPERVISOR_ADMISSION_URL JOURNAL_SUPERVISOR_ADMISSION_TOKEN JOURNAL_SUPERVISOR_TLS_CA_FILE JOURNAL_SUPERVISOR_STATE_DIR JOURNAL_SUPERVISOR_HINTS_DIRECTORY" in bridge_environment
    assert "--env" not in reconcile
    assert "JOURNAL_SUPERVISOR_STATE_DIR=" not in entrypoint and "JOURNAL_SUPERVISOR_STATE_DIR=" not in reconcile


def test_mcp_server_uses_the_proxy_started_by_the_gateway_entrypoint():
    main = (ROOT / "src" / "supervisor_bridge" / "__main__.py").read_text()
    mcp = main.split('if command == ["mcp"]:', 1)[1].split('if command == ["reconcile"]:', 1)[0]

    assert 'if command == ["proxy"]:' in main
    assert 'MeteringProxyServer(proxy).serve()' in main
    assert 'if command == ["wait-for-proxy"]:' in main
    assert 'MeteredAggregateBudgetProof.proxy_is_healthy()' in main
    assert 'McpServer(bridge).serve()' in mcp
    assert 'MeteringProxy(' not in mcp and 'MeteringProxyServer(' not in mcp


def test_secret_runner_timeout_is_a_project_setting_and_runbook_names_the_smoke_limit():
    option = (ROOT / "src" / "journal" / "features" / "secrets" / "secrets_options.py").read_text()
    feature = (ROOT / "src" / "journal" / "features" / "secrets" / "feature.py").read_text()
    secret_run = (ROOT / "src" / "journal" / "features" / "secrets" / "support" / "secret_run.py").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()

    assert 'Option("secrets.longest_run_seconds"' in option
    assert "120, unit=\"seconds\", setter=USER" in option
    assert "options = (SecretsOptions.LONGEST_RUN_SECONDS,)" in feature
    assert "Settings.applied(self.setting_rows, [SecretsOptions.LONGEST_RUN_SECONDS])" in secret_run
    assert "settings.integer(SecretsOptions.LONGEST_RUN_SECONDS)" in secret_run
    assert "secrets.longest_run_seconds` setting to 360 or more" in runbook


def test_smoke_launcher_full_run_fits_the_documented_secret_runner_setting():
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()
    ready = int(re.search(r"^#define CODEX_READY_TIMEOUT_SECONDS (\d+)$", launcher, re.MULTILINE).group(1))
    smoke = int(re.search(r"^#define SMOKE_RUN_SECONDS (\d+)$", launcher, re.MULTILINE).group(1))
    stop = int(re.search(r"^#define STOP_SECONDS (\d+)$", launcher, re.MULTILINE).group(1))

    assert ready + smoke + stop + 5 < 360


def test_gateway_fixture_is_inert_and_has_a_closed_model_and_tool_route():
    fixture = read_json(PROFILE / "gateway-policy.fixture.json")
    contract_fixture = read_json(PROFILE / "fixtures.json")
    compose = read_json(PROFILE / "compose.json")

    assert fixture["is_openclaw_config"] is False
    assert compose["services"]["gateway"]["image"] == fixture["runtime"]["image"]
    assert fixture["runtime"]["base_image"] == "ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5"
    assert fixture["runtime"]["version"] == "v2026.10.8"
    assert contract_fixture["openclaw_pin"]["version"] == fixture["runtime"]["version"].removeprefix("v")
    assert contract_fixture["openclaw_pin"]["commit"] == fixture["runtime"]["source_commit"]
    assert contract_fixture["openclaw_config"]["gateway"] == {
        "mode": "local", "bind": "lan", "auth": {"mode": "token"}
    }
    assert contract_fixture["openclaw_config"]["plugins"]["allow"] == ["anthropic"]
    assert contract_fixture["openclaw_config"]["plugins"]["deny"] == ["memory-core"]
    assert contract_fixture["openclaw_config"]["plugins"]["entries"]["memory-core"] == {
        "enabled": False,
        "config": {"dreaming": {"enabled": False}},
    }
    assert list(contract_fixture["openclaw_config"]["mcp"]["servers"]) == ["journal"]
    assert contract_fixture["openclaw_config"]["mcp"]["servers"]["journal"]["enabled"] is False
    assert contract_fixture["openclaw_config"]["mcp"]["servers"]["journal"]["command"] == (
        "/opt/journal-supervisor/bin/journal-supervisor-mcp"
    )
    assert contract_fixture["openclaw_config"]["mcp"]["servers"]["journal"]["args"] == []
    assert "OPENCLAW_GATEWAY_TOKEN" not in json.dumps(contract_fixture)
    assert fixture["agent"]["model"] == "anthropic/claude-sonnet-5"
    assert fixture["agent"]["thinking_default"] == "high"
    assert fixture["provider"] == {
        "base_url": "http://127.0.0.1:17840",
        "api": "anthropic-messages",
        "auth": "api-key",
        "api_key_placeholder": "journal-supervisor-metered-proxy-placeholder",
        "proxy_credential_file": "/run/secrets/supervisor_anthropic_api_key",
    }
    assert "auth" not in contract_fixture["openclaw_config"]
    openclaw_config = json.dumps(contract_fixture["openclaw_config"])
    assert contract_fixture["openclaw_config"]["models"]["providers"]["anthropic"]["apiKey"] == (
        "journal-supervisor-metered-proxy-placeholder"
    )
    assert "/run/secrets/supervisor_anthropic_api_key" not in openclaw_config
    contract = (PROFILE / "contract.md").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()
    assert "OpenClaw sends the non-secret placeholder to the loopback proxy" in contract
    assert "its `apiKey` is exactly `journal-supervisor-metered-proxy-placeholder`" in runbook
    assert "The real provider key belongs only in the mounted proxy secret" in runbook
    assert "journal-supervisor-mcp" in contract and "args: []" in contract
    assert "journal-supervisor-mcp" in runbook and "args` is empty" in runbook
    assert fixture["agent"]["fallbacks"] == []
    assert fixture["hooks"]["enabled"] is False
    assert fixture["network"] == {"bind": "lan", "port": 18789, "host_published": False}
    assert fixture["reconciliation_job"]["enabled"] is False
    assert contract_fixture["cron_add_params"]["enabled"] is False
    assert fixture["enrollment"]["enabled"] is False
    assert fixture["tools"]["wildcards"] is False
    assert fixture["tools"]["allowlist"] == list(OPENCLAW_TOOL_NAMES)
    assert contract_fixture["openclaw_config"]["tools"]["toolSearch"] is False
    assert fixture["secret_values_in_fixture"] is False
    mapping = contract_fixture["openclaw_config"]["hooks"]["mappings"]
    assert len(mapping) == 1
    assert mapping[0]["match"] == {"path": "journal-supervisor"}
    assert mapping[0]["action"] == "agent" and mapping[0]["sessionMode"] == "isolated"
    assert mapping[0]["agentId"] == "supervisor"
    assert mapping[0]["deliver"] is False
    assert mapping[0]["allowUnsafeExternalContent"] is True
    assert "{{run_ref}}" in mapping[0]["messageTemplate"]
    assert "journal_supervisor.observe" in mapping[0]["messageTemplate"]
    assert "journal_supervisor.receipt" in mapping[0]["messageTemplate"]

    entrypoint = (PROFILE / "gateway-entrypoint.sh").read_text()
    assert ". /opt/journal-supervisor/bin/journal-supervisor-environment" in entrypoint
    assert "JOURNAL_SUPERVISOR_CREDENTIAL" not in entrypoint
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()
    assert '"writer_supervisor_tls_cert"' in launcher
    assert '"writer_supervisor_tls_key"' in launcher
    assert '"writer_supervisor_tls_ca"' in launcher
    assert r'\"defaults\":{\"model\":{\"primary\":\"anthropic/claude-sonnet-5\"}' in launcher
    assert r'\"tools\":{\"toolSearch\":false,\"allow\":[' in launcher
    assert r'\"apiKey\":\"journal-supervisor-metered-proxy-placeholder\"' in launcher
    assert r'!strstr(compact, "\"profiles\":")' in launcher
    assert r'!strstr(compact, "\"order\":")' in launcher
    assert r'\"gateway\":{\"mode\":\"local\",\"bind\":\"lan\",\"auth\":{\"mode\":\"token\"}}' in launcher
    assert r'\"plugins\":{\"enabled\":true,\"allow\":[\"anthropic\"],\"deny\":[\"memory-core\"]' in launcher
    assert r'\"dreaming\":{\"enabled\":false}' in launcher
    assert '!strstr(compact, "\\\"default\\\":")' in launcher


def test_gateway_admission_url_targets_the_private_writer_network():
    compose = read_json(PROFILE / "compose.json")
    gateway = compose["services"]["gateway"]
    writer = compose["services"]["writer"]
    bridge_environment = (PROFILE / "journal-supervisor-bridge-environment.sh").read_text()

    assert "JOURNAL_SUPERVISOR_ADMISSION_URL" not in gateway["environment"]
    assert "JOURNAL_SUPERVISOR_TLS_CA_FILE" not in gateway["environment"]
    assert "JOURNAL_SUPERVISOR_ADMISSION_URL=https://writer:8422" in bridge_environment
    assert "JOURNAL_SUPERVISOR_TLS_CA_FILE=/run/secrets/writer_supervisor_tls_ca" in bridge_environment
    assert writer["expose"] == ["8422"]
    assert "gateway_link" in gateway["networks"] and "gateway_link" in writer["networks"]
    assert "journal_management" not in gateway["networks"]


def test_gateway_listener_is_tls_and_policy_fixture_denies_owner_ports():
    compose = read_json(PROFILE / "compose.json")
    manifest = read_json(PROFILE / "manifest.json")
    firewall = read_json(PROFILE / "firewall-policy.fixture.json")
    writer = compose["services"]["writer"]
    gateway = compose["services"]["gateway"]
    gateway_rules = [
        rule for rule in firewall["rules"]
        if rule["source"] == "10.76.20.20 (Gateway)" and rule["destination"] == "10.76.20.10 (writer)"
    ]
    management_rules = [
        rule for rule in firewall["rules"]
        if rule["source"] == "10.76.20.20 (Gateway)" and rule["destination"] == "10.76.10.10 (writer management)"
    ]

    assert writer["environment"]["JOURNAL_HOST"] == "127.0.0.1"
    assert writer["environment"]["JOURNAL_OWNER_ACCESS_HOST"] == "10.76.10.10"
    assert writer["environment"]["JOURNAL_SUPERVISOR_HOST"] == "10.76.20.10"
    assert writer["networks"]["gateway_link"]["ipv4_address"] == "10.76.20.10"
    assert gateway["networks"]["gateway_link"]["ipv4_address"] == "10.76.20.20"
    assert writer["ports"] == ["127.0.0.1:18440:8423"]
    assert next(iter(writer["networks"])) == "journal_management"
    assert {
        (tuple(rule["ports"]), rule["action"]) for rule in gateway_rules
    } >= {
        ((8422,), "allow"),
        ((8421,), "deny"),
    }
    assert any(rule["ports"] == [8423] and rule["action"] == "deny" for rule in management_rules)
    assert manifest["topology"][0]["supervisor_api"].endswith("token-checked supervisor service routes")
    handler = (ROOT / "src" / "journal" / "http" / "supervisor_handler.py").read_text()
    assert "SERVICE_PATHS" in handler
    assert "urlsplit(self.path).path not in SERVICE_PATHS" in handler
    assert "Response(403" in handler
    assert "super().do_POST()" in handler
    assert "token-checked supervisor routes only" in handler
    authentication = (ROOT / "src" / "journal" / "http" / "support" / "supervisor_authentication.py").read_text()
    assert "if path in SERVICE_PATHS" in authentication
    assert "self.authority.authenticate(token)" in authentication
    assert "TLS_CA_FILE" in (PROFILE / "journal-supervisor-bridge-environment.sh").read_text()
    transport = (ROOT / "src" / "supervisor_bridge" / "transport.py").read_text()
    client = (ROOT / "src" / "supervisor_bridge" / "__main__.py").read_text()
    assert "HTTPSHandler(context=ssl.create_default_context(cafile=ca_file))" in transport
    assert "JsonHttpConnection(url, token, ca_file=ca_file)" in client
    server = (ROOT / "src" / "journal" / "http" / "server.py").read_text()
    config = (ROOT / "src" / "journal" / "config.py").read_text()
    assert "SSLContext(ssl.PROTOCOL_TLS_SERVER)" in server and "load_cert_chain" in server
    assert "JOURNAL_OWNER_ACCESS_HOST" in config and "JOURNAL_SUPERVISOR_TLS_CERT_FILE" in config


def test_plugin_is_uninstalled_guarded_and_uses_plugin_health_contract():
    manifest = read_json(ROOT / "plugins" / "supervisor_v1" / "journal-plugin.json")
    service = manifest["services"][0]

    assert manifest["name"] == "supervisor-v1"
    assert service["name"] == "bridge"
    assert service["when"] == 'test -f "$JOURNAL_PLUGIN_DATA/STAGING_AUTHORIZED"'
    assert service["restart"] == "always"
    assert service["answers"] is True
    assert manifest["health"]["socket_env"] == "SUPERVISOR_HEALTH_SOCKET"
    assert manifest["health"]["answer"] == '{"health":"up","service":"<name>"}'
    assert set(manifest["hears"]) >= {
        "check_failed", "task_test_failed", "worker_silent", "messages.created", "question_posed",
    }
    assert not (ROOT / ".journal" / "plugins" / "supervisor-v1").exists()


def test_event_bridge_spools_only_allowed_row_references(tmp_path: Path):
    row_event = {
        "event": "checks.updated",
        "at": "2026-10-29T10:00:00+00:00",
        "environment": "pilot",
        "data": {"table": "checks", "id": "check-1", "changed": {"result": "private text"}},
    }

    hint = bridge_service.hint_from(json.dumps(row_event))
    path = bridge_service.write_hint(tmp_path, hint)
    saved = json.loads(path.read_text())

    assert saved == {"at": row_event["at"], "environment": "pilot", "event": "checks.updated", "id": "check-1", "table": "checks", "v": "1"}
    assert "private text" not in path.read_text()
    assert bridge_service.hint_from(json.dumps({**row_event, "event": "messages.created"})) is None
    hint_with_extra_field = bridge_service.hint_from(
        json.dumps({**row_event, "data": {"table": "checks", "id": "check-2", "body": "private text"}})
    )
    assert hint_with_extra_field is not None
    assert set(hint_with_extra_field) == {"v", "event", "at", "environment", "table", "id"}
    assert "body" not in hint_with_extra_field


def test_event_bridge_classifies_supervisor_wakes_without_storing_event_contents():
    examples = (
        ("check_failed", {"check_id": 4}, "checks", "failed_check", 4),
        ("task_test_failed", {"task_id": 5, "output_id": 8, "outcome": "private"}, "tasks", "stalled_task", 5),
        ("worker_silent", {"worker": {"id": 6, "name": "private"}, "minutes": 10}, "workers", "stale_worker", 6),
        ("messages.created", {"table": "messages", "id": 7, "by": "user"}, "messages", "message_to_supervisor", 7),
        ("question_posed", {"question_id": 9}, "questions", "question_to_supervisor", 9),
    )

    for event_name, data, table, event_kind, row_id in examples:
        event = {"event": event_name, "at": "2026-10-29T10:00:00+00:00", "environment": "pilot", "data": data}
        hint = bridge_service.hint_from(json.dumps(event))

        assert hint["table"] == table
        assert hint["id"] == str(row_id)
        assert hint["event_kind"] == event_kind
        assert "private" not in json.dumps(hint)


def test_gateway_starts_the_read_only_event_hint_watcher():
    entrypoint = (PROFILE / "gateway-entrypoint.sh").read_text()
    bridge_environment = (PROFILE / "journal-supervisor-bridge-environment.sh").read_text()

    assert "/opt/journal-supervisor/bin/journal-supervisor-bridge watch-events" in entrypoint
    assert "JOURNAL_SUPERVISOR_HINTS_DIRECTORY=/var/lib/journal-supervisor/hints" in bridge_environment


def test_admission_contract_carries_an_optional_event_identity():
    schema = read_json(PROFILE / "contract.schema.json")["$defs"]["AdmissionRequest"]

    assert schema["properties"]["event_kind"]["enum"] == [
        "failed_check", "stalled_task", "stale_worker", "message_to_supervisor", "question_to_supervisor",
    ]
    assert schema["properties"]["event_id"]["maxLength"] == 128
    assert schema["dependentRequired"] == {"event_kind": ["event_id"], "event_id": ["event_kind"]}


def test_event_spool_drops_hints_at_its_bound(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(bridge_service, "MAX_HINTS", 1)
    first = {"v": "1", "event": "tasks.created", "at": "t1", "environment": "pilot", "table": "tasks", "id": "task-1"}
    second = {**first, "id": "task-2"}

    assert bridge_service.write_hint(tmp_path, first) is not None
    assert bridge_service.write_hint(tmp_path, second) is None
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_runbook_declares_recovery_targets_and_live_staging_probes():
    manifest = read_json(PROFILE / "manifest.json")
    runbook = (PROFILE / "RUNBOOK.md").read_text()
    backup = read_json(PROFILE / "compose.json")["services"]["backup"]

    assert manifest["backup"]["rpo"] == "1 hour"
    assert manifest["backup"]["rto"] == "4 hours"
    assert manifest["backup"]["snapshot_interval_seconds"] == 900
    assert backup["environment"]["BACKUP_EVERY"] == "900"
    assert backup["cap_add"] == ["DAC_READ_SEARCH"]
    assert "writer_state:/data:ro" in backup["volumes"]
    assert "gateway_state:/gateway:ro" in backup["volumes"]
    assert "B10 disposable-staging acceptance" in runbook
    assert "restore_candidate" in runbook
    assert "Keep writes disabled" in runbook
    assert "every 15 minutes" in runbook
    assert "-e BACKUP_ONCE=1 backup" in runbook
    assert "-e RESTORE_SNAPSHOT=SNAPSHOT_ID" in runbook
    assert "developer laptop" in runbook
    assert "deliberately failing `false` smoke check" in runbook
    assert "one current failure episode to diagnose" in runbook
    assert "The real Plan agent starts with no work in hand" in runbook
    assert "reserves it for supervisor diagnosis before plan start" in runbook
    assert "up to 300 seconds" in runbook
    assert "refuses an explicit start or worker assignment" in runbook
    assert "exactly one open, unheld diagnostic task" in runbook
    assert "runs the bound, deliberately failing `false` smoke check exactly once after enrollment" in runbook
    assert "first writer reconciliation admit one turn" in runbook
    assert "Cold-reboot the disposable VM" in runbook
    assert "No OpenRig fleet or build worker launcher" in runbook
    assert "build-gateway.sh" in runbook
    assert "PROFILE_REVISION" in runbook
    staging_report = (PROFILE / "STAGING-REPORT.md").read_text()
    assert "build-gateway.sh" in staging_report
    assert "this worker did not run Docker or build the image" in staging_report
    assert "one open, unheld diagnostic task" in staging_report
    assert "first Gateway reconciliation" in staging_report
    assert "kill switch" in runbook
