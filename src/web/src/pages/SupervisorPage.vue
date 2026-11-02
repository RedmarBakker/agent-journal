<script setup>
import {computed, onMounted, ref, watch} from "vue";
import {api} from "../api/client.js";
import Segmented from "../kit/Segmented.vue";
import {PAGES} from "../domain/navigation.js";
import {onPhone} from "../platform/phone.js";
import {href, route} from "../route.js";

const PERIODS = [
    {key: "today", label: "Today"},
    {key: "last_7_days", label: "Last 7 days"},
    {key: "last_30_days", label: "Last 30 days"},
];
const ACTIONS = [
    ["applied", "Actions applied"],
    ["conflicted", "Actions conflicted"],
    ["rejected", "Actions rejected"],
    ["proposed", "Proposals"],
];
const NOT_BUILT = ["Proposals accepted", "Proposals declined", "Useful results", "Undone by you", "Rated useful by you"];
const children = PAGES.supervisor.children;
const subpage = computed(() => route.value.sub || "dashboard");
const period = ref("last_7_days");
const planId = ref("");
const area = ref("");
const plans = ref([]);
const planProblem = ref("");
const answer = ref(null);
const problem = ref("");
const loading = ref(true);
let read = 0;

const records = computed(() => answer.value);
const current = computed(() => records.value?.current);
const previous = computed(() => records.value?.previous);
const actionStats = computed(() => [
    ...ACTIONS.map(([key, title]) => ({
        key,
        title,
        value: current.value.receipts[key],
        comparison: comparison(current.value.receipts[key], previous.value.receipts[key]),
    })),
    {
        key: "verified_receipts",
        title: "Verified receipts",
        value: current.value.verified_receipts,
        detail: `${current.value.verified_receipts} of ${current.value.receipts.applied} applied`,
        comparison: comparison(current.value.verified_receipts, previous.value.verified_receipts),
    },
]);

function comparison(value, before) {
    const difference = value - before;
    if (!difference) return `Same as before (${before})`;
    return `${Math.abs(difference)} ${difference > 0 ? "more" : "fewer"} than before (${before})`;
}

function rowsOf(result) {
    return Array.isArray(result) ? result : (result && result.rows) || [];
}

function subpageHref(key) {
    return `${href.page("supervisor")}?sub=${key}`;
}

function areaTitle(value) {
    return value.split("-").map((word) => `${word[0].toUpperCase()}${word.slice(1)}`).join(" ");
}

async function loadRecords() {
    const request = ++read;
    loading.value = true;
    problem.value = "";
    answer.value = null;
    try {
        const result = await api.supervisorRecords({period: period.value, planId: planId.value, area: area.value});
        if (request === read) answer.value = result;
    } catch (error) {
        if (request === read) problem.value = error.message || "The supervisor record read failed.";
    } finally {
        if (request === read) loading.value = false;
    }
}

async function loadPlans() {
    try {
        plans.value = rowsOf(await api.list("plans", {limit: 49}));
    } catch (error) {
        planProblem.value = error.message || "Plan choices could not be read.";
    }
}

watch([subpage, period, planId, area], () => {
    if (subpage.value === "dashboard") loadRecords();
}, {immediate: true});

onMounted(loadPlans);
</script>

<template>
    <main class="supervisor-page" data-supervisor-dashboard>
        <header class="supervisor-heading">
            <h1>Supervisor</h1>
            <p>What the supervisor did and how well, at a glance.</p>
        </header>

        <nav v-if="onPhone" class="supervisor-subpages" aria-label="Supervisor pages">
            <a
                v-for="child in children"
                :key="child.key"
                :href="subpageHref(child.key)"
                :aria-current="subpage === child.key ? 'page' : undefined"
            >{{ child.title }}</a>
        </nav>

        <template v-if="subpage === 'dashboard'">
            <p v-if="loading" class="supervisor-loading" role="status">Loading supervisor records.</p>
            <section v-else-if="problem" class="supervisor-fault" role="alert" data-record-fault>
                <h2>Could not read the supervisor's records</h2>
                <p>{{ problem }}</p>
            </section>
            <template v-else-if="records">
                <section class="supervisor-summary" aria-label="Supervisor summary">
                    <article class="supervisor-summary-card" data-summary-status>
                        <span class="summary-label">Status</span>
                        <strong class="summary-value">{{ records.status === "never_set_up" ? "Never set up" : records.status === "off" ? "Supervisor off" : "Supervisor on" }}</strong>
                        <p v-if="records.status === 'never_set_up'">Turning on is closed on this installation until its safety checks pass.</p>
                        <p v-else><span class="not-built-yet" title="Not built yet">Not built yet</span> Live bridge status</p>
                        <a :href="subpageHref('control')">Open Control</a>
                    </article>
                    <article class="supervisor-summary-card" data-stat="wake-ups">
                        <span class="summary-label">Wake-ups</span>
                        <strong class="summary-value"><span class="not-built-yet" title="Not built yet">Not built yet</span></strong>
                        <p>Wake-up records are not built yet.</p>
                        <a :href="subpageHref('control')">Open Control</a>
                    </article>
                    <article class="supervisor-summary-card" data-stat="today-cost">
                        <span class="summary-label">Today's cost</span>
                        <strong class="summary-value"><span class="not-built-yet" title="Not built yet">Not built yet</span></strong>
                        <p>Cost records are not built yet.</p>
                        <a :href="subpageHref('cost')">Open Cost</a>
                    </article>
                    <article class="supervisor-summary-card" data-stat="waiting">
                        <span class="summary-label">Waiting for you</span>
                        <strong class="summary-value"><span class="not-built-yet" title="Not built yet">Not built yet</span></strong>
                        <p>Waiting records are not built yet.</p>
                        <a :href="subpageHref('decisions')">Open Decisions and actions</a>
                    </article>
                </section>

                <section class="supervisor-statistics" aria-labelledby="supervisor-statistics-title">
                    <header class="supervisor-section-heading">
                        <div>
                            <h2 id="supervisor-statistics-title">Wake-ups and actions</h2>
                            <p>Each period is compared with the same period before it.</p>
                        </div>
                    </header>

                    <div class="supervisor-filters">
                        <label class="supervisor-period">Period
                            <Segmented :options="PERIODS" :value="period" @pick="period = $event" />
                        </label>
                        <label>Plan
                            <select v-model="planId" aria-label="Plan">
                                <option value="">All plans</option>
                                <option v-for="plan in plans" :key="plan.id" :value="String(plan.id)">Plan {{ plan.id }}: {{ plan.title }}</option>
                            </select>
                        </label>
                        <label>Area
                            <select v-model="area" aria-label="Area">
                                <option value="">All areas</option>
                                <option v-for="value in records.areas" :key="value" :value="value">{{ areaTitle(value) }}</option>
                            </select>
                        </label>
                        <span class="supervisor-period-note">Compared with the period before</span>
                    </div>
                    <p v-if="planProblem" class="supervisor-filter-note" role="status">{{ planProblem }}</p>

                    <p v-if="records.status === 'never_set_up'" class="supervisor-empty" role="status">
                        The supervisor has not woken in this period.
                    </p>
                    <template v-else>
                        <p v-if="records.status === 'off'" class="supervisor-off" role="status">
                            <strong>The supervisor is off.</strong> These figures are from before it was turned off.
                        </p>
                        <section class="supervisor-stat-block" aria-label="Wake-up statistics">
                            <h3>Wake-ups <span class="not-built-yet" title="Not built yet">Not built yet</span></h3>
                            <p>Wake-up kinds, skips and outcomes are not built yet.</p>
                        </section>
                        <section class="supervisor-stat-block" aria-label="Action statistics">
                            <h3>Actions</h3>
                            <div class="supervisor-stat-grid">
                                <article v-for="stat in actionStats" :key="stat.key" class="supervisor-stat" :data-action="stat.key">
                                    <span class="stat-label">{{ stat.title }}</span>
                                    <strong class="stat-value">{{ stat.value }}</strong>
                                    <span v-if="stat.detail" class="stat-detail">{{ stat.detail }}</span>
                                    <span class="stat-comparison">{{ stat.comparison }}</span>
                                </article>
                                <article v-for="title in NOT_BUILT" :key="title" class="supervisor-stat">
                                    <span class="stat-label">{{ title }}</span>
                                    <strong class="stat-value"><span class="not-built-yet" title="Not built yet">Not built yet</span></strong>
                                </article>
                            </div>
                        </section>
                    </template>
                </section>
            </template>
        </template>
        <section v-else class="supervisor-not-built" aria-label="Supervisor sub-page">
            <h2>{{ children.find((child) => child.key === subpage)?.title }}</h2>
            <p><span class="not-built-yet" title="Not built yet">Not built yet</span></p>
        </section>
    </main>
</template>

<style scoped>
.supervisor-page {
    max-width: 1240px;
    margin: 0 auto;
    padding: 22px 24px 36px;
    overflow: auto;
}
.supervisor-heading h1,
.supervisor-section-heading h2,
.supervisor-stat-block h3,
.supervisor-not-built h2 {
    margin: 0;
}
.supervisor-heading p,
.supervisor-section-heading p,
.supervisor-stat-block p,
.supervisor-summary-card p,
.supervisor-not-built p {
    margin: 6px 0 0;
    color: var(--text-3);
    font-size: 13px;
}
.supervisor-heading {
    margin-bottom: 18px;
}
.supervisor-summary {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 16px;
}
.supervisor-summary-card,
.supervisor-statistics,
.supervisor-not-built {
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--panel, var(--side));
}
.supervisor-summary-card {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    min-height: 140px;
    padding: 14px;
}
.summary-label,
.stat-label {
    color: var(--text-3);
    font-size: 12px;
}
.summary-value {
    margin-top: 9px;
    font-size: 20px;
    font-weight: 600;
}
.supervisor-summary-card p {
    min-height: 34px;
}
.supervisor-summary-card a {
    margin-top: auto;
    padding-top: 10px;
    color: var(--accent);
    font-size: 12px;
}
.supervisor-statistics {
    padding: 16px;
}
.supervisor-section-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}
.supervisor-filters {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px 14px;
    margin: 15px 0 12px;
    padding: 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-3);
    font-size: 12px;
}
.supervisor-filters label {
    display: flex;
    align-items: center;
    gap: 8px;
}
.supervisor-filters select {
    max-width: 240px;
    padding: 5px 8px;
    border: 1px solid var(--border-2);
    border-radius: 6px;
    color: var(--text);
    background: var(--side);
    font: inherit;
}
.supervisor-period {
    gap: 9px !important;
}
.supervisor-period-note {
    margin-left: auto;
}
.supervisor-filter-note,
.supervisor-loading,
.supervisor-empty,
.supervisor-fault,
.supervisor-off,
.supervisor-stat-block {
    padding: 12px;
    border-radius: 8px;
}
.supervisor-filter-note,
.supervisor-loading,
.supervisor-empty {
    color: var(--text-3);
}
.supervisor-empty {
    margin: 12px 0 0;
    background: var(--side);
}
.supervisor-off {
    margin: 12px 0;
    color: var(--text-2);
    background: var(--hover);
}
.supervisor-fault {
    color: var(--text);
    background: var(--danger-bg, var(--side));
}
.supervisor-fault h2 {
    margin: 0;
    color: var(--danger, var(--text));
    font-size: 16px;
}
.supervisor-fault p {
    margin: 8px 0 0;
}
.supervisor-stat-block {
    margin-top: 12px;
    border: 1px solid var(--border);
}
.supervisor-stat-block h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
}
.supervisor-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin-top: 12px;
}
.supervisor-stat {
    display: grid;
    gap: 6px;
    padding: 10px;
    border-radius: 7px;
    background: var(--side);
}
.stat-value {
    font-size: 19px;
    font-variant-numeric: tabular-nums;
}
.stat-detail,
.stat-comparison {
    color: var(--text-3);
    font-size: 11px;
}
.not-built-yet {
    display: inline-block;
    padding: 2px 6px;
    border: 1px dashed var(--border-2);
    border-radius: 4px;
    color: var(--text-3);
    font-size: 11px;
    font-weight: 400;
    white-space: nowrap;
}
.supervisor-subpages {
    display: none;
}
.supervisor-not-built {
    padding: 16px;
}
@media (max-width: 900px) {
    .supervisor-summary {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .supervisor-period-note {
        width: 100%;
        margin-left: 0;
    }
}
@media (max-width: 640px) {
    .supervisor-page {
        padding: 16px 12px 28px;
    }
    .supervisor-summary {
        gap: 7px;
    }
    .supervisor-summary-card {
        min-height: 132px;
        padding: 11px;
    }
    .supervisor-statistics {
        padding: 12px;
    }
    .supervisor-stat-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .supervisor-filters {
        align-items: flex-start;
    }
    .supervisor-period {
        align-items: flex-start !important;
        flex-direction: column;
    }
    .supervisor-subpages {
        display: flex;
        gap: 5px;
        margin: 0 0 14px;
        overflow-x: auto;
        border-bottom: 1px solid var(--border);
    }
    .supervisor-subpages a {
        flex: none;
        padding: 8px 10px;
        color: var(--text-3);
        font-size: 12px;
        white-space: nowrap;
    }
    .supervisor-subpages a[aria-current="page"] {
        border-bottom: 2px solid var(--accent);
        color: var(--text);
    }
}
</style>
