<script setup>
import {computed, ref, watch} from "vue";

const props = defineProps({
    items: {type: Array, default: () => []},
    pageSize: {type: Number, required: true},
    label: {type: String, required: true},
    noun: {type: String, required: true},
});

const page = ref(0);
const pageCount = computed(() => Math.ceil(props.items.length / props.pageSize));
const first = computed(() => page.value * props.pageSize + 1);
const last = computed(() => Math.min((page.value + 1) * props.pageSize, props.items.length));
const visible = computed(() => props.items.slice(page.value * props.pageSize, (page.value + 1) * props.pageSize));

watch(() => props.items, () => (page.value = 0));

function previous() {
    page.value = Math.max(0, page.value - 1);
}

function next() {
    page.value = Math.min(pageCount.value - 1, page.value + 1);
}
</script>

<template>
    <div class="paged-cards">
        <slot :items="visible" />
        <nav v-if="pageCount > 1" class="paged-cards-controls" :aria-label="`${label} pages`">
            <span aria-live="polite">Showing {{ first }}–{{ last }} of {{ items.length }} {{ noun }}</span>
            <button type="button" :aria-label="`Previous ${label} page`" :disabled="page === 0" @click="previous">Previous</button>
            <button type="button" :aria-label="`Next ${label} page`" :disabled="page >= pageCount - 1" @click="next">Next</button>
        </nav>
    </div>
</template>

<style scoped>
.paged-cards {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
}

.paged-cards-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px 10px;
    color: var(--text-3);
    font-size: 11px;
}

.paged-cards-controls span {
    margin-right: auto;
    font-variant-numeric: tabular-nums;
}

.paged-cards-controls button {
    min-height: 28px;
    padding: 3px 8px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text-2);
    font: inherit;
    cursor: pointer;
}

.paged-cards-controls button:disabled {
    opacity: 0.5;
    cursor: default;
}

.paged-cards-controls button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
}
</style>
