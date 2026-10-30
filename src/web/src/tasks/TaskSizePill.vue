<script setup>
import {computed} from "vue";

const props = defineProps({task: {type: Object, required: true}});
const known = computed(() => Number.isInteger(props.task.size) && props.task.size > 0);
</script>

<template>
    <span v-if="known" class="task-size" :aria-label="`${task.size} story points`">{{ task.size }} points</span>
    <span v-else class="task-size unknown" data-size-unknown>Size unknown</span>
</template>

<style scoped>
.task-size {
    flex: none;
    padding: 2px 6px;
    border: 1px solid var(--border-2);
    border-radius: 999px;
    color: var(--text-2);
    font-size: 10.5px;
    line-height: 1.3;
    white-space: nowrap;
}

.task-size.unknown {
    border-color: color-mix(in srgb, var(--warning, #d99325) 55%, var(--border));
    color: var(--warning, #d99325);
}
</style>
