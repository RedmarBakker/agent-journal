"""Static and pure-function checks for the inert supervisor v1 deployment package."""

import ast
import json
import stat
from pathlib import Path

from plugins.supervisor_v1 import bridge_service


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
    )
    copies = (
        "COPY --chown=root:root src /opt/agent-journal/src",
        "COPY --chown=root:root install.sh update_steps.json /opt/agent-journal/",
        "COPY --chown=root:root --chmod=755 docker/entrypoint.sh docker/hosted-journal /usr/local/bin/",
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-login docker/supervisor-codex-ready /usr/local/bin/",
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-plan-launcher.py /usr/local/bin/supervisor-codex-plan-launcher",
        "COPY --chown=root:root --chmod=755 docs/supervisor/v1/live-smoke-setup.py /usr/local/bin/supervisor-live-setup",
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
    assert 'CHECK_COMMAND = "curl -fsS http://127.0.0.1:8421/journal/health"' in setup

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
    assert '"max_input_tokens_per_turn": 24000' in setup
    assert '"max_output_tokens_per_turn": 8000' in setup
    assert '"max_provider_requests_per_turn": 8' in setup
    assert '"max_turns_per_day": 1' in setup
    assert '"max_cost_microusd_per_day": 1000000' in setup
    assert "active_workers = workers.global_matching(state=WorkerState.DISPATCHED)" in setup and "if active_workers:" in setup
    assert '"mode": "bounded_write"' in setup
    assert '"/run/journal_supervisor_credential"' in setup
    assert "except (OSError, SetupFailure) as error:" in setup and "revoke(grant_id)" in setup
    assert "STAGING_AUTHORIZED" in host_setup and "compose cp writer:/run/journal_supervisor_credential" in host_setup
    assert "normal_driver_separate_execution_identity" in manifest["launch_gates"]
    assert manifest["launch"]["enrollment_enabled"] is False
    assert "private device-auth login" in setup
    assert manifest["topology"][0]["codex_driver"]["permissions"].startswith("the Dockerfile pre-creates /var/lib/journal-codex as uid/gid 10003 mode 0700")
    assert manifest["volumes"]["codex_driver_state"]["owner"] == "10003:10003"
    assert manifest["execution_identity_contract"]["status"].startswith("packaged; dedicated-VM B10")
    assert manifest["launch_gates"]["normal_driver_separate_execution_identity"] is False
    assert "uid/gid 10003" in runbook and "B10 remains false" in runbook


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

    assert "RUNTIME_SOURCE HEAD must equal PROFILE_REVISION" in script
    assert "status --porcelain --untracked-files=all" in script
    assert 'git -C "$RUNTIME_SOURCE" archive --format=tar "$PROFILE_REVISION"' in script
    assert "src/supervisor_bridge" in script
    assert "docs/supervisor/v1/Dockerfile.gateway" in script
    assert "docs/supervisor/v1/journal-supervisor-bridge" in script
    assert 'tar -xf "$BUILD_CONTEXT/runtime.tar"' in script
    assert '--tag "agent-journal-supervisor-gateway:$PROFILE_REVISION"' in script
    assert "--pull" in script
    assert "FROM ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5" in dockerfile
    assert "apt-get install -y --no-install-recommends python3" in dockerfile
    assert "COPY src/supervisor_bridge /opt/journal-supervisor/lib/supervisor_bridge" in dockerfile
    assert "COPY docs/supervisor/v1/journal-supervisor-bridge /opt/journal-supervisor/bin/journal-supervisor-bridge" in dockerfile
    assert "ENV PYTHONPATH=/opt/journal-supervisor/lib" in dockerfile
    assert "USER 1000:1000" in dockerfile
    assert 'exec python3 -m supervisor_bridge "$@"' in wrapper


def test_gateway_fixture_is_inert_and_has_a_closed_model_and_tool_route():
    fixture = read_json(PROFILE / "gateway-policy.fixture.json")
    compose = read_json(PROFILE / "compose.json")

    assert fixture["is_openclaw_config"] is False
    assert compose["services"]["gateway"]["image"] == fixture["runtime"]["image"]
    assert fixture["runtime"]["base_image"] == "ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5"
    assert fixture["runtime"]["version"] == "v2026.10.8"
    assert fixture["agent"]["model"] == "anthropic/claude-sonnet-5"
    assert fixture["agent"]["thinking_default"] == "high"
    assert fixture["provider"] == {
        "base_url": "http://127.0.0.1:17840",
        "api": "anthropic-messages",
        "auth": "api-key",
        "profile": "anthropic:supervisor-api",
        "credential_file": "/run/secrets/supervisor_anthropic_api_key",
    }
    assert fixture["agent"]["fallbacks"] == []
    assert fixture["hooks"]["enabled"] is False
    assert fixture["network"] == {"bind": "lan", "port": 18789, "host_published": False}
    assert fixture["reconciliation_job"]["enabled"] is False
    assert fixture["enrollment"]["enabled"] is False
    assert fixture["tools"]["wildcards"] is False
    assert len(fixture["tools"]["allowlist"]) == 3
    assert fixture["secret_values_in_fixture"] is False

    entrypoint = (PROFILE / "gateway-entrypoint.sh").read_text()
    assert "cat /run/secrets/supervisor_anthropic_api_key" in entrypoint
    assert "cat /run/secrets/openclaw_hook_token" in entrypoint
    assert "JOURNAL_SUPERVISOR_ADMISSION_TOKEN=$(cat /run/secrets/journal_supervisor_credential)" in entrypoint
    assert "JOURNAL_SUPERVISOR_ADMISSION_URL" in entrypoint
    assert "JOURNAL_SUPERVISOR_ADMISSION_TOKEN" in entrypoint
    assert "JOURNAL_SUPERVISOR_TLS_CA_FILE" in entrypoint
    assert "JOURNAL_SUPERVISOR_CREDENTIAL" not in entrypoint
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()
    assert '"writer_supervisor_tls_cert"' in launcher
    assert '"writer_supervisor_tls_key"' in launcher
    assert '"writer_supervisor_tls_ca"' in launcher


def test_gateway_admission_url_targets_the_private_writer_network():
    compose = read_json(PROFILE / "compose.json")
    gateway = compose["services"]["gateway"]
    writer = compose["services"]["writer"]

    assert gateway["environment"]["JOURNAL_SUPERVISOR_ADMISSION_URL"] == "https://writer:8422"
    assert gateway["environment"]["JOURNAL_SUPERVISOR_TLS_CA_FILE"] == "/run/secrets/writer_supervisor_tls_ca"
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
    assert "TLS_CA_FILE" in (PROFILE / "gateway-entrypoint.sh").read_text()
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
    assert "Cold-reboot the disposable VM" in runbook
    assert "No OpenRig fleet or build worker launcher" in runbook
    assert "build-gateway.sh" in runbook
    assert "PROFILE_REVISION" in runbook
    staging_report = (PROFILE / "STAGING-REPORT.md").read_text()
    assert "build-gateway.sh" in staging_report
    assert "this worker did not run Docker or build the image" in staging_report
    assert "kill switch" in runbook
