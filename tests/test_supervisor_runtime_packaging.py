"""Static and pure-function checks for the inert supervisor v1 deployment package."""

import json
import stat
from pathlib import Path

from plugins.supervisor_v1 import bridge_service


ROOT = Path(__file__).parents[1]
PROFILE = ROOT / "docs" / "supervisor" / "v1"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


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
    assert compose["services"]["writer"]["restart"] == "unless-stopped"
    assert compose["services"]["gateway"]["restart"] == "unless-stopped"
    assert compose["services"]["writer"]["healthcheck"]["test"] == ["CMD-SHELL", "curl -fsS http://127.0.0.1:8440/ready"]
    assert compose["services"]["gateway"]["healthcheck"]["test"] == [
        "CMD",
        "node",
        "-e",
        "fetch('http://127.0.0.1:18789/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))",
    ]
    assert compose["services"]["writer"]["ports"] == ["127.0.0.1:18440:8440"]
    assert compose["services"]["writer"]["expose"] == ["8421"]
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
        "url": "https://writer:8421",
        "network": "gateway_link",
        "token_secret": "journal_supervisor_credential",
        "token_environment": "JOURNAL_SUPERVISOR_ADMISSION_TOKEN",
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

    assert gateway_secrets == {"supervisor_anthropic_api_key", "openclaw_hook_token", "journal_supervisor_credential"}
    assert writer_secrets == {"codex_driver_credentials"}
    assert backup_secrets == {"restic_password", "restic_repository", "backup_object_store_credentials"}
    assert set(secrets) == gateway_secrets | writer_secrets | backup_secrets
    manifest_secrets = {secret["name"]: secret for secret in read_json(PROFILE / "manifest.json")["secrets"]}
    assert {manifest_secrets[name]["host_owner"] for name in gateway_secrets} == {"root:1000"}
    assert {manifest_secrets[name]["host_owner"] for name in backup_secrets} == {"root:10005"}
    assert {manifest_secrets[name]["host_mode"] for name in gateway_secrets | backup_secrets} == {"0440"}
    driver = manifest_secrets["codex_driver_credentials"]
    assert driver["host_owner"] == "10001:10001" and driver["host_mode"] == "0400"
    assert driver["mounted_to"] == "journal-writer:/run/secrets/codex_driver_credentials only"
    assert "shared uid10001" in driver["status"]


def test_network_policy_is_default_deny_and_refuses_unisolated_workers():
    manifest = read_json(PROFILE / "manifest.json")
    firewall = read_json(PROFILE / "firewall-policy.fixture.json")
    execution = manifest["execution_identity_contract"]
    worker = manifest["worker_identity_contract"]

    assert manifest["network_policy_fixture"] == "firewall-policy.fixture.json"
    assert firewall["is_applied_firewall_config"] is False
    assert set(firewall["default_policy"].values()) == {"deny", True}
    assert any(rule["ports"] == [8421] and rule["action"] == "allow" for rule in firewall["rules"])
    assert any(rule["ports"] == [8440, 5432, 3306, 6379] and rule["action"] == "deny" for rule in firewall["rules"])
    assert any(rule["destination"] == "api.anthropic.com" and rule["ports"] == [443] for rule in firewall["rules"])
    assert any(rule["destination"] == "api.openai.com" and rule["ports"] == [443] for rule in firewall["rules"])
    assert any("refuse enrollment" in rule["action"] for rule in firewall["rules"])
    assert manifest["launch_gates"]["active_worker_restricted_profile_verified_or_enrollment_refused"] is False
    assert manifest["launch"]["enrollment_enabled"] is False
    assert execution["uid"] == 10003 and execution["gid"] == 10003
    assert execution["root_filesystem"] == "read-only"
    assert execution["capabilities"] == [] and execution["no_new_privileges"] is True
    assert execution["status"] == "contract only; current AgentLauncher does not enforce it"
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
    assert "docs/supervisor/v1/live-smoke-setup.py" in script
    assert 'tar -xf "$BUILD_CONTEXT/runtime.tar"' in script
    assert '"$BUILD_CONTEXT"' in script


def test_codex_plan_driver_is_pinned_file_backed_and_uses_the_owner_plan_lifecycle():
    compose = read_json(PROFILE / "compose.json")
    manifest = read_json(PROFILE / "manifest.json")
    writer = compose["services"]["writer"]
    gateway = compose["services"]["gateway"]
    backup = compose["services"]["backup"]
    dockerfile = (ROOT / "docker" / "Dockerfile").read_text()
    entrypoint = (ROOT / "docker" / "entrypoint.sh").read_text()
    setup = (PROFILE / "live-smoke-setup.py").read_text()
    host_setup = (PROFILE / "setup-live-smoke.sh").read_text()
    assert (PROFILE / "setup-live-smoke.sh").stat().st_mode & stat.S_IXUSR

    assert "npm install -g @openai/codex@0.165.0" in dockerfile
    assert "CODEX_HOME" not in dockerfile and "CODEX_API_KEY" not in dockerfile
    assert writer["environment"]["CODEX_HOME"] == "/run/codex"
    assert writer["tmpfs"] == ["/tmp", "/run:mode=1777"]
    assert {secret["source"] for secret in writer["secrets"]} == {"codex_driver_credentials"}
    assert {secret["source"] for secret in gateway["secrets"]}.isdisjoint({"codex_driver_credentials"})
    assert {secret["source"] for secret in backup["secrets"]}.isdisjoint({"codex_driver_credentials"})
    assert compose["secrets"]["codex_driver_credentials"]["file"].endswith("/codex_driver_credentials")
    assert "codex login --with-api-key < /run/secrets/codex_driver_credentials" in entrypoint
    assert ">/dev/null 2>&1" in entrypoint
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
    manifest_secrets = {secret["name"]: secret for secret in manifest["secrets"]}
    assert "shared uid10001" in manifest_secrets["codex_driver_credentials"]["status"]


def test_codex_secret_stager_is_fixed_owner_only_and_built_from_the_reviewed_source():
    stage = (ROOT / "src" / "supervisor_bridge" / "codex_driver_secret_stage.c").read_text()
    build = (ROOT / "src" / "supervisor_bridge" / "build-driver-secret-stage.sh").read_text()
    launcher = (ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c").read_text()
    runbook = (PROFILE / "RUNBOOK.md").read_text()
    report = (PROFILE / "STAGING-REPORT.md").read_text()

    assert "argc != 1" in stage
    assert "TENANT_SECRET_SOURCE_DIR" in stage and "codex_driver_credentials" in stage
    assert "O_CREAT | O_EXCL | O_NOFOLLOW, 0400" in stage
    assert "fchmod(file, 0400)" in stage and '"sk-"' in stage and '"sk-ant-"' in stage
    assert "puts(key" not in stage and "printf(key" not in stage
    assert "RUNTIME_SOURCE HEAD must equal PROFILE_REVISION" in build
    assert "git -C \"$RUNTIME_SOURCE\" archive --format=tar \"$PROFILE_REVISION\"" in build
    assert "/usr/local/bin/journal-supervisor-driver-secret-stage" in build
    assert "journal secret run 2 -- journal-supervisor-driver-secret-stage" in runbook
    assert "revoke the provisional grant" in runbook
    assert '"codex_driver_credentials"' in launcher
    assert "copy_driver_secret(source, directory)" in launcher
    assert "journal-supervisor-driver-secret-stage" in runbook
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
    assert "JOURNAL_SUPERVISOR_CREDENTIAL" not in entrypoint


def test_gateway_admission_url_targets_the_private_writer_network():
    compose = read_json(PROFILE / "compose.json")
    gateway = compose["services"]["gateway"]
    writer = compose["services"]["writer"]

    assert gateway["environment"]["JOURNAL_SUPERVISOR_ADMISSION_URL"] == "https://writer:8421"
    assert writer["expose"] == ["8421"]
    assert "gateway_link" in gateway["networks"] and "gateway_link" in writer["networks"]
    assert "journal_management" not in gateway["networks"]


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
