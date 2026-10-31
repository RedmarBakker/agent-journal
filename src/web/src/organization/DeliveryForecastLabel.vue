<script setup>
import {computed} from "vue";
import {formatForecastDay, forecastTone} from "../domain/deliveryForecast.js";

const props = defineProps({forecast: {type: Object, default: null}, sprint: {type: Object, default: null}, plan: {type: Object, required: true}});
const chance = computed(() => props.forecast?.probability_this_sprint);
const tone = computed(() => forecastTone(chance.value));
const likelyFinish = computed(() => props.forecast?.status === "forecast" && props.forecast.p50 && Number.isFinite(chance.value));
const awaiting = computed(() => Number(props.forecast?.awaiting_deploy_count || 0));
const notDeployed = computed(() => props.plan.state === "done" && props.forecast?.execution_complete && props.forecast?.delivery_complete === false);
const missed = computed(() => props.sprint?.state === "closed" && props.forecast?.delivery_complete === false && props.plan.state !== "done");
const delivered = computed(() => props.forecast?.delivery_complete === true);
const latestDelivery = computed(() => props.forecast?.latest_delivery_at ? formatForecastDay(props.forecast.latest_delivery_at) : "");
const capacityLine = computed(() => {
    const forecast = props.forecast;
    if (forecast?.capacity_freshness === "unknown" || !forecast?.capacity_observed_through) return "Capacity not observed";
    const age = forecast.capacity_age_days == null ? "" : ` · ${forecast.capacity_age_days} ${forecast.capacity_age_days === 1 ? "day" : "days"} old`;
    const freshness = forecast.capacity_freshness === "stale" ? "stale" : "fresh";
    return `Capacity through ${formatForecastDay(forecast.capacity_observed_through)}${age} · ${freshness}`;
});
const sampleLine = computed(() => {
    if (!props.forecast) return "";
    const deliveries = Number(props.forecast.delivered_outcomes || 0);
    const model = props.forecast.method_version ? `Forecast model: ${props.forecast.method_version}` : "";
    const calibration = props.forecast.duration_calibration;
    const p50 = calibration?.coverage?.p50?.percent;
    const laterResults = calibration?.status === "measured"
        ? `Compared with ${calibration.observed_count} later task results; the usual range included ${p50 == null ? "not measured" : `${p50}%`}`
        : `Not enough later task results to compare saved estimates (${calibration?.observed_count || 0} finished tasks)`;
    return [`${deliveries} delivered ${deliveries === 1 ? "plan" : "plans"} · Delivery chance uses past sprint results · ${laterResults} · ${capacityLine.value}`, model]
        .filter(Boolean)
        .join(" · ");
});
const waitingLine = computed(() => {
    if (!awaiting.value) return "";
    const count = `${awaiting.value} ${awaiting.value === 1 ? "task" : "tasks"} awaiting deployment`;
    const age = props.forecast?.awaiting_deploy_oldest_age_days;
    if (age == null) return `${count}; age unknown`;
    const days = Math.floor(age);
    return `${count} for ${days < 1 ? "less than a day" : `${days} ${days === 1 ? "day" : "days"}`}`;
});
</script>

<template>
    <div class="delivery-forecast-label" :data-chance-tone="tone" aria-label="Plan delivery forecast">
        <template v-if="notDeployed">
            <p class="delivery-not-deployed">All tasks done, not deployed yet.</p>
        </template>
        <template v-else-if="missed">
            <p class="delivery-missed">Missed Sprint {{ sprint.id }}. It was not delivered by the sprint's end. Decide where it goes next.</p>
        </template>
        <template v-else-if="delivered">
            <p class="delivery-complete">Delivered<span v-if="latestDelivery"> · deployed {{ latestDelivery }}</span>.</p>
        </template>
        <template v-else-if="!sprint">
            <p class="delivery-unscheduled">No sprint. Put this plan in a sprint to see when it is likely to finish.</p>
        </template>
        <template v-else-if="likelyFinish">
            <p class="delivery-likely-finish" :class="`tone-${tone}`">
                Likely finish {{ formatForecastDay(forecast.p50) }} · {{ chance }}% chance in Sprint {{ sprint.id }}
            </p>
            <div v-if="forecast.probability_next_sprint != null && forecast.next_sprint_id != null && forecast.probability_later != null" class="delivery-probability" :aria-label="`${chance}% in Sprint ${sprint.id}, ${forecast.probability_next_sprint}% in Sprint ${forecast.next_sprint_id}, ${forecast.probability_later}% later`">
                <span class="this-sprint" :style="{width: `${chance}%`}" />
                <span class="next-sprint" :style="{width: `${forecast.probability_next_sprint}%`}" />
                <span class="later" :style="{width: `${forecast.probability_later}%`}" />
            </div>
            <p v-if="forecast.probability_next_sprint != null && forecast.next_sprint_id != null" class="delivery-split">
                Sprint {{ forecast.next_sprint_id }} {{ forecast.probability_next_sprint }}% · later {{ forecast.probability_later }}% · carry-over {{ forecast.carry_over }}%
            </p>
            <p v-if="tone === 'risk'" class="delivery-carry-over">Likely to carry over.</p>
        </template>
        <p v-else-if="forecast?.status === 'unknown constraints'" class="delivery-unknown">Forecast constraints are unknown.</p>
        <p v-else class="delivery-unknown">Not enough history yet</p>
        <p v-if="waitingLine" class="delivery-waiting">{{ waitingLine }}</p>
        <p v-if="sampleLine" class="delivery-sample">{{ sampleLine }}<span v-if="forecast.as_of"> · updated {{ formatForecastDay(forecast.as_of) }}</span></p>
    </div>
</template>

<style scoped>
.delivery-forecast-label {
    display: grid;
    gap: 4px;
    color: var(--text-2);
    font-size: 11.5px;
}

.delivery-forecast-label p {
    margin: 0;
}

.delivery-likely-finish {
    font-weight: 550;
}

.tone-good {
    color: var(--success, #56b878);
}

.tone-caution {
    color: var(--warning, #d99325);
}

.tone-risk,
.delivery-not-deployed {
    color: var(--danger, #df6b62);
}

.delivery-unscheduled,
.delivery-carry-over,
.delivery-waiting,
.delivery-split,
.delivery-sample {
    color: var(--text-3);
}

.delivery-missed {
    color: var(--warning, #d99325);
}

.delivery-complete {
    color: var(--success, #56b878);
}

.delivery-probability {
    display: flex;
    height: 4px;
    overflow: hidden;
    border-radius: 999px;
    background: var(--line);
}

.delivery-probability span {
    min-width: 1px;
}

.this-sprint {
    background: var(--accent);
}

.next-sprint {
    background: color-mix(in srgb, var(--accent) 55%, var(--text-3));
}

.later {
    background: var(--text-3);
}

.delivery-split {
    font-variant-numeric: tabular-nums;
}

.delivery-unknown {
    color: var(--text-2);
}
</style>
