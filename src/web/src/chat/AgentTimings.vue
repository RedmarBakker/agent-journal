<script setup>
import {ref} from "vue";
import MenuPanel from "../kit/MenuPanel.vue";
import AgentFact from "./AgentFact.vue";

defineProps({icon: {type: String, required: true}, title: {type: String, required: true}, heading: {type: String, required: true}, average: {type: Number, required: true}, parts: {type: Array, default: () => []}});
const LEAVE_MS = 250;
const button = ref(null);
const shown = ref(false);
const pinned = ref(false);
let leaving = 0;
const enter = () => (clearTimeout(leaving), (shown.value = true));
const leave = () => (clearTimeout(leaving), (leaving = setTimeout(() => !pinned.value && (shown.value = false), LEAVE_MS)));
const toggle = () => (pinned.value = !pinned.value) || (shown.value = false);
const close = () => (pinned.value = shown.value = false);
</script>

<template>
    <span ref="button" class="agent-timings" @mouseenter="enter" @mouseleave="leave">
        <AgentFact :class="['agent-fact', 'agent-count', {open: shown}]" :icon="icon" :title="title" :aria-expanded="shown" @click="toggle">{{ average }} ms</AgentFact>
        <template v-if="shown">
            <MenuPanel :anchor="button" @click.stop @close="close" @mouseenter="enter" @mouseleave="leave">
                <div class="timings-card">
                    <p class="timings-head">{{ heading }}, slowest first</p>
                    <template v-for="part in parts" :key="part.name">
                        <div class="timings-row">
                            <span class="timings-name">{{ part.name }}</span>
                            <b>{{ part.average_ms }} ms</b>
                            <small>{{ part.count }} timed</small>
                        </div>
                    </template>
                    <template v-if="!parts.length">
                        <p class="timings-none">Nothing timed yet</p>
                    </template>
                </div>
            </MenuPanel>
        </template>
    </span>
</template>

<style scoped>
.agent-timings {
    display: inline-flex;
}

.timings-card {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 240px;
    padding: 8px 10px;
    font-size: 12px;
}

.timings-head {
    margin: 0 0 2px;
    color: var(--text-3);
    font-size: 11px;
}

.timings-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
}

.timings-name {
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.timings-row small,
.timings-none {
    color: var(--text-3);
}
</style>
