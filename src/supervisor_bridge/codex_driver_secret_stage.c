#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "live_smoke_settings.h"

#define ENV_FILE "docs/supervisor/v1/live-smoke.env"
#define MAX_PATH_BYTES 4096
#define MAX_SECRET_BYTES 4096
#define JOURNAL_UID 10001
#define JOURNAL_GID 10001

static void erase(char *value, size_t length) {
    volatile char *cursor = value;
    while (length--) *cursor++ = 0;
}

static bool private_directory(const char *path) {
    struct stat details;
    if (lstat(path, &details) != 0) return false;
    return S_ISDIR(details.st_mode) && details.st_uid == geteuid() && (details.st_mode & 0077) == 0;
}

static bool key_character(unsigned char byte) {
    return (byte >= 'a' && byte <= 'z') || (byte >= 'A' && byte <= 'Z')
        || (byte >= '0' && byte <= '9') || byte == '-' || byte == '_';
}

static int read_key(char *key, size_t capacity, size_t *length) {
    size_t used = 0;
    for (;;) {
        unsigned char byte;
        ssize_t count = read(STDIN_FILENO, &byte, 1);
        if (count < 0 && errno == EINTR) continue;
        if (count != 1) return -1;
        if (byte == '\n') break;
        if (!key_character(byte) || used >= capacity - 1) return -1;
        key[used++] = (char)byte;
    }
    unsigned char extra;
    ssize_t count;
    do count = read(STDIN_FILENO, &extra, 1); while (count < 0 && errno == EINTR);
    if (count != 0 || used < 16 || strncmp(key, "sk-", 3) != 0 || strncmp(key, "sk-ant-", 7) == 0) return -1;
    key[used] = 0;
    *length = used;
    return 0;
}

static int write_driver_secret(const char *directory, const char *key, size_t length) {
    int directory_fd = open(directory, O_RDONLY | O_DIRECTORY | O_NOFOLLOW);
    if (directory_fd < 0) return -1;
    int file = openat(directory_fd, "codex_driver_credentials", O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0400);
    if (file < 0) {
        close(directory_fd);
        return -1;
    }
    int result = 0;
    if (geteuid() == 0 && fchown(file, JOURNAL_UID, JOURNAL_GID) != 0) result = -1;
    size_t written = 0;
    while (result == 0 && written < length) {
        ssize_t amount = write(file, key + written, length - written);
        if (amount < 0 && errno == EINTR) continue;
        if (amount <= 0) result = -1;
        else written += (size_t)amount;
    }
    if (result == 0) {
        ssize_t newline;
        do newline = write(file, "\n", 1); while (newline < 0 && errno == EINTR);
        if (newline != 1) result = -1;
    }
    if (result == 0 && fchmod(file, 0400) != 0) result = -1;
    if (close(file) != 0) result = -1;
    if (result != 0) unlinkat(directory_fd, "codex_driver_credentials", 0);
    if (close(directory_fd) != 0) result = -1;
    return result;
}

int main(int argc, char **argv) {
    (void)argv;
    umask(077);
    char directory[MAX_PATH_BYTES];
    char key[MAX_SECRET_BYTES] = {0};
    size_t length = 0;
    if (argc != 1
        || live_smoke_setting_value(ENV_FILE, "TENANT_SECRET_SOURCE_DIR", directory, sizeof(directory)) != 0
        || !private_directory(directory)
        || read_key(key, sizeof(key), &length) != 0) {
        erase(key, sizeof(key));
        return 2;
    }
    int result = write_driver_secret(directory, key, length);
    erase(key, sizeof(key));
    if (result != 0) return 2;
    puts("Codex driver credential staged as a private file");
    return 0;
}
