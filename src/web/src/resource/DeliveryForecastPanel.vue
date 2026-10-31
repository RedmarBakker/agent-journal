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
const criticalPath = computed(() => props.forecast?.critical_path || null);
const durationRanges = computed(() => props.forecast?.duration_ranges || null);
const durationCalibration = computed(() => props.forecast?.duration_calibration || null);
const comparableExamples = computed(() => (durationRanges.value?.tasks || []).flatMap((task) => task.comparable_examples || []));
const learnedRangeSummary = computed(() => {
    if (!durationRanges.value) return "";
    if (durationRanges.value.status !== "forecast") return "Learned ranges: not enough history yet.";
    const coverage = durationCalibration.value?.coverage?.raw_p85;
    if (coverage?.percent == null) return "Ranges come from past delivered tasks; they are advice only. Not enough finished tasks to check how often they fit yet.";
    return `Ranges come from past delivered tasks; they are advice only. The wider range included ${coverage.percent}% of ${coverage.observed} finished task times.`;
});
const sizingBias = computed(() => durationCalibration.value?.sizing_bias || {});
const biasStages = computed(() => [
    {key: "execution_cycle"},
    {key: "delivery_delay"},
].filter(({key}) => sizingBias.value[key]));
const durationHistoryLine = computed(() => {
    const history = durationRanges.value?.history;
    if (!history) return "History age not available";
    if (history.freshness === "unknown") return "No finished task times recorded";
    const age = `${history.age_days} ${history.age_days === 1 ? "day" : "days"} old`;
    const through = history.observed_through ? ` · last observed ${formatForecastDay(history.observed_through)}` : "";
    return `${history.completed_observations} finished task times${through} · ${age} · ${history.freshness}`;
});
const calibrationSummary = computed(() => {
    const calibration = durationCalibration.value;
    if (!calibration || calibration.status !== "measured") {
        return `Not enough later task results to compare saved estimates (${calibration?.observed_count || 0} finished tasks from ${calibration?.prediction_count || 0} saved estimates).`;
    }
    const reference = calibration.coverage?.empirical_p50?.percent == null
        ? ""
        : ` Past task times alone included ${calibration.coverage.empirical_p50.percent}% in the usual range and ${calibration.coverage?.empirical_p85?.percent ?? "not measured"}% in the wider range.`;
    return `Compared with ${calibration.observed_count} later task results from ${calibration.prediction_count} saved estimates, the usual range included ${calibration.coverage?.p50?.percent ?? "not measured"}% and the wider range included ${calibration.coverage?.raw_p85?.percent ?? "not measured"}%.${reference}`;
});
const formatDuration = (seconds) => seconds >= 86400 ? `${(seconds / 86400).toFixed(1)} days`
    : seconds >= 3600 ? `${(seconds / 3600).toFixed(1)} hours` : `${Math.round(seconds / 60)} minutes`;
const criticalPathLine = computed(() => {
    const path = criticalPath.value?.critical_path_task_ids || [];
    if (!path.length) return "";
    const finish = criticalPath.value.p50_finish ? ` · P50 finish ${formatForecastDay(criticalPath.value.p50_finish)}` : "";
    return `Critical path: ${path.map((id) => "#" + id).join(" → ")}${finish}`;
});
const criticalTasks = computed(() => (criticalPath.value?.critical_task_ids || []).map((id) => "#" + id).join(", "));
const independentTasks = computed(() => (criticalPath.value?.independent_groups || []).flat().map((id) => "task #" + id).join(", "));
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
                <p class="sprint-end">Sprint ends {{ sprintEnd(sprint) }}</p>
                <div v-if="expected" class="forecast-bands" aria-label="Chance of delivery by sprint">
                    <div><span>Sprint {{ sprint.id }} (its sprint, {{ sprintRange(sprint) }})</span><strong>{{ forecast.probability_this_sprint }}%</strong><progress :value="forecast.probability_this_sprint" max="100" /></div>
                    <div v-if="forecast.probability_next_sprint != null && forecast.next_sprint_id != null"><span>Sprint {{ forecast.next_sprint_id }}</span><strong>{{ forecast.probability_next_sprint }}%</strong><progress :value="forecast.probability_next_sprint" max="100" /></div>
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
                <div><dt>Updated</dt><dd>{{ forecast?.as_of ? formatForecastDay(forecast.as_of) : "Not estimated" }}</dd></div>
                <div><dt>Delivery chance</dt><dd>Based on past sprint results.<span v-if="forecast?.network_forecast?.comparison?.selection === 'none'"> The shared dependency estimate is shown for comparison only.</span></dd></div>
                <div v-if="durationRanges"><dt>Task-time ranges</dt><dd>{{ learnedRangeSummary }} These ranges do not change the delivery chance. {{ durationHistoryLine }}</dd></div>
                <div v-if="durationCalibration"><dt>Saved estimates and later results</dt><dd>{{ calibrationSummary }}</dd></div>
                <div v-for="stage in biasStages" :key="stage.key"><dt>{{ stage.key === 'execution_cycle' ? 'Work-time estimate' : 'Delivery-time estimate' }}</dt><dd><template v-if="sizingBias[stage.key].status === 'measured'">Across {{ sizingBias[stage.key].observed }} finished tasks, {{ stage.key === 'execution_cycle' ? 'work' : 'time from finishing work to delivery' }} took {{ Number(sizingBias[stage.key].actual_to_predicted_p50_ratio).toFixed(1) }} times as long as estimated.</template><template v-else>Not enough finished tasks to compare {{ stage.key === 'execution_cycle' ? 'work-time' : 'delivery-time' }} estimates ({{ sizingBias[stage.key].observed }} of {{ durationCalibration.minimum_calibration_samples }}).</template></dd></div>
            </dl>
            <section v-if="comparableExamples.length" class="duration-examples" aria-label="Similar finished tasks">
                <h4>Similar finished tasks</h4>
                <ul>
                    <li v-for="example in comparableExamples" :key="example.task_id">
                        Task #{{ example.task_id }} · original estimate {{ example.original_size_points }} points · finished size {{ example.execution_size_points }} points · work took {{ formatDuration(example.execution_seconds) }} · delivery took {{ formatDuration(example.delivery_seconds) }} after work finished
                    </li>
                </ul>
            </section>
            <p v-else-if="durationRanges" class="forecast-unknown">No similar finished tasks yet.</p>
            <section v-if="criticalPath && criticalPath.status !== 'empty'" class="critical-path-read" aria-label="Critical path">
                <h4>Critical path</h4>
                <p v-if="criticalPath.status === 'structural'">The dependency graph is structural. Start, finish and slack are unknown.</p>
                <template v-else>
                    <p>{{ criticalPathLine }}</p>
                    <p v-if="criticalTasks">Critical tasks: {{ criticalTasks }}</p>
                    <ul v-if="criticalPath.tasks?.length">
                        <li v-for="task in criticalPath.tasks" :key="task.task_id">
                            Task #{{ task.task_id }} · P50 {{ task.p50_duration_days }} days · starts {{ formatForecastDay(task.earliest_start) }} · finishes {{ formatForecastDay(task.earliest_finish) }} · {{ task.slack_days }} {{ task.slack_days === 1 ? "day" : "days" }} of slack
                        </li>
                    </ul>
                </template>
                <p v-if="independentTasks">Independent work: {{ independentTasks }}</p>
                <ul v-if="criticalPath.external_conditions?.length">
                    <li v-for="condition in criticalPath.external_conditions" :key="`${condition.task_id}:${condition.prerequisite_id}:${condition.kind}`">
                        Cross-plan {{ condition.kind === "delivery_gate" ? "delivery gate" : "prerequisite" }} from task #{{ condition.task_id }} to task #{{ condition.prerequisite_id }} is {{ condition.status }}.
                    </li>
                </ul>
            </section>
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

.duration-examples h4,
.duration-examples ul {
    margin: 0;
}

.duration-examples ul {
    padding-left: 20px;
    color: var(--text-2);
    font-size: 12px;
}

.critical-path-read {
    display: grid;
    gap: 6px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    color: var(--text-2);
    font-size: 12px;
}

.critical-path-read h4,
.critical-path-read p,
.critical-path-read ul {
    margin: 0;
}

.critical-path-read ul {
    display: grid;
    gap: 4px;
    padding-left: 18px;
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
