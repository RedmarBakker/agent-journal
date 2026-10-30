<script setup>
import {modeOf} from "../domain/plans.js";
import {phaseName} from "../domain/organizationBoard.js";
import {peek} from "../route.js";
import Btn from "../kit/Btn.vue";
import {useScope} from "../composables/scope.js";
import DeliveryForecastLabel from "./DeliveryForecastLabel.vue";
import {pointLabel} from "../domain/taskSizing.js";

const props = defineProps({plan: {type: Object, required: true}, forecast: {type: Object, default: null}, compact: Boolean});
const scope = useScope();
const progress = () => `${props.plan.done || 0} of ${(props.plan.tasks || []).length} done`;
const points = () => pointLabel(props.plan);
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
    <article :class="['organization-plan-card', {compact}]" :data-plan-id="plan.id" :data-plan-state="plan.state || null">
        <button type="button" class="organization-plan-title" :aria-label="`Open plan ${plan.title}`" @click="openPlan">{{ plan.title }}</button>
        <span class="organization-plan-details">
            <span>{{ modeOf(plan) }}</span>
            <span v-if="!compact">Phase: {{ shownPhase() }}</span>
            <span>{{ progress() }} · {{ points() }}</span>
        </span>
        <span v-if="plan.waits_on" class="organization-plan-wait">Waits on: {{ plan.waits_on }}</span>
        <DeliveryForecastLabel :forecast="forecast" :sprint="forecast?.sprint || null" :plan="plan" />
        <template v-if="!compact">
            <span class="organization-plan-cost">Estimated API cost: {{ estimatedApiCost() }}</span>
            <span v-if="plan.cost_cap_usd != null" class="organization-plan-cap">Cost cap: {{ costCap() }}</span>
            <span v-if="plan.plan_agent_state" class="organization-plan-agent">Plan agent: {{ plan.plan_agent_state }}</span>
            <Btn v-if="plan.chat" small :href="scope.api.page(plan.chat)" :title="`Plan agent in ${plan.chat}`">Open its chat</Btn>
        </template>
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

.organization-plan-card.compact {
    display: grid;
    grid-template-columns: minmax(145px, 1.2fr) minmax(180px, 1.35fr) minmax(120px, 0.9fr) minmax(200px, 1.45fr);
    align-items: center;
    gap: 8px 12px;
    padding: 9px 12px;
    border: 0;
    border-bottom: 1px solid var(--line);
    border-radius: 0;
    background: transparent;
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

.organization-plan-card.compact .organization-plan-title {
    min-width: 0;
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

@media (max-width: 900px) {
    .organization-plan-card.compact {
        grid-template-columns: minmax(130px, 1fr) minmax(150px, 1fr);
    }
}
</style>
