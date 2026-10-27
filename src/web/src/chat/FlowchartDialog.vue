<script setup>
import {computed} from "vue";
import Dialog from "../kit/Dialog.vue";
import {layoutOf} from "../domain/flowchart.js";

const props = defineProps({title: {type: String, required: true}, edges: {type: Array, required: true}});
const emit = defineEmits(["close"]);
const chart = computed(() => layoutOf(props.edges));
</script>

<template>
    <Dialog :title="title" large @close="emit('close')">
        <svg class="flowchart" :viewBox="`0 0 ${chart.width} ${chart.height}`" role="img" :aria-label="title">
            <defs>
                <marker id="flowchart-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
                    <path d="M0 0L10 5L0 10z" />
                </marker>
            </defs>
            <template v-for="arrow in chart.arrows" :key="`${arrow.from}>${arrow.to}`">
                <line class="flowchart-arrow" :x1="arrow.x1" :y1="arrow.y1" :x2="arrow.x2" :y2="arrow.y2" marker-end="url(#flowchart-head)" />
                <template v-if="arrow.label">
                    <text class="flowchart-label" :x="(arrow.x1 + arrow.x2) / 2 + 6" :y="(arrow.y1 + arrow.y2) / 2">{{ arrow.label }}</text>
                </template>
            </template>
            <template v-for="node in chart.nodes" :key="node.name">
                <g class="flowchart-node">
                    <rect :x="node.x" :y="node.y" :width="chart.size.width" :height="chart.size.height" rx="8" />
                    <text :x="node.x + chart.size.width / 2" :y="node.y + chart.size.height / 2">{{ node.name }}</text>
                </g>
            </template>
        </svg>
    </Dialog>
</template>

<style scoped>
.flowchart {
    display: block;
    width: 100%;
    height: auto;
}

.flowchart-arrow {
    stroke: var(--text-3);
    stroke-width: 1.5;
}

#flowchart-head {
    fill: var(--text-3);
}

.flowchart-node rect {
    fill: var(--raised);
    stroke: var(--border-3);
}

.flowchart-node text {
    fill: var(--text);
    font-size: 13px;
    text-anchor: middle;
    dominant-baseline: middle;
}

.flowchart-label {
    fill: var(--text-3);
    font-size: 11px;
}
</style>
