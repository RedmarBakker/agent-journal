<script setup>
import {computed, ref} from "vue";
import Icon from "../kit/Icon.vue";
import {peek} from "../route.js";

const props = defineProps({
    worker: {type: String, required: true},
    workerId: {type: Number, default: 0},
    messageId: {type: Number, required: true},
    taskId: {type: Number, default: 0},
    text: {type: String, default: ""},
});

const opened = ref(false);
const who = computed(() => (props.workerId ? `Report from worker ${props.workerId}, ${props.worker}` : `Report from ${props.worker}`));
const title = computed(() => (props.taskId ? `${who.value}, on task ${props.taskId}` : who.value));
const openWorker = () => (props.workerId ? peek("workers", props.workerId) : peek("messages", props.messageId));
</script>

<template>
    <div :class="['report-card-wrap', {open: opened}]">
        <button type="button" class="report-card" :aria-expanded="opened" @click="opened = !opened">
            <Icon name="agents" :size="14" />
            <span class="report-card-worker">{{ title }}</span>
        </button>
        <div class="report-card-more">
            <div class="report-card-body">
                <p class="report-card-report">{{ text }}</p>
                <button type="button" class="report-card-open" @click="openWorker">Open the worker</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.report-card-wrap {
    display: flex;
    flex-direction: column;
    max-width: 560px;
    border: 1px solid var(--border-2);
    border-radius: 9px;
    background: var(--raised);
}

.report-card-wrap:hover {
    border-color: var(--accent);
}

.report-card {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border: 0;
    background: none;
    color: var(--text);
    font: inherit;
    font-size: 12px;
    text-align: left;
    cursor: pointer;
}

.report-card-worker {
    font-weight: 500;
}

.report-card-more {
    display: grid;
    grid-template-rows: 0fr;
    opacity: 0;
    transition:
        grid-template-rows var(--move),
        opacity var(--fade);
}

.report-card-wrap.open .report-card-more {
    grid-template-rows: 1fr;
    opacity: 1;
}

.report-card-body {
    min-height: 0;
    padding: 0 10px;
    overflow: hidden;
    font-size: 12px;
}

.report-card-wrap.open .report-card-body {
    padding: 0 10px 8px;
}

.report-card-report {
    margin: 0 0 8px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.report-card-open {
    padding: 0;
    border: 0;
    background: none;
    color: var(--accent);
    font: inherit;
    cursor: pointer;
}
</style>
