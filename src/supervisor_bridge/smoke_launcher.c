#if defined(__APPLE__)
#define _DARWIN_C_SOURCE
#endif
#define _POSIX_C_SOURCE 200809L
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include "live_smoke_settings.h"

#ifndef SMOKE_RUN_SECONDS
#define SMOKE_RUN_SECONDS 105
#endif

#define ENV_FILE "docs/supervisor/v1/live-smoke.env"
#define COMPOSE_FILE "docs/supervisor/v1/compose.json"
#define WRITER_DOCKERFILE "docker/Dockerfile"
#define WRITER_ENTRYPOINT "docker/entrypoint.sh"
#define CODEX_LOGIN "docker/supervisor-codex-login"
#define CODEX_READY "docker/supervisor-codex-ready"
#define WRITER_SETUP "docs/supervisor/v1/live-smoke-setup.py"
#define GATEWAY_DOCKERFILE "docs/supervisor/v1/Dockerfile.gateway"
#define GATEWAY_ENTRYPOINT "docs/supervisor/v1/gateway-entrypoint.sh"
#define SUPERVISOR_HANDLER "src/journal/http/supervisor_handler.py"
#define JOURNAL_CONFIG "src/journal/config.py"
#define JOURNAL_SERVER "src/journal/http/server.py"
#define FIREWALL_POLICY "docs/supervisor/v1/firewall-policy.fixture.json"
#define PROJECT_NAME "journal-supervisor-smoke"
#define MAX_SECRET_BYTES 4096
#define MAX_EXTERNAL_SECRET_BYTES 65536
#define MAX_PATH_BYTES 4096
#define STOP_SECONDS 3

static const char *required_secret_files[] = {
    "openclaw_hook_token",
    "journal_supervisor_credential",
    "restic_password",
    "restic_repository",
    "backup_object_store_credentials",
};

static const char *required_external_secret_files[] = {
    "writer_supervisor_tls_cert",
    "writer_supervisor_tls_key",
    "writer_supervisor_tls_ca",
};

static volatile sig_atomic_t stop_requested = 0;

static void request_stop(int signal_number) {
    (void)signal_number;
    stop_requested = 1;
}

static void erase(char *value, size_t length) {
    volatile char *cursor = value;
    while (length--) *cursor++ = 0;
}

static bool private_directory(const char *path) {
    struct stat details;
    if (lstat(path, &details) != 0) return false;
    return S_ISDIR(details.st_mode) && details.st_uid == geteuid() && (details.st_mode & 0077) == 0;
}

static bool required_file(const char *path) {
    struct stat details;
    if (lstat(path, &details) != 0) return false;
    return S_ISREG(details.st_mode) && (details.st_mode & 0022) == 0 && details.st_size > 0 && details.st_size <= MAX_SECRET_BYTES;
}

static bool required_external_file(const char *path) {
    struct stat details;
    if (lstat(path, &details) != 0) return false;
    return S_ISREG(details.st_mode) && (details.st_mode & 0022) == 0 && details.st_size > 0 && details.st_size <= MAX_EXTERNAL_SECRET_BYTES;
}

static bool path_join(char *result, size_t capacity, const char *directory, const char *name) {
    size_t directory_length = strlen(directory), name_length = strlen(name);
    if (directory_length + name_length + 2 > capacity) return false;
    memcpy(result, directory, directory_length);
    result[directory_length] = '/';
    memcpy(result + directory_length + 1, name, name_length + 1);
    return true;
}

static int read_file(const char *path, char **contents, size_t maximum) {
    int file = open(path, O_RDONLY | O_NOFOLLOW);
    if (file < 0) return -1;
    struct stat details;
    if (fstat(file, &details) != 0 || !S_ISREG(details.st_mode) || details.st_size <= 0 || (size_t)details.st_size > maximum || (details.st_mode & 0022) != 0) {
        close(file);
        return -1;
    }
    size_t length = (size_t)details.st_size;
    char *buffer = malloc(length + 1);
    if (!buffer) {
        close(file);
        return -1;
    }
    ssize_t total = 0;
    while ((size_t)total < length) {
        ssize_t count = read(file, buffer + total, length - (size_t)total);
        if (count <= 0) {
            free(buffer);
            close(file);
            return -1;
        }
        total += count;
    }
    close(file);
    buffer[length] = 0;
    *contents = buffer;
    return 0;
}

static char *compact_json(const char *json) {
    size_t length = strlen(json);
    char *compact = malloc(length + 1);
    if (!compact) return NULL;
    bool quoted = false, escaped = false;
    size_t used = 0;
    for (size_t index = 0; index < length; index++) {
        unsigned char byte = (unsigned char)json[index];
        if (!quoted && isspace(byte)) continue;
        compact[used++] = (char)byte;
        if (quoted && escaped) escaped = false;
        else if (quoted && byte == '\\') escaped = true;
        else if (byte == '"') quoted = !quoted;
    }
    compact[used] = 0;
    return compact;
}

static bool all_values_equal(const char *json, const char *key, const char *expected) {
    char marker[128];
    size_t key_length = strlen(key);
    if (key_length + 4 > sizeof(marker)) return false;
    marker[0] = '"';
    memcpy(marker + 1, key, key_length);
    marker[key_length + 1] = '"';
    marker[key_length + 2] = ':';
    marker[key_length + 3] = 0;
    const char *cursor = json;
    size_t count = 0, expected_length = strlen(expected);
    while ((cursor = strstr(cursor, marker))) {
        cursor += strlen(marker);
        if (strncmp(cursor, expected, expected_length) != 0) return false;
        cursor += expected_length;
        count++;
    }
    return count > 0;
}

static bool all_arrays_empty(const char *json, const char *key) {
    char marker[128];
    size_t key_length = strlen(key);
    if (key_length + 4 > sizeof(marker)) return false;
    marker[0] = '"';
    memcpy(marker + 1, key, key_length);
    marker[key_length + 1] = '"';
    marker[key_length + 2] = ':';
    marker[key_length + 3] = 0;
    const char *cursor = json;
    size_t count = 0;
    while ((cursor = strstr(cursor, marker))) {
        cursor += strlen(marker);
        if (strncmp(cursor, "[]", 2) != 0) return false;
        cursor += 2;
        count++;
    }
    return count > 0;
}

static bool contains_all(const char *text, const char *const *needles, size_t count) {
    for (size_t index = 0; index < count; index++) if (!strstr(text, needles[index])) return false;
    return true;
}

static int valid_profile(const char *config_path) {
    static const char *required_config[] = {
        "\"allowRequestSessionKey\":false",
        "\"allowedAgentIds\":[\"supervisor\"]",
        "\"allow\":[\"anthropic/claude-sonnet-5\"]",
        "\"id\":\"openclaw\"",
        "\"hooks\":{\"enabled\":true",
        "\"mcp\":{\"servers\":{\"journal\":{\"enabled\":true",
        "\"command\":\"/opt/journal-supervisor/bin/journal-supervisor-bridge\"",
        "journal__journal_supervisor-observe",
        "journal__journal_supervisor-apply_maintenance",
        "journal__journal_supervisor-receipt",
    };
    static const char *required_gateway_image[] = {
        "agent-journal-supervisor-gateway:${PROFILE_REVISION:?set PROFILE_REVISION to the reviewed source commit}",
    };
    static const char *required_gateway_package[] = {
        "FROM ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5",
        "apt-get install -y --no-install-recommends python3",
        "COPY src/supervisor_bridge /opt/journal-supervisor/lib/supervisor_bridge",
        "COPY docs/supervisor/v1/journal-supervisor-bridge /opt/journal-supervisor/bin/journal-supervisor-bridge",
    };
    static const char *required_writer_package[] = {
        "npm install -g @openai/codex@0.165.0",
        "groupadd --gid 10003 codex-driver",
        "useradd --uid 10003 --gid codex-driver",
        "chown codex-driver:codex-driver /var/lib/journal-codex",
        "chmod 700 /data/home /data/secrets /data/gateway /data/vault /var/lib/journal-codex",
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-login docker/supervisor-codex-ready /usr/local/bin/",
        "COPY --chown=root:root --chmod=755 docker/supervisor-codex-plan-launcher.py /usr/local/bin/supervisor-codex-plan-launcher",
        "COPY docs/supervisor/v1/live-smoke-setup.py /usr/local/bin/supervisor-live-setup",
    };
    static const char *required_writer_volume[] = {
        "\"JOURNAL_HOST\": \"127.0.0.1\"",
        "\"JOURNAL_OWNER_ACCESS_HOST\": \"10.76.10.10\"",
        "\"JOURNAL_OWNER_ACCESS_PORT\": \"8423\"",
        "\"JOURNAL_SUPERVISOR_HOST\": \"10.76.20.10\"",
        "\"JOURNAL_SUPERVISOR_PORT\": \"8422\"",
        "\"JOURNAL_SUPERVISOR_TLS_CERT_FILE\": \"/run/secrets/writer_supervisor_tls_cert\"",
        "\"JOURNAL_SUPERVISOR_TLS_KEY_FILE\": \"/run/secrets/writer_supervisor_tls_key\"",
        "\"ports\": [\"127.0.0.1:18440:8423\"]",
        "\"expose\": [\"8422\"]",
        "\"JOURNAL_SUPERVISOR_ADMISSION_URL\": \"https://writer:8422\"",
        "\"JOURNAL_SUPERVISOR_TLS_CA_FILE\": \"/run/secrets/writer_supervisor_tls_ca\"",
        "TENANT_SECRET_SOURCE_DIR",
        "${TENANT_SECRET_SOURCE_DIR:?set the root-owned tenant secret source directory}/writer_supervisor_tls_cert",
        "${TENANT_SECRET_SOURCE_DIR:?set the root-owned tenant secret source directory}/writer_supervisor_tls_key",
        "${TENANT_SECRET_SOURCE_DIR:?set the root-owned tenant secret source directory}/writer_supervisor_tls_ca",
        "\"JOURNAL_CODEX_HOME\": \"/var/lib/journal-codex\"",
        "\"JOURNAL_PLAN_DRIVER_SOCKET\": \"/run/journal-plan-driver.sock\"",
        "\"codex_driver_state:/var/lib/journal-codex\"",
        "\"codex_driver_state\": {}",
        "\"cap_add\": [\"SETUID\", \"SETGID\", \"SETPCAP\"]",
    };
    static const char *required_gateway_entrypoint[] = {
        "JOURNAL_SUPERVISOR_TLS_CA_FILE",
        "export ANTHROPIC_API_KEY OPENCLAW_HOOK_TOKEN JOURNAL_SUPERVISOR_ADMISSION_URL JOURNAL_SUPERVISOR_ADMISSION_TOKEN JOURNAL_SUPERVISOR_TLS_CA_FILE",
    };
    static const char *required_supervisor_handler[] = {
        "SERVICE_PATHS",
        "token-checked supervisor routes only",
    };
    static const char *required_listener_config[] = {
        "JOURNAL_OWNER_ACCESS_HOST",
        "JOURNAL_OWNER_ACCESS_PORT",
        "JOURNAL_SUPERVISOR_HOST",
        "JOURNAL_SUPERVISOR_TLS_CERT_FILE",
        "supervisor_listener",
    };
    static const char *required_listener_server[] = {
        "SSLContext(ssl.PROTOCOL_TLS_SERVER)",
        "load_cert_chain",
        "_build_supervisor_handler",
        "_build_owner_access",
    };
    static const char *required_firewall[] = {
        "\"destination\": \"10.76.20.10 (writer)\"",
        "\"ports\": [8422]",
        "\"ports\": [8421]",
        "\"destination\": \"10.76.10.10 (writer management)\"",
        "\"ports\": [8423]",
        "\"action\": \"deny\"",
    };
    static const char *required_writer_entrypoint[] = {
        "supervisor-codex-ready",
        "setpriv --reuid 10003 --regid 10003 --clear-groups supervisor-codex-ready",
        "/run/journal-plan-driver-server.pid",
        "supervisor-codex-plan-launcher",
        "complete supervisor-codex-login before starting the writer",
    };
    static const char *required_login_command[] = {
        "supervisor-codex-login accepts no arguments",
        "supervisor-codex-login must run as uid/gid 10003",
        "pre-created as uid/gid 10003 with mode 0700",
        "codex login --device-auth",
    };
    static const char *required_ready_command[] = {
        "supervisor-codex-ready accepts no arguments",
        "supervisor-codex-ready must run as uid/gid 10003",
        "Codex device login is absent or not private",
        "stat -c %u",
        "stat -c %g",
        "stat -c %a",
    };
    static const char *required_setup[] = {
        "if len(sys.argv) != 1",
        "/_supervisor/v1/enrollment",
        "PlanMode.SOLO",
        "SupervisorLink",
        "\"max_input_tokens_per_turn\": 24000",
        "\"max_output_tokens_per_turn\": 8000",
        "\"max_provider_requests_per_turn\": 8",
        "\"mode\": \"bounded_write\"",
    };
    char *compose = NULL, *writer_package = NULL, *writer_entrypoint = NULL, *writer_setup = NULL;
    char *login_command = NULL, *ready_command = NULL;
    char *gateway_package = NULL, *gateway_entrypoint = NULL, *supervisor_handler = NULL;
    char *firewall = NULL, *journal_config = NULL, *journal_server = NULL, *config = NULL;
    if (read_file(COMPOSE_FILE, &compose, 131072) != 0
        || read_file(WRITER_DOCKERFILE, &writer_package, 131072) != 0
        || read_file(WRITER_ENTRYPOINT, &writer_entrypoint, 131072) != 0
        || read_file(CODEX_LOGIN, &login_command, 131072) != 0
        || read_file(CODEX_READY, &ready_command, 131072) != 0
        || read_file(WRITER_SETUP, &writer_setup, 131072) != 0
        || read_file(GATEWAY_DOCKERFILE, &gateway_package, 131072) != 0
        || read_file(GATEWAY_ENTRYPOINT, &gateway_entrypoint, 131072) != 0
        || read_file(SUPERVISOR_HANDLER, &supervisor_handler, 131072) != 0
        || read_file(FIREWALL_POLICY, &firewall, 131072) != 0
        || read_file(JOURNAL_CONFIG, &journal_config, 131072) != 0
        || read_file(JOURNAL_SERVER, &journal_server, 131072) != 0
        || read_file(config_path, &config, 131072) != 0) {
        free(compose);
        free(writer_package);
        free(writer_entrypoint);
        free(login_command);
        free(ready_command);
        free(writer_setup);
        free(gateway_package);
        free(gateway_entrypoint);
        free(supervisor_handler);
        free(firewall);
        free(journal_config);
        free(journal_server);
        free(config);
        return -1;
    }
    char *compact = compact_json(config);
    const char *gateway_service = strstr(compose, "\"gateway\": {");
    const char *backup_service = gateway_service ? strstr(gateway_service, "\"backup\": {") : NULL;
    bool valid = compact
        && gateway_service && backup_service
        && contains_all(compose, required_gateway_image, sizeof(required_gateway_image) / sizeof(required_gateway_image[0]))
        && contains_all(compose, required_writer_volume, sizeof(required_writer_volume) / sizeof(required_writer_volume[0]))
        && contains_all(gateway_entrypoint, required_gateway_entrypoint, sizeof(required_gateway_entrypoint) / sizeof(required_gateway_entrypoint[0]))
        && contains_all(supervisor_handler, required_supervisor_handler, sizeof(required_supervisor_handler) / sizeof(required_supervisor_handler[0]))
        && contains_all(firewall, required_firewall, sizeof(required_firewall) / sizeof(required_firewall[0]))
        && contains_all(journal_config, required_listener_config, sizeof(required_listener_config) / sizeof(required_listener_config[0]))
        && contains_all(journal_server, required_listener_server, sizeof(required_listener_server) / sizeof(required_listener_server[0]))
        && contains_all(writer_package, required_writer_package, sizeof(required_writer_package) / sizeof(required_writer_package[0]))
        && contains_all(writer_entrypoint, required_writer_entrypoint, sizeof(required_writer_entrypoint) / sizeof(required_writer_entrypoint[0]))
        && contains_all(login_command, required_login_command, sizeof(required_login_command) / sizeof(required_login_command[0]))
        && !strstr(login_command, "chown")
        && contains_all(ready_command, required_ready_command, sizeof(required_ready_command) / sizeof(required_ready_command[0]))
        && contains_all(writer_setup, required_setup, sizeof(required_setup) / sizeof(required_setup[0]))
        && contains_all(gateway_package, required_gateway_package, sizeof(required_gateway_package) / sizeof(required_gateway_package[0]))
        && contains_all(compact, required_config, sizeof(required_config) / sizeof(required_config[0]))
        && all_values_equal(compact, "api", "\"anthropic-messages\"")
        && all_values_equal(compact, "maxTokens", "8000")
        && all_values_equal(compact, "primary", "\"anthropic/claude-sonnet-5\"")
        && all_values_equal(compact, "thinkingDefault", "\"high\"")
        && all_values_equal(compact, "baseUrl", "\"http://127.0.0.1:17840\"")
        && all_arrays_empty(compact, "fallbacks")
        && !strstr(compact, "https://api.anthropic.com");
    free(compact);
    free(compose);
    free(writer_package);
    free(writer_entrypoint);
    free(login_command);
    free(ready_command);
    free(writer_setup);
    free(gateway_package);
    free(gateway_entrypoint);
    free(supervisor_handler);
    free(firewall);
    free(journal_config);
    free(journal_server);
    free(config);
    return valid ? 0 : -1;
}

static bool receipt_complete(const char *path) {
    char *state = NULL;
    if (read_file(path, &state, 131072) != 0) return false;
    char *compact = compact_json(state);
    free(state);
    if (!compact) return false;
    char *requests = strstr(compact, "\"provider_requests\":");
    long request_count = requests ? strtol(requests + strlen("\"provider_requests\":"), NULL, 10) : 0;
    bool complete = strstr(compact, "\"last_admission\":\"verified\"")
        && strstr(compact, "\"usage_settlement\":\"settled\"")
        && strstr(compact, "\"status\":\"applied\"")
        && strstr(compact, "\"verification\":\"verified\"")
        && request_count > 0;
    free(compact);
    return complete;
}

static bool fresh_state(const char *gateway_state) {
    char path[MAX_PATH_BYTES], *state = NULL;
    if (!path_join(path, sizeof(path), gateway_state, "journal-supervisor-transport/bridge-state.json")) return false;
    if (read_file(path, &state, 131072) != 0) return access(path, F_OK) != 0 && errno == ENOENT;
    char *compact = compact_json(state);
    free(state);
    if (!compact) return false;
    bool fresh = strstr(compact, "\"receipt\":null") != NULL;
    free(compact);
    return fresh;
}

static int copy_secret(const char *source_directory_path, const char *target_directory, const char *name) {
    char source[MAX_PATH_BYTES], target[MAX_PATH_BYTES];
    if (!path_join(source, sizeof(source), source_directory_path, name)) return -1;
    if (!path_join(target, sizeof(target), target_directory, name)) return -1;
    int source_fd = open(source, O_RDONLY | O_NOFOLLOW);
    if (source_fd < 0) return -1;
    struct stat details;
    if (fstat(source_fd, &details) != 0 || !S_ISREG(details.st_mode) || details.st_size <= 0 || details.st_size > MAX_SECRET_BYTES || (details.st_mode & 0022) != 0) {
        close(source_fd);
        return -1;
    }
    int target_fd = open(target, O_WRONLY | O_CREAT | O_EXCL, 0444);
    if (target_fd < 0) {
        close(source_fd);
        return -1;
    }
    char buffer[MAX_SECRET_BYTES];
    ssize_t count = 0;
    int result = 0;
    while ((count = read(source_fd, buffer, sizeof(buffer))) > 0) {
        ssize_t written = 0;
        while (written < count) {
            ssize_t amount = write(target_fd, buffer + written, (size_t)(count - written));
            if (amount <= 0) {
                result = -1;
                break;
            }
            written += amount;
        }
        if (result != 0) break;
    }
    if (count < 0) result = -1;
    erase(buffer, sizeof(buffer));
    if (close(source_fd) != 0 || close(target_fd) != 0) result = -1;
    return result;
}

static int read_key(char *key, size_t capacity, size_t *length) {
    size_t used = 0;
    for (;;) {
        unsigned char byte;
        ssize_t count = read(STDIN_FILENO, &byte, 1);
        if (count != 1) return -1;
        if (byte == '\n') break;
        if (byte < 0x21 || byte > 0x7e || used >= capacity - 1) return -1;
        if (!(isalnum(byte) || byte == '-' || byte == '_')) return -1;
        key[used++] = (char)byte;
    }
    unsigned char extra;
    if (read(STDIN_FILENO, &extra, 1) != 0 || used < 16 || strncmp(key, "sk-ant-", 7) != 0) return -1;
    key[used] = 0;
    *length = used;
    return 0;
}

static int write_key(const char *directory, const char *key, size_t length) {
    char path[MAX_PATH_BYTES];
    if (!path_join(path, sizeof(path), directory, "supervisor_anthropic_api_key")) return -1;
    int file = open(path, O_WRONLY | O_CREAT | O_EXCL, 0444);
    if (file < 0) return -1;
    ssize_t written = 0;
    while ((size_t)written < length) {
        ssize_t amount = write(file, key + written, length - (size_t)written);
        if (amount <= 0) {
            close(file);
            unlink(path);
            return -1;
        }
        written += amount;
    }
    if (write(file, "\n", 1) != 1 || close(file) != 0) {
        unlink(path);
        return -1;
    }
    return 0;
}

static int stop_child(pid_t child, int result) {
    struct timespec interval = {.tv_sec = 0, .tv_nsec = 100000000};
    int status = 0;
    kill(child, SIGTERM);
    for (int attempt = 0; attempt < STOP_SECONDS * 10; attempt++) {
        pid_t stopped = waitpid(child, &status, WNOHANG);
        if (stopped == child) return result;
        nanosleep(&interval, NULL);
    }
    kill(child, SIGKILL);
    waitpid(child, &status, 0);
    return result;
}

static int wait_for(pid_t child, int seconds, const char *receipt_path) {
    struct timespec interval = {.tv_sec = 0, .tv_nsec = 100000000};
    struct timespec started;
    clock_gettime(CLOCK_MONOTONIC, &started);
    int status = 0;
    while (!stop_requested) {
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        time_t deadline = started.tv_sec + seconds;
        if (now.tv_sec > deadline || (now.tv_sec == deadline && now.tv_nsec >= started.tv_nsec)) break;
        if (receipt_path && receipt_complete(receipt_path)) return stop_child(child, 0);
        pid_t result = waitpid(child, &status, WNOHANG);
        if (result == child) {
            if (!WIFEXITED(status)) return 128;
            if (WEXITSTATUS(status) == 0 && receipt_path) return 2;
            return WEXITSTATUS(status);
        }
        if (result < 0 && errno != EINTR) return 127;
        nanosleep(&interval, NULL);
    }
    return stop_child(child, stop_requested ? 128 : 124);
}

typedef enum { COMPOSE_READY, COMPOSE_UP, COMPOSE_DOWN } ComposeAction;

static int compose(ComposeAction action, const char *secret_directory, const char *gateway_state, int timeout) {
    char *up_arguments[] = {
        "docker", "compose", "--project-name", PROJECT_NAME, "--env-file", ENV_FILE,
        "-f", COMPOSE_FILE, "--profile", "authorized-staging", "up", "--no-build",
        "--pull", "never", "--abort-on-container-exit", "--exit-code-from", "gateway",
        "writer", "gateway", NULL,
    };
    char *down_arguments[] = {
        "docker", "compose", "--project-name", PROJECT_NAME, "--env-file", ENV_FILE,
        "-f", COMPOSE_FILE, "--profile", "authorized-staging", "down", "--timeout",
        "3", "--remove-orphans", NULL,
    };
    char *ready_arguments[] = {
        "docker", "compose", "--project-name", PROJECT_NAME, "--env-file", ENV_FILE,
        "-f", COMPOSE_FILE, "--profile", "authorized-staging", "run", "--rm",
        "--no-deps", "--user", "10003:10003", "--entrypoint", "/usr/local/bin/supervisor-codex-ready", "writer", NULL,
    };
    char **arguments = action == COMPOSE_DOWN ? down_arguments : action == COMPOSE_READY ? ready_arguments : up_arguments;
    pid_t child = fork();
    if (child < 0) return 127;
    if (child == 0) {
        int null = open("/dev/null", O_WRONLY);
        if (null >= 0) {
            dup2(null, STDOUT_FILENO);
            dup2(null, STDERR_FILENO);
            close(null);
        }
        setenv("TENANT_SECRET_DIR", secret_directory, 1);
        setenv("GATEWAY_STATE_PATH", gateway_state, 1);
        execvp("docker", arguments);
        _exit(127);
    }
    char receipt_path[MAX_PATH_BYTES];
    const char *wait_path = NULL;
    if (action == COMPOSE_UP && path_join(receipt_path, sizeof(receipt_path), gateway_state, "journal-supervisor-transport/bridge-state.json")) wait_path = receipt_path;
    return wait_for(child, timeout, wait_path);
}

static void remove_secrets(const char *directory) {
    char path[MAX_PATH_BYTES];
    for (size_t index = 0; index < sizeof(required_secret_files) / sizeof(required_secret_files[0]); index++) {
        if (path_join(path, sizeof(path), directory, required_secret_files[index])) unlink(path);
    }
    if (path_join(path, sizeof(path), directory, "supervisor_anthropic_api_key")) unlink(path);
    rmdir(directory);
}

int main(int argc, char **argv) {
    (void)argv;
    if (argc != 1 || access(COMPOSE_FILE, R_OK) != 0 || access(ENV_FILE, R_OK) != 0) return 2;
    char source[MAX_PATH_BYTES], config_path[MAX_PATH_BYTES], gateway_state[MAX_PATH_BYTES], receipt_path[MAX_PATH_BYTES];
    if (live_smoke_setting_value(ENV_FILE, "TENANT_SECRET_SOURCE_DIR", source, sizeof(source)) != 0
        || live_smoke_setting_value(ENV_FILE, "OPENCLAW_CONFIG_FILE", config_path, sizeof(config_path)) != 0
        || live_smoke_setting_value(ENV_FILE, "GATEWAY_STATE_PATH", gateway_state, sizeof(gateway_state)) != 0
        || !private_directory(source)
        || !private_directory(gateway_state)
        || !path_join(receipt_path, sizeof(receipt_path), gateway_state, "journal-supervisor-transport/bridge-state.json")
        || !fresh_state(gateway_state)
        || valid_profile(config_path) != 0) return 2;
    for (size_t index = 0; index < sizeof(required_secret_files) / sizeof(required_secret_files[0]); index++) {
        char path[MAX_PATH_BYTES];
        if (!path_join(path, sizeof(path), source, required_secret_files[index])) return 2;
        if (!required_file(path)) return 2;
    }
    for (size_t index = 0; index < sizeof(required_external_secret_files) / sizeof(required_external_secret_files[0]); index++) {
        char path[MAX_PATH_BYTES];
        if (!path_join(path, sizeof(path), source, required_external_secret_files[index])) return 2;
        if (!required_external_file(path)) return 2;
    }
    const char *home = getenv("HOME");
    if (!home || !private_directory(home)) return 2;
    char directory[MAX_PATH_BYTES];
    if (!path_join(directory, sizeof(directory), home, "journal-supervisor-smoke-XXXXXX") || !mkdtemp(directory)) return 2;
    chmod(directory, 0700);
    bool secrets_ready = true;
    for (size_t index = 0; index < sizeof(required_secret_files) / sizeof(required_secret_files[0]); index++) {
        if (copy_secret(source, directory, required_secret_files[index]) != 0) secrets_ready = false;
    }
    char key[MAX_SECRET_BYTES + 1] = {0};
    size_t key_length = 0;
    if (!secrets_ready || read_key(key, sizeof(key), &key_length) != 0 || write_key(directory, key, key_length) != 0) {
        erase(key, sizeof(key));
        remove_secrets(directory);
        return 2;
    }
    erase(key, sizeof(key));
    struct sigaction action = {0};
    action.sa_handler = request_stop;
    sigemptyset(&action.sa_mask);
    sigaction(SIGINT, &action, NULL);
    sigaction(SIGTERM, &action, NULL);
    int codex_ready = compose(COMPOSE_READY, directory, gateway_state, 30);
    if (codex_ready != 0) {
        remove_secrets(directory);
        puts("supervisor smoke refused to start without the staged Codex device login");
        return codex_ready;
    }
    int result = compose(COMPOSE_UP, directory, gateway_state, SMOKE_RUN_SECONDS);
    int cleanup = compose(COMPOSE_DOWN, directory, gateway_state, STOP_SECONDS + 5);
    remove_secrets(directory);
    if (result == 0 && cleanup == 0) {
        puts("supervisor smoke stopped after one verified receipt");
        return 0;
    }
    puts("supervisor smoke runtime stopped without a verified result");
    return result ? result : cleanup;
}
