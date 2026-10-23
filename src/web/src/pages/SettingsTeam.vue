<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import Btn from "../kit/Btn.vue";
import EmptyState from "../kit/EmptyState.vue";
import {href} from "../route.js";
import TeamConnect from "./TeamConnect.vue";
import "./team.css";

const standing = ref(null);
const outcome = ref("");
const failure = ref("");

async function load() {
    try {
        standing.value = await api.team();
    } catch (e) {
        failure.value = e.message;
    }
}

async function joined(line) {
    outcome.value = line;
    await load();
}

onMounted(load);
</script>

<template>
    <div class="team-pane">
        <template v-if="failure">
            <p class="team-failure">{{ failure }}</p>
        </template>
        <template v-else-if="!standing">
            <EmptyState loading />
        </template>
        <template v-else-if="!standing.joined">
            <TeamConnect :email="standing.email" @joined="joined" />
        </template>
        <template v-else>
            <template v-if="outcome">
                <p class="team-line">{{ outcome }}</p>
            </template>
            <p class="team-plain">{{ standing.line }}. The team's sync, people, machines and worker pool are on the Team page.</p>
            <div>
                <Btn :href="href.page('team')">Open the Team page</Btn>
            </div>
        </template>
    </div>
</template>

<style scoped>
.team-pane {
    display: flex;
    flex-direction: column;
    gap: 18px;
    max-width: 640px;
}
</style>
