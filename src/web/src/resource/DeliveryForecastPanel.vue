<script setup>
import {computed} from "vue";
import {formatForecastDay, sprintEnd, sprintRange} from "../domain/deliveryForecast.js";

const props = defineProps({forecast: {type: Object, default: null}, sprint: {type: Object, default: null}, plan: {type: Object, required: true}, loading: Boolean});
const expected = computed(() => props.forecast?.status === "forecast");
const currentScope = computed(() => props.forecast?.current_scope || props.forecast?.scope || {});
const delivered = computed(() => props.forecast?.delivered_scope?.length ?? currentScope.value.delivered_count ?? 0);
const taskCount = computed(() => currentScope.value.task_count ?? 0);
const remainingPoints = computed(() => currentScope.value.remaining_points);
const unknownSizes = computed(() => currentScope.value.unknown_size_tasks || 0);
const deliveredTasks = computed(() => props.forecast?.delivered_scope || []);
const currentTasks = computed(() => currentScope.value.task_ids || []);
const deliveredLine = computed(() => deliveredTasks.value.length ? " · Delivered task " + deliveredTasks.value.map((id) => "#" + id).join(", ") : "");
const currentLine = computed(() => currentTasks.value.length ? " · Current tasks " + currentTasks.value.map((id) => "#" + id).join(", ") : "");
const waitingCount = computed(() => props.forecast?.awaiting_deploy_count || 0);
const waitingAge = computed(() => props.forecast?.awaiting_deploy_oldest_age_days);
const waitingLine = computed(() => {
    if (!waitingCount.value) return "No tasks awaiting deployment";
    const count = `${waitingCount.value} ${waitingCount.value === 1 ? "task" : "tasks"} awaiting deployment`;
    if (waitingAge.value == null) return `${count}; age unknown`;
    const age = Math.floor(waitingAge.value);
    return `${count} for ${age < 1 ? "less than a day" : `${age} ${age === 1 ? "day" : "days"}`}`;
});
const historyLine = computed(() => {
    const deliveries = props.forecast?.delivered_outcomes;
    const capacity = props.forecast?.observed_capacity_days;
    return `${deliveries ?? 0} comparable ${deliveries === 1 ? "delivery" : "deliveries"} · ${capacity ?? 0} ${capacity === 1 ? "day" : "days"} of observed capacity`;
});
const capacityLine = computed(() => {
    const through = props.forecast?.capacity_observed_through;
    const age = props.forecast?.capacity_age_days;
    if (!through) return "Capacity not observed";
    const ageLine = age == null ? "" : ` · ${age} ${age === 1 ? "day" : "days"} old`;
    const freshness = props.forecast?.capacity_freshness === "stale" ? " · stale" : "";
    return `Capacity last observed ${formatForecastDay(through)}${ageLine}${freshness}`;
});
const criteria = computed(() => props.forecast?.domain_criteria || []);
const missing = computed(() => props.forecast?.missing_evidence || []);
const missingCriteria = computed(() => props.forecast?.missing_criteria || []);
</script>

<template>
    <section class="delivery-forecast-panel" aria-label="Delivery forecast">
        <header><h3>Delivery forecast</h3></header>
        <p v-if="loading" class="forecast-reading">Reading delivery forecast</p>
        <template v-else>
            <p v-if="plan.state === 'done' && forecast?.execution_complete && forecast?.delivery_complete === false" class="delivery-not-deployed">
                All tasks done, not deployed yet. It counts as delivered once it is deployed.
            </p>
            <p v-if="!sprint" class="forecast-unknown">No sprint. Put this plan in a sprint to see when it is likely to finish.</p>
            <template v-else>
                <p v-if="expected && forecast.p50" class="likely-finish">Likely finish <strong>{{ formatForecastDay(forecast.p50) }}</strong></p>
                <p v-if="expected && forecast.p85" class="almost-certain">Almost certain by {{ formatForecastDay(forecast.p85) }}</p>
                <p v-else-if="forecast?.status === 'unknown constraints'" class="forecast-unknown">Forecast constraints are unknown. No date or percentage is shown.</p>
                <p v-else-if="!expected" class="forecast-unknown">Not enough history yet. No date or percentage is shown.</p>
                <p class="sprint-end">Sprint {{ sprint.id }} · {{ sprintRange(sprint) }} · ends {{ sprintEnd(sprint) }}</p>
                <div v-if="expected" class="forecast-bands" aria-label="Chance of delivery by sprint">
                    <div><span>Sprint {{ sprint.id }} (this sprint)</span><strong>{{ forecast.probability_this_sprint }}%</strong><progress :value="forecast.probability_this_sprint" max="100" /></div>
                    <div><span>Next sprint</span><strong>{{ forecast.probability_next_sprint }}%</strong><progress :value="forecast.probability_next_sprint" max="100" /></div>
                    <div><span>Later</span><strong>{{ forecast.probability_later }}%</strong><progress :value="forecast.probability_later" max="100" /></div>
                    <p>Chance it carries over: {{ forecast.carry_over }}%</p>
                </div>
            </template>
            <dl class="forecast-facts">
                <div><dt>Scope</dt><dd>{{ delivered }} of {{ taskCount }} tasks delivered{{ deliveredLine }}{{ currentLine }}<span v-if="remainingPoints != null"> · {{ remainingPoints }} points remain</span><span v-else-if="unknownSizes"> · {{ unknownSizes }} {{ unknownSizes === 1 ? "task has" : "tasks have" }} no size</span></dd></div>
                <div><dt>Delivery backlog</dt><dd>{{ waitingLine }}</dd></div>
                <div v-for="criterion in criteria" :key="`${criterion.domain}:${criterion.version}`"><dt>{{ criterion.domain }} done means</dt><dd>{{ criterion.criterion }}</dd></div>
                <div v-if="!criteria.length"><dt>Done criteria</dt><dd>{{ missingCriteria[0] || missing[0] || "Definition of done not set" }}</dd></div>
                <div><dt>History</dt><dd>{{ historyLine }}</dd></div>
                <div><dt>Capacity</dt><dd>{{ capacityLine }}</dd></div>
                <div><dt>Method and update</dt><dd>{{ forecast?.method_version || "Not estimated" }}<span v-if="forecast?.as_of"> · {{ formatForecastDay(forecast.as_of) }}</span></dd></div>
            </dl>
            <p v-if="missing.length" class="missing-evidence">Not included: {{ missing.join(", ") }}.</p>
        </template>
    </section>
</template>

<style scoped>
.delivery-forecast-panel {
    display: grid;
    gap: 12px;
    margin: 14px 0;
    padding: 14px;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: var(--bg-2, var(--raised));
}

.delivery-forecast-panel p,
.delivery-forecast-panel h3 {
    margin: 0;
}

.delivery-forecast-panel h3 {
    font-size: 15px;
}

.likely-finish {
    font-size: 14px;
}

.almost-certain,
.sprint-end,
.forecast-unknown,
.forecast-reading,
.missing-evidence {
    color: var(--text-3);
    font-size: 12px;
}

.delivery-not-deployed {
    color: var(--warning, #d99325);
    font-size: 12px;
}

.forecast-bands {
    display: grid;
    gap: 7px;
}

.forecast-bands div {
    display: grid;
    grid-template-columns: minmax(120px, 1fr) 42px minmax(80px, 2fr);
    align-items: center;
    gap: 10px;
    color: var(--text-2);
    font-size: 12px;
}

.forecast-bands strong {
    color: var(--text);
    font-variant-numeric: tabular-nums;
}

.forecast-bands progress {
    width: 100%;
    height: 7px;
    accent-color: var(--accent);
}

.forecast-bands p {
    color: var(--text-3);
    font-size: 12px;
}

.forecast-facts {
    display: grid;
    gap: 7px;
    margin: 0;
}

.forecast-facts div {
    display: grid;
    grid-template-columns: minmax(100px, 0.35fr) minmax(0, 1fr);
    gap: 8px;
    font-size: 12px;
}

.forecast-facts dt {
    color: var(--text-3);
}

.forecast-facts dd {
    margin: 0;
    color: var(--text-2);
}

@media (max-width: 650px) {
    .forecast-bands div {
        grid-template-columns: 1fr auto;
    }

    .forecast-bands progress {
        grid-column: 1 / -1;
    }

    .forecast-facts div {
        grid-template-columns: 1fr;
        gap: 2px;
    }
}
</style>
