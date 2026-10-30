<script setup>
import {computed, onMounted, ref} from "vue";
import {api} from "../api/client.js";
import CopyButton from "../kit/CopyButton.vue";

const INSTALLER = "https://github.com/jessegall/agent-journal/releases/download/{tag}/install.sh";
const BACKUP = "docker exec agent-journal-<project> python -m sync_server backup --data /data/team";

const installed = ref("");
const command = computed(() => installed.value && `curl -fsSL ${INSTALLER.replace("{tag}", `v${installed.value}`)} | sh`);

onMounted(async () => (installed.value = (await api.releases()).installed));
</script>

<template>
    <div class="team-block">
        <h2 class="team-section">Set a team server up</h2>
        <p class="team-plain">Run this on the server, which needs Docker; Docker is installed first when the machine has none.</p>
        <template v-if="command">
            <div class="team-command">
                <code>{{ command }}</code>
                <CopyButton :text="command" hint="Copy the command" />
            </div>
        </template>
        <p class="team-plain">It asks for the project and the server's address, or reads them from TEAM_PROJECT and TEAM_ADDRESS.</p>
        <p class="team-plain">It listens on 8443 and 8080 unless TEAM_HTTPS_PORT and TEAM_HTTP_PORT say otherwise.</p>
        <p class="team-plain">At the end it prints the server's URL. Connect to it first: the first journal to connect becomes the team's admin.</p>
        <p class="team-fine">Back up a running server with:</p>
        <div class="team-command">
            <code>{{ BACKUP }}</code>
            <CopyButton :text="BACKUP" hint="Copy the backup command" />
        </div>
    </div>
</template>
