<script setup>
import {modeOf} from "../domain/plans.js";
import {peek} from "../route.js";

const props = defineProps({plan: {type: Object, required: true}});
const progress = () => `${props.plan.done || 0} of ${(props.plan.tasks || []).length} done`;
const open = () => peek("plans", props.plan.id);
</script>

<template>
    <button type="button" class="organization-plan-card" :data-plan-id="plan.id" :aria-label="`Open plan ${plan.title}`" @click="open">
        <span class="organization-plan-title">{{ plan.title }}</span>
        <span class="organization-plan-details">
            <span>{{ modeOf(plan) }}</span>
            <span>{{ progress() }}</span>
        </span>
        <span v-if="plan.waits_on" class="organization-plan-wait">Waits on: {{ plan.waits_on }}</span>
    </button>
</template>

<style scoped>
.organization-plan-card {
    display: flex;
    flex-direction: column;
    gap: 7px;
    width: 100%;
    padding: 11px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg-2, var(--bg));
    color: var(--text);
    text-align: left;
    font: inherit;
    cursor: pointer;
}

.organization-plan-card:hover {
    border-color: var(--accent);
}

.organization-plan-title {
    font-weight: 600;
}

.organization-plan-details {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
    color: var(--text-2);
    font-size: 12px;
}

.organization-plan-wait {
    color: var(--text-3);
    font-size: 12px;
}
</style>
