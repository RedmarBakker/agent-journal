# Starts real programs, so it is not in the default run: journal suite tests/supervisor_smoke_launcher_processes_run.py -q.
from pathlib import Path
import json
import shutil
import subprocess
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
    int is_up = 0;
    for (int index = 1; index < argc; index++) if (strcmp(argv[index], "up") == 0) is_up = 1;
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
        if (is_up && access(path, F_OK) != 0) {
            const char *gateway_state = getenv("GATEWAY_STATE_PATH");
            if (!gateway_state) return 16;
            snprintf(path, sizeof(path), "%s/journal-supervisor-transport", gateway_state);
            if (mkdir(path, 0700) != 0) return 17;
            snprintf(path, sizeof(path), "%s/journal-supervisor-transport/bridge-state.json", gateway_state);
            FILE *state = fopen(path, "w");
            if (!state) return 18;
            fputs("{\"last_admission\":\"verified\",\"usage_settlement\":\"settled\",\"receipt\":{\"status\":\"applied\",\"verification\":\"verified\"},\"metering\":{\"provider_requests\":1}}", state);
            fclose(state);
            for (;;) pause();
        }
    }
    puts("synthetic provider key is not part of this line");
    return 0;
}
'''
    )
    compiled = subprocess.run(
        [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2", "-D_XOPEN_SOURCE=700", "-DSMOKE_RUN_SECONDS=1", str(SOURCE), "-o", str(executable)],
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
    (work / COMPOSE).write_text('"image":"agent-journal-supervisor-gateway:${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed source commit}"\n')
    (work / "docs/supervisor/v1/Dockerfile.gateway").write_text(
        "FROM ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5\n"
        "RUN apt-get install -y --no-install-recommends python3\n"
        "COPY src/supervisor_bridge /opt/journal-supervisor/lib/supervisor_bridge\n"
        "COPY docs/supervisor/v1/journal-supervisor-bridge /opt/journal-supervisor/bin/journal-supervisor-bridge\n"
    )
    config = work / "docs/supervisor/v1/openclaw-live.json"
    config.write_text(json.dumps({
        "models": {"providers": {"anthropic": {"baseUrl": "http://127.0.0.1:17840", "api": "anthropic-messages", "maxTokens": 8000}}},
        "agents": {"entries": {"supervisor": {"model": {"primary": "anthropic/claude-sonnet-5", "fallbacks": []}, "modelPolicy": {"allow": ["anthropic/claude-sonnet-5"]}, "thinkingDefault": "high", "models": {"anthropic/claude-sonnet-5": {"agentRuntime": {"id": "openclaw"}}}}}},
        "hooks": {"enabled": True, "allowedAgentIds": ["supervisor"], "allowRequestSessionKey": False},
        "mcp": {"servers": {"journal": {"enabled": True, "command": "/opt/journal-supervisor/bin/journal-supervisor-bridge", "args": ["mcp"]}}},
        "cron_add_params": {"name": "journal-supervisor-reconcile-v1", "agentId": "supervisor", "schedule": {"everyMs": 300000}, "sessionTarget": "isolated", "wakeMode": "now", "delivery": {"mode": "none"}},
        "hook_agent_request": {"deliver": False, "thinking": "high", "model": "anthropic/claude-sonnet-5", "timeoutSeconds": 180},
        "tools": {"allow": ["journal__journal_supervisor-observe", "journal__journal_supervisor-apply_maintenance", "journal__journal_supervisor-receipt"]},
    }))
    secrets = tmp_path / "tenant-secrets"
    secrets.mkdir(mode=0o700)
    for name in SECRET_FILES:
        (secrets / name).write_text(f"staged-{name}\n")
        (secrets / name).chmod(0o600)
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

    result = run_launcher(executable, work, home, docker_path, key)

    assert result.returncode == 0, result.stderr
    assert key.strip() not in result.stdout + result.stderr
    assert (home / "key-seen-by-runtime").read_bytes().strip() == key.strip()
    assert not (secrets / "supervisor_anthropic_api_key").exists()
    assert not Path((home / "secret-path").read_text()).exists()
    calls = (home / "docker-calls").read_text().splitlines()
    assert len(calls) == 2
    assert "--project-name journal-supervisor-smoke" in calls[0]
    assert f"--env-file {ENV_FILE}" in calls[0]
    assert f"-f {COMPOSE}" in calls[0]
    assert "--profile authorized-staging" in calls[0]
    assert "--no-build --pull never" in calls[0]
    assert " up " in f" {calls[0]} " and "gateway" in calls[0] and "writer" in calls[0]
    assert "down --timeout 3 --remove-orphans" in calls[1]
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
    assert len((home / "docker-calls").read_text().splitlines()) == 2
    assert not Path((home / "secret-path").read_text()).exists()
    assert "#define SMOKE_RUN_SECONDS 105" in SOURCE.read_text()
