<script setup>
import {modeOf} from "../domain/plans.js";
import {phaseName} from "../domain/organizationBoard.js";
import {peek} from "../route.js";
import Btn from "../kit/Btn.vue";
import {useScope} from "../composables/scope.js";

const props = defineProps({plan: {type: Object, required: true}});
const scope = useScope();
const progress = () => `${props.plan.done || 0} of ${(props.plan.tasks || []).length} done`;
const estimatedApiCost = () => {
    if (props.plan.estimated_api_cost_usd == null) return "Not reported";
    const amount = `$${Number(props.plan.estimated_api_cost_usd).toFixed(2)}`;
    return props.plan.estimated_api_cost_status === "stale" ? `Stale (${amount})` : amount;
};
const costCap = () => Number(props.plan.cost_cap_usd) > 0 ? `$${Number(props.plan.cost_cap_usd).toFixed(2)}` : "No cap";
const shownPhase = () => props.plan.phase_name || phaseName(props.plan.phase);
const openPlan = () => peek("plans", props.plan.id);
</script>

<template>
    <article class="organization-plan-card" :data-plan-id="plan.id" :data-plan-state="plan.state || null">
        <button type="button" class="organization-plan-title" :aria-label="`Open plan ${plan.title}`" @click="openPlan">{{ plan.title }}</button>
        <span class="organization-plan-details">
            <span>{{ modeOf(plan) }}</span>
            <span>Phase: {{ shownPhase() }}</span>
            <span>{{ progress() }}</span>
        </span>
        <span class="organization-plan-cost">Estimated API cost: {{ estimatedApiCost() }}</span>
        <span v-if="plan.cost_cap_usd != null" class="organization-plan-cap">Cost cap: {{ costCap() }}</span>
        <span v-if="plan.plan_agent_state" class="organization-plan-agent">Plan agent: {{ plan.plan_agent_state }}</span>
        <span v-if="plan.waits_on" class="organization-plan-wait">Waits on: {{ plan.waits_on }}</span>
        <Btn v-if="plan.chat" small :href="scope.api.page(plan.chat)" :title="`Plan agent in ${plan.chat}`">Open its chat</Btn>
    </article>
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
    font: inherit;
}

.organization-plan-card:hover,
.organization-plan-card:focus-within {
    border-color: var(--accent);
}

.organization-plan-title {
    width: fit-content;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--text);
    text-align: left;
    font: inherit;
    font-weight: 600;
    cursor: pointer;
}

.organization-plan-title:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
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

.organization-plan-cost {
    color: var(--text-2);
    font-size: 12px;
}

.organization-plan-cap,
.organization-plan-agent {
    color: var(--text-2);
    font-size: 12px;
}
</style>
