#ifndef JOURNAL_SUPERVISOR_LIVE_SMOKE_SETTINGS_H
#define JOURNAL_SUPERVISOR_LIVE_SMOKE_SETTINGS_H

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static int live_smoke_setting_value(const char *env_file, const char *setting, char *value, size_t capacity) {
    struct stat file_details;
    if (lstat(env_file, &file_details) != 0 || !S_ISREG(file_details.st_mode) || file_details.st_uid != geteuid() || (file_details.st_mode & 0022) != 0) return -1;
    FILE *settings = fopen(env_file, "r");
    if (!settings) return -1;
    char line[4096 + 64];
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

#endif
