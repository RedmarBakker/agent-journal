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
    <div class="report-card-wrap">
        <button type="button" class="report-card" :aria-expanded="opened" @click="opened = !opened">
            <Icon name="agents" :size="14" />
            <span class="report-card-worker">{{ title }}</span>
        </button>
        <template v-if="opened">
            <div class="report-card-body">
                <p class="report-card-report">{{ text }}</p>
                <button type="button" class="report-card-open" @click="openWorker">Open the worker</button>
            </div>
        </template>
    </div>
</template>

<style scoped>
.report-card-wrap {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-width: 560px;
}

.report-card {
    display: flex;
    align-items: center;
    gap: 8px;
    max-width: 480px;
    padding: 6px 10px;
    border: 1px solid var(--border-2);
    border-radius: 9px;
    background: var(--raised);
    color: var(--text);
    font: inherit;
    font-size: 12px;
    text-align: left;
    cursor: pointer;
}

.report-card:hover {
    border-color: var(--accent);
}

.report-card-worker {
    font-weight: 500;
}

.report-card-body {
    padding: 8px 10px;
    border: 1px solid var(--border-2);
    border-radius: 9px;
    font-size: 12px;
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
