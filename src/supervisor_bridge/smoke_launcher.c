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

#ifndef SMOKE_RUN_SECONDS
#define SMOKE_RUN_SECONDS 105
#endif

#define ENV_FILE "docs/supervisor/v1/live-smoke.env"
#define COMPOSE_FILE "docs/supervisor/v1/compose.json"
#define PROJECT_NAME "journal-supervisor-smoke"
#define MAX_SECRET_BYTES 4096
#define MAX_PATH_BYTES 4096
#define STOP_SECONDS 3

static const char *required_secret_files[] = {
    "openclaw_hook_token",
    "journal_supervisor_credential",
    "restic_password",
    "restic_repository",
    "backup_object_store_credentials",
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

static int setting_value(const char *setting, char *value, size_t capacity) {
    struct stat file_details;
    if (lstat(ENV_FILE, &file_details) != 0 || !S_ISREG(file_details.st_mode) || file_details.st_uid != geteuid() || (file_details.st_mode & 0022) != 0) return -1;
    FILE *settings = fopen(ENV_FILE, "r");
    if (!settings) return -1;
    char line[MAX_PATH_BYTES + 64];
    size_t prefix_length = strlen(setting) + 1;
    bool found = false;
    while (fgets(line, sizeof(line), settings)) {
        size_t length = strlen(line);
        if (length && line[length - 1] == '\n') line[--length] = 0;
        if (length < prefix_length || strncmp(line, setting, prefix_length - 1) != 0 || line[prefix_length - 1] != '=') continue;
        if (found || length <= prefix_length || length - prefix_length >= capacity) {
            fclose(settings);
            return -1;
        }
        const char *source = line + prefix_length;
        if (source[0] != '/') {
            fclose(settings);
            return -1;
        }
        for (const unsigned char *cursor = (const unsigned char *)source; *cursor; cursor++) {
            if (isspace(*cursor) || *cursor == '$' || *cursor == '`' || *cursor == '\\' || *cursor == '\'' || *cursor == '"') {
                fclose(settings);
                return -1;
            }
        }
        memcpy(value, source, length - prefix_length + 1);
        found = true;
    }
    int error = ferror(settings) ? -1 : 0;
    fclose(settings);
    return error == 0 && found ? 0 : -1;
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
    char *compose = NULL, *config = NULL;
    if (read_file(COMPOSE_FILE, &compose, 131072) != 0 || read_file(config_path, &config, 131072) != 0) {
        free(compose);
        free(config);
        return -1;
    }
    char *compact = compact_json(config);
    bool valid = compact
        && strstr(compose, "ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5")
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
    ssize_t count;
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

static int compose(bool down, const char *secret_directory, const char *gateway_state, int timeout) {
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
    char **arguments = down ? down_arguments : up_arguments;
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
    if (!down && path_join(receipt_path, sizeof(receipt_path), gateway_state, "journal-supervisor-transport/bridge-state.json")) wait_path = receipt_path;
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
    if (setting_value("TENANT_SECRET_SOURCE_DIR", source, sizeof(source)) != 0
        || setting_value("OPENCLAW_CONFIG_FILE", config_path, sizeof(config_path)) != 0
        || setting_value("GATEWAY_STATE_PATH", gateway_state, sizeof(gateway_state)) != 0
        || !private_directory(source)
        || !private_directory(gateway_state)
        || !path_join(receipt_path, sizeof(receipt_path), gateway_state, "journal-supervisor-transport/bridge-state.json")
        || !fresh_state(gateway_state)
        || valid_profile(config_path) != 0) return 2;
    for (size_t index = 0; index < sizeof(required_secret_files) / sizeof(required_secret_files[0]); index++) {
        char path[MAX_PATH_BYTES];
        if (!path_join(path, sizeof(path), source, required_secret_files[index]) || !required_file(path)) return 2;
    }
    const char *home = getenv("HOME");
    if (!home || !private_directory(home)) return 2;
    char directory[MAX_PATH_BYTES];
    if (!path_join(directory, sizeof(directory), home, "journal-supervisor-smoke-XXXXXX") || !mkdtemp(directory)) return 2;
    chmod(directory, 0700);
    bool ready = true;
    for (size_t index = 0; index < sizeof(required_secret_files) / sizeof(required_secret_files[0]); index++) {
        if (copy_secret(source, directory, required_secret_files[index]) != 0) ready = false;
    }
    char key[MAX_SECRET_BYTES + 1] = {0};
    size_t key_length = 0;
    if (!ready || read_key(key, sizeof(key), &key_length) != 0 || write_key(directory, key, key_length) != 0) {
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
    int result = compose(false, directory, gateway_state, SMOKE_RUN_SECONDS);
    int cleanup = compose(true, directory, gateway_state, STOP_SECONDS + 5);
    remove_secrets(directory);
    if (result == 0 && cleanup == 0) {
        puts("supervisor smoke stopped after one verified receipt");
        return 0;
    }
    puts("supervisor smoke runtime stopped without a verified result");
    return result ? result : cleanup;
}
