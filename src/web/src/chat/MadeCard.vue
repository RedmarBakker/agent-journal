<script setup>
import Icon from "../kit/Icon.vue";
import {meta} from "../domain/tables.js";
import {peek} from "../route.js";

defineProps({made: {type: Object, required: true}});
</script>

<template>
    <button type="button" class="thread-made" :title="`Open the ${meta(made.table).title.toLowerCase()}`" @click="peek(made.table, made.id)">
        <Icon :name="meta(made.table).icon" :size="14" />
        <span class="thread-made-title">{{ made.title }}</span>
        <template v-if="made.status">
            <span :class="['thread-made-status', {writing: made.status === 'Being written'}]">{{ made.status }}</span>
        </template>
    </button>
</template>

<style scoped>
.thread-made {
    display: flex;
    align-items: center;
    gap: 8px;
    max-width: 100%;
    padding: 2px 0;
    border: 0;
    background: none;
    color: var(--text-3);
    font: inherit;
    font-size: 12px;
    text-align: left;
    cursor: pointer;
}

.thread-made:hover {
    color: var(--text);
}

.thread-made-status {
    flex: none;
    color: var(--text-4);
    font-size: 11px;
    transition: color 0.3s;
}

.thread-made-status.writing {
    color: var(--accent-text);
}

.thread-made-title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>
