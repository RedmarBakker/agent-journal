# Starts real programs, so it is not in the default run: journal suite tests/supervisor_smoke_launcher_processes_run.py -q.
from pathlib import Path
import json
import os
import shutil
import stat
import subprocess
import time

import pytest


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "src" / "supervisor_bridge" / "smoke_launcher.c"
SECRET_STAGE_SOURCE = ROOT / "src" / "supervisor_bridge" / "codex_driver_secret_stage.c"
COMPOSE = "docs/supervisor/v1/compose.json"
ENV_FILE = "docs/supervisor/v1/live-smoke.env"
SECRET_FILES = (
    "codex_driver_credentials",
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
    secret_stage = tmp_path / "journal-supervisor-driver-secret-stage"
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
        snprintf(path, sizeof(path), "%s/codex_driver_credentials", secret_dir);
        struct stat driver_secret;
        if (stat(path, &driver_secret) != 0 || (driver_secret.st_mode & 0777) != 0400) return 19;
        snprintf(path, sizeof(path), "%s/driver-secret-info", home);
        FILE *driver_info = fopen(path, "w");
        if (!driver_info) return 20;
        fprintf(driver_info, "%o %u\n", driver_secret.st_mode & 0777, driver_secret.st_uid);
        fclose(driver_info);
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
    staged = subprocess.run(
        [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2", "-D_XOPEN_SOURCE=700", str(SECRET_STAGE_SOURCE), "-o", str(secret_stage)],
        capture_output=True,
        text=True,
    )
    assert staged.returncode == 0, staged.stderr
    subprocess.run(
        [compiler, "-std=c11", "-Wall", "-Wextra", "-O2", str(stub_source), "-o", str(docker_stub)],
        check=True,
        capture_output=True,
        text=True,
    )
    return executable, docker_stub, secret_stage


def staging_root(tmp_path):
    work = tmp_path / "project"
    (work / "docs/supervisor/v1").mkdir(parents=True)
    (work / COMPOSE).write_text(
        '{"services":{"writer":{"secrets":[{"source": "codex_driver_credentials", "target": "codex_driver_credentials"}],'
        '"environment":{"CODEX_HOME": "/run/codex"}},'
        '"gateway": {"secrets":[]},"backup": {"secrets":[]}},'
        '"image":"agent-journal-supervisor-gateway:${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed source commit}",'
        '"secrets":{"codex_driver_credentials": {"file": "${TENANT_SECRET_DIR:?set the temporary tenant secret directory}/codex_driver_credentials"}}}\n'
    )
    (work / "docker").mkdir()
    (work / "docker/Dockerfile").write_text(
        "RUN npm install -g @openai/codex@0.165.0\n"
        "COPY docs/supervisor/v1/live-smoke-setup.py /usr/local/bin/supervisor-live-setup\n"
    )
    (work / "docker/entrypoint.sh").write_text(
        "codex login --with-api-key < /run/secrets/codex_driver_credentials >/dev/null 2>&1\n"
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
        (secrets / name).chmod(0o400 if name == "codex_driver_credentials" else 0o600)
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


def run_secret_stage(executable, work, key, *arguments):
    return subprocess.run(
        [str(executable), *arguments],
        input=key,
        cwd=work,
        env={"PATH": "/usr/bin:/bin", "HOME": "/root", "LANG": "C.UTF-8"},
        capture_output=True,
        timeout=10,
    )


def test_launcher_starts_one_fixed_pinned_smoke_without_echoing_or_placing_the_key_in_arguments(compiled_launcher, tmp_path):
    executable, docker_stub, _secret_stage = compiled_launcher
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
    executable, docker_stub, _secret_stage = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)

    argument_result = run_launcher(executable, work, home, docker_path, b"not-a-key\n", "docker")
    input_result = run_launcher(executable, work, home, docker_path, b"not-a-key\n")

    assert argument_result.returncode != 0
    assert input_result.returncode != 0
    assert not (home / "docker-calls").exists()
    assert b"not-a-key" not in argument_result.stdout + argument_result.stderr + input_result.stdout + input_result.stderr


def test_launcher_refuses_a_direct_provider_route_or_model_fallback(compiled_launcher, tmp_path):
    executable, docker_stub, _secret_stage = compiled_launcher
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
    executable, docker_stub, _secret_stage = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    dockerfile = work / "docs/supervisor/v1/Dockerfile.gateway"
    dockerfile.write_text("FROM ghcr.io/openclaw/openclaw:latest\n")

    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert result.returncode != 0
    assert not (home / "docker-calls").exists()


def test_launcher_refuses_a_previous_receipt_in_the_gateway_state(compiled_launcher, tmp_path):
    executable, docker_stub, _secret_stage = compiled_launcher
    work, _secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    gateway_state = tmp_path / "gateway-state/journal-supervisor-transport"
    gateway_state.mkdir()
    (gateway_state / "bridge-state.json").write_text('{"receipt":{"status":"applied"}}')

    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert result.returncode != 0
    assert not (home / "docker-calls").exists()


def test_launcher_stops_and_removes_the_staged_runtime_after_its_fixed_deadline(compiled_launcher, tmp_path):
    executable, docker_stub, _secret_stage = compiled_launcher
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


def test_codex_secret_stage_writes_one_owner_only_file_without_echoing_the_key(compiled_launcher, tmp_path):
    _launcher, _docker_stub, secret_stage = compiled_launcher
    work, secrets, _home = staging_root(tmp_path)
    key = b"sk-proj-supervisor-test-key-123456789\n"

    result = run_secret_stage(secret_stage, work, key)

    secret = secrets / "codex_driver_credentials"
    details = secret.stat()
    expected_owner = 10001 if os.geteuid() == 0 else os.geteuid()
    assert result.returncode == 0, result.stderr
    assert key.strip() not in result.stdout + result.stderr
    assert secret.read_bytes() == key
    assert stat.S_IMODE(details.st_mode) == 0o400 and details.st_uid == expected_owner


def test_codex_secret_stage_rejects_arguments_malformed_lines_and_unbounded_input(compiled_launcher, tmp_path):
    _launcher, _docker_stub, secret_stage = compiled_launcher
    work, secrets, _home = staging_root(tmp_path)
    (secrets / "codex_driver_credentials").unlink()
    key = b"sk-proj-supervisor-test-key-123456789\n"
    anthropic_key = b"sk-ant-test-anthropic-key-123456789\n"

    argument = run_secret_stage(secret_stage, work, key, "extra")
    malformed = run_secret_stage(secret_stage, work, b"not-an-openai-key\n")
    anthropic = run_secret_stage(secret_stage, work, anthropic_key)
    multiple = run_secret_stage(secret_stage, work, key + b"second-line\n")
    unbounded = run_secret_stage(secret_stage, work, b"sk-" + b"a" * 4096 + b"\n")

    assert all(result.returncode != 0 for result in (argument, malformed, anthropic, multiple, unbounded))
    assert not (secrets / "codex_driver_credentials").exists()
    assert all(key.strip() not in result.stdout + result.stderr for result in (argument, malformed, anthropic, multiple, unbounded))
    assert anthropic_key.strip() not in anthropic.stdout + anthropic.stderr


def test_codex_secret_stage_refuses_to_replace_an_existing_credential(compiled_launcher, tmp_path):
    _launcher, _docker_stub, secret_stage = compiled_launcher
    work, secrets, _home = staging_root(tmp_path)
    existing = (secrets / "codex_driver_credentials").read_bytes()

    result = run_secret_stage(secret_stage, work, b"sk-proj-supervisor-test-key-123456789\n")

    assert result.returncode != 0
    assert (secrets / "codex_driver_credentials").read_bytes() == existing


def test_launcher_requires_the_codex_driver_secret_and_copies_it_private(compiled_launcher, tmp_path):
    executable, docker_stub, _secret_stage = compiled_launcher
    work, secrets, home = staging_root(tmp_path)
    docker_path = fake_docker(tmp_path, home, docker_stub)
    secret = secrets / "codex_driver_credentials"
    original_owner = secret.stat().st_uid
    secret.chmod(0o600)

    wrong_mode = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")
    secret.unlink()
    missing = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")

    assert wrong_mode.returncode != 0 and missing.returncode != 0
    assert not (home / "docker-calls").exists()
    secret.write_text("sk-proj-staged-driver-credential-123456789\n")
    secret.chmod(0o400)
    result = run_launcher(executable, work, home, docker_path, b"sk-ant-test-fixed-smoke-key-123456789\n")
    assert result.returncode == 0, result.stderr
    copied = (home / "driver-secret-info").read_text().split()
    assert int(copied[0], 8) == 0o400 and int(copied[1]) == original_owner
    assert not Path((home / "secret-path").read_text()).joinpath("codex_driver_credentials").exists()
