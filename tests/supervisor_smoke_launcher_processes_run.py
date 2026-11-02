# Starts real programs, so it is not in the default run: journal suite tests/supervisor_smoke_launcher_processes_run.py -q.
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import pytest


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c"
COMPOSE = "docs/supervisor/v1/compose.json"
ENV_FILE = "docs/supervisor/v1/live-smoke.env"
SECRET_FILES = (
    "openclaw_hook_token",
    "journal_supervisor_credential",
    "restic_password",
    "restic_repository",
    "backup_object_store_credentials",
)
EXTERNAL_SECRET_FILES = (
    "writer_supervisor_tls_cert",
    "writer_supervisor_tls_key",
    "writer_supervisor_tls_ca",
)


@pytest.fixture
def compiled_launcher(tmp_path):
    compiler = shutil.which("cc")
    assert compiler, "a C compiler is required to build the native launcher"
    executable = tmp_path / "journal-supervisor-smoke"
    docker_stub = tmp_path / "docker"
    stub_source = tmp_path / "docker_stub.c"
    stub_source.write_text(
        r'''#define _XOPEN_SOURCE 700
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char **argv) {
    char path[4096];
    const char *home = getenv("HOME");
    const char *secret_dir = getenv("TENANT_SECRET_DIR");
    if (!home || !secret_dir) return 10;
    snprintf(path, sizeof(path), "%s/docker-calls", home);
    FILE *calls = fopen(path, "a");
    if (!calls) return 11;
    for (int index = 1; index < argc; index++) fprintf(calls, "%s%s", index == 1 ? "" : " ", argv[index]);
    fputc('\n', calls);
    fclose(calls);
    snprintf(path, sizeof(path), "%s/secret-path", home);
    FILE *secret_path = fopen(path, "w");
    if (!secret_path) return 15;
    fputs(secret_dir, secret_path);
    fclose(secret_path);
    int is_up = 0, is_ready = 0, is_gateway_health = 0, is_reconcile = 0;
    for (int index = 1; index < argc; index++) {
        if (strcmp(argv[index], "up") == 0) is_up = 1;
        if (strcmp(argv[index], "/usr/local/bin/supervisor-codex-ready") == 0) is_ready = 1;
        if (strstr(argv[index], "healthz")) is_gateway_health = 1;
        if (strcmp(argv[index], "/opt/journal-supervisor/bin/journal-supervisor-bridge") == 0 && index + 1 < argc && strcmp(argv[index + 1], "reconcile") == 0) is_reconcile = 1;
    }
    if (is_ready) {
        snprintf(path, sizeof(path), "%s/codex-login-missing", home);
        if (access(path, F_OK) == 0) return 21;
        return 0;
    }
    if (is_gateway_health) {
        snprintf(path, sizeof(path), "%s/gateway-ready", home);
        if (access(path, F_OK) != 0) return 23;
        snprintf(path, sizeof(path), "%s/gateway-health-passed", home);
        FILE *ready = fopen(path, "w");
        if (!ready) return 24;
        fclose(ready);
        return 0;
    }
    if (is_reconcile) {
        snprintf(path, sizeof(path), "%s/gateway-health-passed", home);
        if (access(path, F_OK) != 0) return 25;
        const char *gateway_state = getenv("GATEWAY_STATE_PATH");
        if (!gateway_state) return 16;
        snprintf(path, sizeof(path), "%s/journal-supervisor-transport", gateway_state);
        if (mkdir(path, 0700) != 0) return 17;
        snprintf(path, sizeof(path), "%s/journal-supervisor-transport/bridge-state.json", gateway_state);
        FILE *state = fopen(path, "w");
        if (!state) return 18;
        fputs("{\"last_admission\":\"verified\",\"usage_settlement\":\"settled\",\"receipt\":{\"status\":\"applied\",\"verification\":\"verified\"},\"metering\":{\"provider_requests\":1}}", state);
        fclose(state);
        return 0;
    }
    if (is_up) {
        snprintf(path, sizeof(path), "%s/supervisor_anthropic_api_key", secret_dir);
        FILE *key_file = fopen(path, "r");
        if (!key_file) return 12;
        char key[4097] = {0};
        if (!fgets(key, sizeof(key), key_file)) return 13;
        fclose(key_file);
        snprintf(path, sizeof(path), "%s/key-seen-by-runtime", home);
        FILE *seen = fopen(path, "w");
        if (!seen) return 14;
        fputs(key, seen);
        fclose(seen);
        snprintf(path, sizeof(path), "%s/slow-up", home);
        if (is_up && access(path, F_OK) == 0) sleep(5);
        snprintf(path, sizeof(path), "%s/gateway-starts-slow", home);
        if (access(path, F_OK) == 0) sleep(1);
        snprintf(path, sizeof(path), "%s/gateway-ready", home);
        FILE *ready = fopen(path, "w");
        if (!ready) return 19;
        fclose(ready);
        for (;;) pause();
    }
    puts("synthetic provider key is not part of this line");
    return 0;
}
'''
    )
    compiled = subprocess.run(
        [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2", "-D_XOPEN_SOURCE=700", "-DSMOKE_RUN_SECONDS=3", str(SOURCE), "-o", str(executable)],
        capture_output=True,
        text=True,
    )
    assert compiled.returncode == 0, compiled.stderr
    subprocess.run(
        [compiler, "-std=c11", "-Wall", "-Wextra", "-O2", str(stub_source), "-o", str(docker_stub)],
        check=True,
        capture_output=True,
        text=True,
    )
    return executable, docker_stub


def staging_root(tmp_path):
    work = tmp_path / "project"
    (work / "docs/supervisor/v1").mkdir(parents=True)
    (work / COMPOSE).write_text(
        '{"services":{"writer":{"environment":{"JOURNAL_HOST": "127.0.0.1",'
        '"JOURNAL_OWNER_ACCESS_HOST": "10.76.10.10","JOURNAL_OWNER_ACCESS_PORT": "8423",'
        '"JOURNAL_SUPERVISOR_HOST": "10.76.20.10","JOURNAL_SUPERVISOR_PORT": "8422",'
        '"JOURNAL_SUPERVISOR_TLS_CERT_FILE": "/run/secrets/writer_supervisor_tls_cert",'
        '"JOURNAL_SUPERVISOR_TLS_KEY_FILE": "/run/secrets/writer_supervisor_tls_key",'
        '"JOURNAL_SUPERVISOR_ADMISSION_URL": "https://writer:8422",'
        '"JOURNAL_SUPERVISOR_TLS_CA_FILE": "/run/secrets/writer_supervisor_tls_ca",'
        '"TENANT_SECRET_SOURCE_DIR": "source", "JOURNAL_CODEX_HOME": "/var/lib/journal-codex",'
        '"JOURNAL_PLAN_DRIVER_SOCKET": "/run/journal-plan-driver.sock"},'
        '"cap_add": ["SETUID", "SETGID", "SETPCAP"],'
        '"ports": ["127.0.0.1:18440:8423"], "expose": ["8422"],'
        '"volumes":["codex_driver_state:/var/lib/journal-codex"]},'
        '"writer_supervisor_tls_cert": "${TENANT_SECRET_SOURCE_DIR:?set the root-owned tenant secret source directory}/writer_supervisor_tls_cert",'
        '"writer_supervisor_tls_key": "${TENANT_SECRET_SOURCE_DIR:?set the root-owned tenant secret source directory}/writer_supervisor_tls_key",'
        '"writer_supervisor_tls_ca": "${TENANT_SECRET_SOURCE_DIR:?set the root-owned tenant secret source directory}/writer_supervisor_tls_ca",'
        "\"gateway\": {\"secrets\":[],\"healthcheck\":{\"test\":[\"CMD\",\"node\",\"-e\",\"fetch('http://127.0.0.1:18789/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))\"]}},"
        '"backup": {"secrets":[]}},'
        '"image":"agent-journal-supervisor-gateway:${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed source commit}",'
        '"volumes":{"codex_driver_state": {}},"secrets":{}}\n'
    )
    (work / "docker").mkdir()
    (work / "docker/Dockerfile").write_text(
        "RUN npm install -g @openai/codex@0.165.0\n"
        "groupadd --gid 10003 codex-driver\n"
        "useradd --uid 10003 --gid codex-driver\n"
        "chown codex-driver:codex-driver /var/lib/journal-codex\n"
        "chmod 700 /data/home /data/secrets /data/gateway /data/vault /var/lib/journal-codex\n"
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-login docker/supervisor-codex-ready /usr/local/bin/\n"
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-plan-launcher.py /usr/local/bin/supervisor-codex-plan-launcher\n"
        "COPY --chown=root:root --chmod=755 docs/supervisor/v1/live-smoke-setup.py /usr/local/bin/supervisor-live-setup\n"
    )
    (work / "docker/entrypoint.sh").write_text(
        "setpriv --reuid 10003 --regid 10003 --clear-groups supervisor-codex-ready\n"
        "/run/journal-plan-driver-server.pid\n"
        "supervisor-codex-plan-launcher\n"
        "if ! supervisor-codex-ready; then\n"
        "echo complete supervisor-codex-login before starting the writer\n"
    )
    (work / "docker/supervisor-codex-login").write_text(
        "supervisor-codex-login accepts no arguments\n"
        "supervisor-codex-login must run as uid/gid 10003\n"
        "Codex driver home must be pre-created as uid/gid 10003 with mode 0700\n"
        "codex login --device-auth\n"
    )
    (work / "docker/supervisor-codex-ready").write_text(
        "supervisor-codex-ready accepts no arguments\n"
        "supervisor-codex-ready must run as uid/gid 10003\n"
        "Codex device login is absent or not private\n"
        "stat -c %u\nstat -c %g\nstat -c %a\n"
    )
    (work / "docs/supervisor/v1/live-smoke-setup.py").write_text(
        "if len(sys.argv) != 1\n/_supervisor/v1/enrollment\nPlanMode.SOLO\nSupervisorLink\n"
        '"max_input_tokens_per_turn": 24000\n"max_output_tokens_per_turn": 8000\n'
        '"max_provider_requests_per_turn": 8\n"mode": "bounded_write"\n'
    )
    (work / "docs/supervisor/v1/Dockerfile.gateway").write_text(
        "FROM ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5\n"
        "RUN apt-get install -y --no-install-recommends python3\n"
        "COPY src/supervisor_bridge /opt/journal-supervisor/lib/supervisor_bridge\n"
        "COPY docs/supervisor/v1/journal-supervisor-bridge /opt/journal-supervisor/bin/journal-supervisor-bridge\n"
    )
    config = work / "docs/supervisor/v1/openclaw-live.json"
    config.write_text(json.dumps({
        "models": {"providers": {"anthropic": {"baseUrl": "http://127.0.0.1:17840", "api": "anthropic-messages", "maxTokens": 8000}}},
        "gateway": {"mode": "local", "bind": "lan", "auth": {"mode": "token"}},
        "plugins": {"enabled": True, "allow": ["anthropic"], "deny": ["memory-core"], "entries": {"memory-core": {"enabled": False, "config": {"dreaming": {"enabled": False}}}}},
        "agents": {"entries": {"supervisor": {"model": {"primary": "anthropic/claude-sonnet-5", "fallbacks": []}, "modelPolicy": {"allow": ["anthropic/claude-sonnet-5"]}, "thinkingDefault": "high", "models": {"anthropic/claude-sonnet-5": {"agentRuntime": {"id": "openclaw"}}}}}, "defaults": {"model": {"primary": "anthropic/claude-sonnet-5"}}},
        "hooks": {"enabled": True, "allowedAgentIds": ["supervisor"], "allowRequestSessionKey": False},
        "mcp": {"servers": {"journal": {"enabled": True, "transport": "stdio", "command": "/opt/journal-supervisor/bin/journal-supervisor-bridge", "args": ["mcp"], "connectionTimeoutMs": 5000, "requestTimeoutMs": 20000, "supportsParallelToolCalls": False, "toolFilter": {"include": ["journal_supervisor.observe", "journal_supervisor.apply_maintenance", "journal_supervisor.receipt"]}}}},
        "cron_add_params": {"name": "journal-supervisor-reconcile-v1", "agentId": "supervisor", "schedule": {"everyMs": 300000}, "sessionTarget": "isolated", "wakeMode": "now", "delivery": {"mode": "none"}},
        "hook_agent_request": {"deliver": False, "thinking": "high", "model": "anthropic/claude-sonnet-5", "timeoutSeconds": 180},
        "tools": {"allow": ["journal__journal_supervisor-observe", "journal__journal_supervisor-apply_maintenance", "journal__journal_supervisor-receipt"]},
    }))
    secrets = tmp_path / "tenant-secrets"
    secrets.mkdir(mode=0o700)
    for name in SECRET_FILES:
        (secrets / name).write_text(f"staged-{name}\n")
        (secrets / name).chmod(0o600)
    for name in EXTERNAL_SECRET_FILES:
        (secrets / name).write_text(f"staged-{name}\n")
        (secrets / name).chmod(0o600)
    (work / "docs/supervisor/v1/gateway-entrypoint.sh").write_text(
        "JOURNAL_SUPERVISOR_TLS_CA_FILE\n"
        "OPENCLAW_GATEWAY_TOKEN=$(node -e 'process.stdout.write(require(\"node:crypto\").randomBytes(32).toString(\"hex\"))')\n"
        "export ANTHROPIC_API_KEY OPENCLAW_HOOK_TOKEN OPENCLAW_GATEWAY_TOKEN JOURNAL_SUPERVISOR_ADMISSION_URL "
        "JOURNAL_SUPERVISOR_ADMISSION_TOKEN JOURNAL_SUPERVISOR_TLS_CA_FILE\n"
    )
    handler = work / "src/journal/http/supervisor_handler.py"
    handler.parent.mkdir(parents=True)
    handler.write_text("SERVICE_PATHS\ntoken-checked supervisor routes only\n")
    (work / "docs/supervisor/v1/firewall-policy.fixture.json").write_text(
        '"destination": "10.76.20.10 (writer)"\n"ports": [8422]\n"ports": [8421]\n'
        '"destination": "10.76.10.10 (writer management)"\n"ports": [8423]\n"action": "deny"\n'
    )
    (work / "src/journal/config.py").write_text(
        "JOURNAL_OWNER_ACCESS_HOST\nJOURNAL_OWNER_ACCESS_PORT\n"
        "JOURNAL_SUPERVISOR_HOST\nJOURNAL_SUPERVISOR_TLS_CERT_FILE\nsupervisor_listener\n"
    )
    (work / "src/journal/http/server.py").write_text(
        "SSLContext(ssl.PROTOCOL_TLS_SERVER)\nload_cert_chain\n"
        "_build_supervisor_handler\n_build_owner_access\n"
    )
    gateway_state = tmp_path / "gateway-state"
    gateway_state.mkdir(mode=0o700)
    (work / ENV_FILE).write_text(f"TENANT_SECRET_SOURCE_DIR={secrets}\nOPENCLAW_CONFIG_FILE={config}\nGATEWAY_STATE_PATH={gateway_state}\nPROFILE_REVISION=test-reviewed-revision\n")
    home = tmp_path / "secret-run-home"
    home.mkdir(mode=0o700)
    return work, secrets, home


def fake_docker(tmp_path, home, executable):
    directory = tmp_path / "path"
    directory.mkdir()
    (directory / "docker").symlink_to(executable)
    return directory


def run_launcher(executable, work, home, docker_path, key, *arguments):
    environment = {"PATH": f"{docker_path}:/usr/bin:/bin", "HOME": str(home), "LANG": "C.UTF-8"}
    return subprocess.run(
        [str(executable), *arguments],
        input=key,
        cwd=work,
        env=environment,
        capture_output=True,
        timeout=10,
    )


def test_launcher_starts_one_fixed_pinned_smoke_without_echoing_or_placing_the_key_in_arguments(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    key = b"sk-ant-test-fixed-smoke-key-123456789\n"
    (home / "gateway-starts-slow").touch()

    result = run_launcher(executable, work, home, docker_path, key)

    assert result.returncode == 0, result.stderr
    assert key.strip() not in result.stdout + result.stderr
    assert (home / "key-seen-by-runtime").read_bytes().strip() == key.strip()
    assert not (secrets / "supervisor_anthropic_api_key").exists()
    assert not Path((home / "secret-path").read_text()).exists()
    calls = (home / "docker-calls").read_text().splitlines()
    assert "--project-name journal-supervisor-smoke" in calls[0]
    assert f"--env-file {ENV_FILE}" in calls[0]
    assert f"-f {COMPOSE}" in calls[0]
    assert "--profile authorized-staging" in calls[0]
    assert "exec -T --user 10003:10003 writer /usr/local/bin/supervisor-codex-ready" in calls[0]
    up_indexes = [index for index, call in enumerate(calls) if " up " in f" {call} "]
    assert len(up_indexes) == 1
    assert "gateway" in calls[up_indexes[0]] and "writer" in calls[up_indexes[0]]
    assert "--no-build --pull never" in calls[up_indexes[0]]
    health_indexes = [index for index, call in enumerate(calls) if "healthz" in call]
    reconcile_indexes = [index for index, call in enumerate(calls) if "/opt/journal-supervisor/bin/journal-supervisor-bridge reconcile" in call]
    down_indexes = [index for index, call in enumerate(calls) if "down --timeout 3 --remove-orphans" in call]
    assert len(reconcile_indexes) == 1
    assert health_indexes and calls[health_indexes[-1]].find("gateway") >= 0
    assert down_indexes and up_indexes[0] < health_indexes[-1] < reconcile_indexes[0] < down_indexes[0]
    assert (home / "gateway-health-passed").exists()
    assert "exec -T gateway /opt/journal-supervisor/bin/journal-supervisor-bridge reconcile" in calls[reconcile_indexes[0]]
    assert "-v" not in calls[down_indexes[0]]
    assert key.decode().strip() not in " ".join(calls)
    assert "--message" not in " ".join(calls) and "--session" not in " ".join(calls)


def test_launcher_rejects_arguments_and_non_anthropic_input_without_starting_runtime(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)

    argument_result = run_launcher(executable, work, home, docker_path, b"not-a-key\n", "docker")
    input_result = run_launcher(executable, work, home, docker_path, b"not-a-key\n")

    assert argument_result.returncode != 0
    assert input_result.returncode != 0
    assert not (home / "docker-calls").exists()
    assert b"not-a-key" not in argument_result.stdout + argument_result.stderr + input_result.stdout + input_result.stderr


def test_launcher_refuses_a_direct_provider_route_or_model_fallback(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    config = work / "docs/supervisor/v1/openclaw-live.json"
    original = config.read_text()
    config.write_text(original.replace("http://127.0.0.1:17840", "https://api.anthropic.com"))

    direct_route = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    config.write_text(original.replace('"fallbacks": []', '"fallbacks": ["anthropic/claude-haiku"]'))
    fallback_route = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert direct_route.returncode != 0
    assert fallback_route.returncode != 0
    assert not (home / "docker-calls").exists()


def test_launcher_refuses_extra_plugins_or_mcp_servers(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    config = work / "docs/supervisor/v1/openclaw-live.json"
    original = json.loads(config.read_text())

    expanded_plugins = json.loads(json.dumps(original))
    expanded_plugins["plugins"]["allow"].append("browser")
    config.write_text(json.dumps(expanded_plugins))
    plugin_result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    expanded_servers = json.loads(json.dumps(original))
    expanded_servers["mcp"]["servers"]["extra"] = {"enabled": True}
    config.write_text(json.dumps(expanded_servers))
    server_result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert plugin_result.returncode != 0
    assert server_result.returncode != 0
    assert not (home / "docker-calls").exists()


def test_launcher_refuses_a_gateway_package_without_the_pinned_runtime(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    dockerfile = work / "docs/supervisor/v1/Dockerfile.gateway"
    dockerfile.write_text("FROM ghcr.io/openclaw/openclaw:latest\n")

    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert result.returncode != 0
    assert not (home / "docker-calls").exists()


def test_launcher_refuses_a_previous_receipt_in_the_gateway_state(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    gateway_state = tmp_path / "gateway-state/journal-supervisor-transport"
    gateway_state.mkdir()
    (gateway_state / "bridge-state.json").write_text('{"receipt":{"status":"applied"}}')

    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert result.returncode != 0
    assert not (home / "docker-calls").exists()


def test_launcher_stops_and_removes_the_staged_runtime_after_its_fixed_deadline(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    (home / "slow-up").touch()
    started = time.monotonic()

    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert time.monotonic() - started < 4
    assert result.returncode != 0
    calls = (home / "docker-calls").read_text().splitlines()
    assert any("healthz" in call for call in calls)
    assert not any("/opt/journal-supervisor/bin/journal-supervisor-bridge reconcile" in call for call in calls)
    assert "down --timeout 3 --remove-orphans" in calls[-1]
    assert not Path((home / "secret-path").read_text()).exists()
    assert "#define SMOKE_RUN_SECONDS 300" in SOURCE.read_text()


def test_launcher_refuses_when_writer_tls_material_is_missing(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    (secrets / "writer_supervisor_tls_key").unlink()

    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert result.returncode != 0
    assert not (home / "docker-calls").exists()


def test_launcher_refuses_to_start_services_without_the_persistent_codex_device_login(compiled_launcher, tmp_path):
    executable, docker_stub = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    (home / "codex-login-missing").touch()

    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert result.returncode != 0
    assert "device login" in result.stdout.decode()
    calls = (home / "docker-calls").read_text().splitlines()
    assert len(calls) == 1
    assert "supervisor-codex-ready" in calls[0]
    assert " up " not in f" {calls[0]} "


def test_uid10001_cannot_read_codex_driver_state_owned_by_uid10003():
    setpriv = shutil.which("setpriv")
    if os.name != "posix" or not setpriv or os.geteuid() != 0:
        pytest.skip("the DAC probe needs Linux setpriv and root to create the staged identities")
    volume = Path(tempfile.mkdtemp(prefix="codex-driver-state-"))
    try:
        auth = volume / "auth.json"
        auth.write_text("private Codex device token")
        os.chown(volume, 10003, 10003)
        os.chmod(volume, 0o700)
        os.chown(auth, 10003, 10003)
        os.chmod(auth, 0o600)
        denied = subprocess.run(
            [setpriv, "--reuid=10001", "--regid=10001", "--clear-groups", "--", sys.executable, "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).read_bytes()", str(auth)],
            capture_output=True,
            text=True,
        )
        assert denied.returncode != 0
        assert "PermissionError" in denied.stderr
        assert "private Codex device token" not in denied.stdout + denied.stderr
    finally:
        shutil.rmtree(volume)
