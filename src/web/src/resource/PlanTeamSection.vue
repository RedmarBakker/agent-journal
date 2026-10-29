<script setup>
import {ref, watch} from "vue";
import {useScope} from "../composables/scope.js";

const props = defineProps({
    plan: {type: Object, required: true},
    readOnly: Boolean,
    initial: {type: Object, default: null},
});
const scope = useScope();
const team = ref({domains: [], seat_cap: 0, estimated_api_cost_usd: null, cost_cap_usd: 0});
const loading = ref(false);
const error = ref("");

function usd(value) {
    return `$${Number(value).toFixed(2)}`;
}

function state(seat) {
    if (seat.state === "waiting") return `Waiting in a shared Role's queue${seat.task_id ? ` for task ${seat.task_id}` : ""}`;
    if (seat.state === "working") return seat.task_id ? `Working on task ${seat.task_id}` : "Working";
    return "Idle";
}

watch(() => props.plan.id, async (id) => {
    if (props.initial) {
        team.value = props.initial;
        loading.value = false;
        return;
    }
    if (props.readOnly) return;
    loading.value = true;
    error.value = "";
    try {
        team.value = await scope.api.planTeam(id);
    } catch (e) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
}, {immediate: true});
</script>

<template>
    <section class="plan-team" aria-label="Team working on this plan">
        <h3>Team</h3>
        <p v-if="error" class="plan-team-error" role="alert">{{ error }}</p>
        <p v-else-if="loading && !team.domains.length" class="plan-team-note">Loading team…</p>
        <template v-else>
            <dl class="plan-team-caps">
                <div><dt>Shared seat cap across plans</dt><dd>{{ team.seat_cap > 0 ? `${team.seat_cap} seats at once` : "No cap" }}</dd></div>
                <div><dt>Estimated API cost cap</dt><dd>{{ team.cost_cap_usd > 0 ? usd(team.cost_cap_usd) : "No cap" }}</dd></div>
                <div><dt>Recorded plan estimate</dt><dd>{{ team.estimated_api_cost_usd == null ? "Not reported" : usd(team.estimated_api_cost_usd) }}</dd></div>
            </dl>
            <p v-if="!team.domains.length" class="plan-team-note">No Role seats have been staffed yet.</p>
            <div v-for="domain in team.domains" :key="domain.id" class="plan-team-domain">
                <h4>{{ domain.title }}</h4>
                <article v-for="seat in domain.seats" :key="seat.id" class="plan-team-seat">
                    <div class="plan-team-seat-heading">
                        <strong>{{ seat.title }}</strong>
                        <span class="plan-team-state">{{ state(seat) }}</span>
                    </div>
                    <p v-if="seat.task_title" class="plan-team-task">{{ seat.task_title }}</p>
                    <p v-else-if="seat.task_id" class="plan-team-task">Task {{ seat.task_id }}</p>
                    <p class="plan-team-cost">Estimated API cost: {{ seat.estimated_api_cost_usd == null ? "Not measured" : usd(seat.estimated_api_cost_usd) }}</p>
                </article>
            </div>
        </template>
    </section>
</template>

<style scoped>
.plan-team {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 8px 0 16px;
    padding: 12px 14px;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: var(--panel);
}

.plan-team h3,
.plan-team h4,
.plan-team p,
.plan-team-caps {
    margin: 0;
}

.plan-team h3 {
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.plan-team-note,
.plan-team-error,
.plan-team-caps,
.plan-team-state,
.plan-team-task,
.plan-team-cost {
    color: var(--text-3);
    font-size: 12px;
}

.plan-team-error {
    color: var(--danger);
}

.plan-team-caps {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 18px;
}

.plan-team-caps div {
    display: flex;
    gap: 5px;
}

.plan-team-caps dd {
    margin: 0;
    color: var(--text-2);
}

.plan-team-domain {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.plan-team h4 {
    color: var(--text-2);
    font-size: 12px;
    font-weight: 600;
}

.plan-team-seat {
    display: flex;
    flex-direction: column;
    gap: 3px;
    padding: 8px 10px;
    border: 1px solid var(--border);
    border-radius: 7px;
    background: var(--panel);
}

.plan-team-seat-heading {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 4px 12px;
    color: var(--text);
    font-size: 12px;
}

.plan-team-task {
    color: var(--text-2);
}
</style>
