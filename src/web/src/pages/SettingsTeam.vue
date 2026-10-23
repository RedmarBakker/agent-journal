<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import Btn from "../kit/Btn.vue";
import EmptyState from "../kit/EmptyState.vue";
import StateDot from "../kit/StateDot.vue";
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
                <p class="team-joined">
                    <StateDot state="done" />
                    <span>{{ outcome }}</span>
                </p>
            </template>
            <div class="team-where">
                <p class="team-plain">{{ standing.line }}. The team's sync, its people, your password, the worker pool, the machines and the Team chat are on the Team page.</p>
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

.team-joined {
    display: flex;
    align-items: flex-start;
    gap: 9px;
    margin: 0;
    padding: 10px 14px;
    border: 1px solid color-mix(in oklab, var(--tone-good) 40%, var(--border));
    border-radius: 10px;
}

.team-joined :deep(.state-dot) {
    margin-top: 6px;
}

.team-where {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px 16px;
}

.team-where p {
    flex: 1 1 280px;
}
</style>
