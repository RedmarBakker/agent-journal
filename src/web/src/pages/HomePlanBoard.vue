<script setup>
import {computed, onMounted, ref} from "vue";
import {api} from "../api/client.js";
import EmptyState from "../kit/EmptyState.vue";
import OrganizationPlanBoard from "../organization/OrganizationPlanBoard.vue";
import {sprintPointLabel} from "../domain/taskSizing.js";

const props = defineProps({view: {type: String, default: "plans"}});
const organization = ref(null);
const loading = ref(true);
const problem = ref("");
const filter = ref("all");
const plans = computed(() => organization.value?.plans || []);
const scheduledPlans = computed(() => organization.value?.scheduled_plans || []);
const sprintForecasts = computed(() => organization.value?.sprint_forecasts || []);
const visiblePlans = computed(() => {
    if (filter.value === "all") return plans.value;
    if (filter.value === "scheduled") return [];
    return plans.value.filter((plan) => {
        if (filter.value === "running") return plan.plan_agent_state === "running";
        if (filter.value === "paused") return plan.state === "paused";
        return Boolean(plan.waiting_on_you);
    });
});
const showScheduled = computed(() => filter.value === "all" || filter.value === "scheduled");
const emptyTitle = computed(() => ({running: "No running plans", paused: "No paused plans", waiting: "No plans are waiting on you", scheduled: "No scheduled plans"}[filter.value] || "No plans to show"));

const scheduleNames = {daily: "Daily", weekly: "Weekly", monthly: "Monthly", quarterly: "Quarterly"};
const scheduleName = (schedule) => scheduleNames[schedule] || schedule;
const startTime = (value) => new Intl.DateTimeFormat(undefined, {dateStyle: "medium", timeStyle: "short"}).format(new Date(value));

onMounted(async () => {
    try {
        organization.value = await api.organization();
    } catch (error) {
        problem.value = error.message;
    } finally {
        loading.value = false;
    }
});
</script>

<template>
    <section class="home-plan-board" data-home-plan-board aria-label="Plans">
        <h1>{{ view === "board" ? "Board" : "Plans" }}</h1>
        <p v-if="problem" class="home-plan-board-problem" role="alert">{{ problem }}</p>
        <label v-if="!loading" class="home-plan-board-filter">
            Filter plans
            <select v-model="filter" aria-label="Filter plans">
                <option value="all">All</option>
                <option value="running">Running</option>
                <option value="paused">Paused</option>
                <option value="waiting">Waiting on you</option>
                <option value="scheduled">Scheduled</option>
            </select>
        </label>
        <OrganizationPlanBoard v-if="loading || visiblePlans.length" :plans="visiblePlans" :sprint-forecasts="sprintForecasts" :view="view" :loading="loading" />
        <section v-if="showScheduled && scheduledPlans.length" class="home-plan-board-scheduled" aria-label="Scheduled plans">
            <h2>Starts on a schedule</h2>
            <ul>
                <li v-for="plan in scheduledPlans" :key="plan.id">
                    <span class="home-plan-board-scheduled-title">{{ plan.title }}</span>
                    <span>Schedule: {{ scheduleName(plan.schedule) }}</span>
                    <time :datetime="plan.next_start">Next start: {{ startTime(plan.next_start) }}</time>
                </li>
            </ul>
        </section>
        <EmptyState v-else-if="!loading && !problem && !visiblePlans.length" :title="emptyTitle">
            Plans that match this filter appear here.
        </EmptyState>
    </section>
</template>

<style scoped>
.home-plan-board {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-width: 0;
    padding: 18px 22px 40px;
}

.home-plan-board h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 650;
}

.home-plan-board-problem {
    margin: 0;
    color: var(--danger);
}

.home-plan-board-filter {
    display: flex;
    flex-direction: column;
    gap: 5px;
    width: min(300px, 100%);
    color: var(--text-2);
    font-size: 12px;
}

.home-plan-board-filter select {
    min-height: 34px;
    padding: 6px 9px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text);
    font: inherit;
}

.home-plan-board-scheduled h2 {
    margin: 0 0 8px;
    font-size: 16px;
}

.home-plan-board-scheduled ul {
    display: grid;
    gap: 8px;
    margin: 0;
    padding: 0;
    list-style: none;
}

.home-plan-board-scheduled li {
    display: flex;
    flex-wrap: wrap;
    gap: 5px 14px;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-2);
    font-size: 12px;
}

.home-plan-board-scheduled-title {
    color: var(--text);
    font-weight: 600;
}
</style>
