<script setup>
import Icon from "../kit/Icon.vue";
import {clock} from "../format/time.js";
import {peek} from "../route.js";

const props = defineProps({worker: {type: String, required: true}, workerId: {type: Number, default: 0}, messageId: {type: Number, required: true}, task: {type: Object, default: null}, time: {type: Number, default: 0}});

const open = () => (props.workerId ? peek("workers", props.workerId) : peek("messages", props.messageId));
</script>

<template>
    <button type="button" class="report-card" :title="`Open the report of ${worker}`" @click="open">
        <Icon name="agents" :size="14" />
        <span class="report-card-text">
            <span class="report-card-worker">{{ worker }}</span>
            <template v-if="task">
                <span class="report-card-task">task {{ task.id }}, {{ task.title }}</span>
            </template>
        </span>
        <span class="report-card-time">{{ clock(time) }}</span>
    </button>
</template>

<style scoped>
.report-card {
    display: flex;
    align-items: center;
    gap: 8px;
    max-width: 380px;
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

.report-card-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.report-card-worker {
    font-weight: 500;
}

.report-card-task {
    overflow: hidden;
    color: var(--muted);
    text-overflow: ellipsis;
    white-space: nowrap;
}

.report-card-time {
    margin-left: auto;
    color: var(--muted);
    font-size: 11px;
}
</style>
