<script setup>
// one compaction's round of memories, as its mark keeps it: those still shown, those faded out, those removed since the last round
import {computed} from "vue";
import {useTurnLinks} from "./turnLinks.js";

const props = defineProps({round: {type: Object, default: null}});
const {openRef} = useTurnLinks();

const parts = computed(() =>
    props.round
        ? [
              {label: "Still shown", rows: props.round.shown || [], weight: (m) => `weight ${m.weight_before} to ${m.weight_after}`},
              {label: "Faded out", rows: props.round.faded || [], weight: () => "weight 0"},
              {label: "Removed since the last round", rows: props.round.removed || [], weight: (m) => `weight ${m.weight}`},
          ].filter((part) => part.rows.length)
        : []
);
</script>

<template>
    <div class="memory-round">
        <template v-if="!round">
            <p class="memory-round-missing">This round was not recorded: the mark was written before rounds were kept.</p>
        </template>
        <template v-for="part in parts" :key="part.label">
            <p class="memory-round-label">{{ part.label }}</p>
            <ul class="memory-round-rows">
                <template v-for="memory in part.rows" :key="memory.id">
                    <li class="memory-round-row">
                        <button type="button" class="memory-round-ref" @click.stop="openRef(`memories:${memory.id}`)">Memory {{ memory.id }}</button>
                        <span class="memory-round-weight">{{ part.weight(memory) }}</span>
                        <span class="memory-round-text">{{ memory.text }}</span>
                    </li>
                </template>
            </ul>
        </template>
    </div>
</template>

<style scoped>
.memory-round {
    margin: 0 0 0 20px;
}

/* each list has its label above it */
.memory-round-label {
    margin: 8px 0 2px;
    color: var(--text-4);
    font-size: 10.5px;
}

.memory-round-missing {
    margin: 4px 0 0;
    color: var(--text-2);
    font-size: 12px;
}

.memory-round-rows {
    margin: 0;
    padding: 0;
    list-style: none;
}

.memory-round-row {
    display: flex;
    flex-wrap: wrap;
    gap: 2px 8px;
    padding: 2px 0;
    color: var(--text-2);
    font-size: 12px;
    line-height: 1.45;
    overflow-wrap: anywhere;
}

.memory-round-ref {
    padding: 0;
    border: 0;
    background: none;
    color: var(--accent-text);
    font: inherit;
    cursor: pointer;
}

.memory-round-weight {
    color: var(--text-4);
}

.memory-round-text {
    flex-basis: 100%;
}
</style>
