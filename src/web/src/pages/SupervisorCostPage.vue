<script setup>
import {computed, ref} from "vue";
import {api} from "../api/client.js";

const costs = ref(null);
const problem = ref("");
const loading = ref(true);
const dailyCap = ref(null);
const selectedInterval = ref(null);
const PERIODS = [
    {key: "today", title: "Today"},
    {key: "week", title: "This week"},
    {key: "month", title: "This month"},
];
const INTERVALS = [15, 30, 60];

const periods = computed(() => costs.value?.periods || {});
const week = computed(() => periods.value.week || {});
const active = computed(() => Boolean(periods.value.month?.runs || periods.value.month?.wakeups));
const trend = computed(() => costs.value?.daily_trend || []);
const wakeups = computed(() => costs.value?.wakeups_per_day || []);
const knownRunCost = computed(() => costs.value?.averages?.per_wakeup?.usd);
const runShare = computed(() => week.value.wakeups ? week.value.runs / week.value.wakeups : 0);
const trendScale = computed(() => Math.max(
    dailyCap.value || 0,
    ...trend.value.map((day) => Number(day.known_usd) || 0),
    0.01,
));
const wakeupScale = computed(() => Math.max(1, ...wakeups.value.map((day) => day.total)));
const intervals = computed(() => INTERVALS.map((minutes) => {
    const fullRate = knownRunCost.value === null || knownRunCost.value === undefined
        ? null
        : Number(knownRunCost.value) * 1440 / minutes;
    return {
        minutes,
        full_rate: fullRate,
        expected_rate: fullRate === null ? null : fullRate * runShare.value,
    };
}));

function money(value) {
    return value === null || value === undefined ? "Not known" : `$${Number(value).toFixed(2)}`;
}

function periodCost(period) {
    if (period.unknown_runs) {
        return period.known_runs ? `${money(period.known_usd)} known` : "Not known";
    }
    return money(period.known_usd);
}

function periodNote(period) {
    const capNote = `Daily cost cap × ${period.days} ${period.days === 1 ? "day" : "days"}`;
    if (period.unknown_runs) {
        const noun = period.unknown_runs === 1 ? "run" : "runs";
        return `${capNote} · ${period.unknown_runs} ${noun} cost Not known`;
    }
    return capNote;
}

function capFor(days) {
    return dailyCap.value === null ? "Not available" : money(dailyCap.value * days);
}

function periodFill(period) {
    if (dailyCap.value === null) return "0%";
    const cap = dailyCap.value * period.days;
    return `${Math.min(100, Number(period.known_usd) / cap * 100)}%`;
}

function totalLabel(item) {
    if (item.unknown_runs) {
        return item.known_usd === "0.00"
            ? "Not known"
            : `${money(item.known_usd)} known · ${item.unknown_runs} Not known`;
    }
    return money(item.known_usd);
}

function averageLabel(item, missing) {
    if (item.usd !== null && item.usd !== undefined) return money(item.usd);
    if (item.unknown_runs || item.unknown_results) return "Not known";
    return missing;
}

function savingsLabel() {
    const savings = costs.value?.quiet_savings;
    if (!savings?.quiet_wakeups) return "No quiet wake-ups yet";
    return savings.estimated_usd === null ? "Not known" : `${money(savings.estimated_usd)} estimated`;
}

function costHeight(day) {
    if (day.known_usd === null) return "0%";
    return `${Math.max(1, Number(day.known_usd) / trendScale.value * 100)}%`;
}

function wakeupHeight(count) {
    return `${count / wakeupScale.value * 100}%`;
}

function wakeupDate(date) {
    return new Date(`${date}T00:00:00`).toLocaleDateString(undefined, {weekday: "short"});
}

function wakeupTitle(day) {
    return `${day.date}: ${day.total} wake-ups, ${day.quiet} skipped as quiet`;
}

function dayCostTitle(day) {
    if (day.unknown_runs) {
        return `${day.date}: Not known for ${day.unknown_runs} ${day.unknown_runs === 1 ? "run" : "runs"}`;
    }
    return `${day.date}: ${money(day.known_usd)}`;
}

function intervalEstimate(value) {
    return value === null ? "Not known" : `${money(value)} a day`;
}

async function loadCosts() {
    try {
        costs.value = await api.supervisorCosts();
    } catch (error) {
        problem.value = error.message || "Cost records could not be read.";
    } finally {
        loading.value = false;
    }
}

async function loadControl() {
    try {
        const control = await api.supervisorControl();
        const limit = control.grant?.limits?.max_cost_microusd_per_day;
        dailyCap.value = Number.isFinite(Number(limit)) && Number(limit) > 0 ? Number(limit) / 1000000 : null;
        selectedInterval.value = Number(control.grant?.wake_interval_minutes) || null;
    } catch {
        dailyCap.value = null;
        selectedInterval.value = null;
    }
}

loadCosts();
loadControl();
</script>

<template>
    <section class="supervisor-costs" data-supervisor-costs aria-labelledby="supervisor-cost-title">
        <header class="cost-heading">
            <div>
                <h2 id="supervisor-cost-title">Cost</h2>
                <p>Measured supervisor costs, unknown usage and the daily cap.</p>
            </div>
        </header>

        <p v-if="problem" class="cost-problem" role="alert" data-cost-fault>{{ problem }}</p>
        <p v-if="costs?.status === 'off'" class="cost-off" role="status">
            <strong>The supervisor is off.</strong> Recorded costs remain available.
        </p>
        <p v-if="loading" class="cost-loading" role="status">Loading cost records.</p>
        <p v-else-if="!problem && !active" class="cost-empty" role="status">No cost recorded.</p>
        <template v-else-if="!problem && costs">
            <section class="cost-periods" aria-label="Cost against the daily cap">
                <article
                    v-for="period in PERIODS"
                    :key="period.key"
                    class="cost-period"
                    :data-cost-period="period.key"
                >
                    <div class="cost-period-heading">
                        <h3>{{ period.title }}</h3>
                        <strong>{{ periodCost(periods[period.key]) }}</strong>
                    </div>
                    <p>of {{ capFor(periods[period.key].days) }}</p>
                    <div
                        class="cost-track"
                        :data-incomplete="Boolean(periods[period.key].unknown_runs)"
                    >
                        <span :style="{width: periodFill(periods[period.key])}" />
                    </div>
                    <small>{{ periodNote(periods[period.key]) }}</small>
                </article>
            </section>

            <section class="cost-lists" aria-label="Cost averages and totals">
                <article class="cost-card">
                    <h3>Averages, last 7 days</h3>
                    <dl>
                        <div>
                            <dt>Cost per wake-up that ran the model</dt>
                            <dd>{{ averageLabel(costs.averages.per_wakeup, "No model runs") }}</dd>
                        </div>
                        <div>
                            <dt>Cost per action</dt>
                            <dd>{{ averageLabel(costs.averages.per_action, "No actions") }}</dd>
                        </div>
                        <div>
                            <dt>Cost per useful result</dt>
                            <dd>{{ averageLabel(costs.averages.per_useful_result, "No useful results") }}</dd>
                        </div>
                    </dl>
                    <p v-if="costs.averages.per_wakeup.unknown_runs" class="cost-unknown-note">
                        {{ costs.averages.per_wakeup.unknown_runs }} run cost Not known.
                    </p>
                </article>
                <article class="cost-card">
                    <h3>Cost per plan, last 7 days</h3>
                    <p v-if="!costs.per_plan.length">No plan costs recorded.</p>
                    <dl v-else>
                        <div v-for="item in costs.per_plan" :key="item.plan_id">
                            <dt>Plan {{ item.plan_id }}: {{ item.title }}</dt><dd>{{ totalLabel(item) }}</dd>
                        </div>
                    </dl>
                </article>
                <article class="cost-card">
                    <h3>Cost per area, last 7 days</h3>
                    <p v-if="!costs.per_area.length">No area costs recorded.</p>
                    <dl v-else>
                        <div v-for="item in costs.per_area" :key="item.area_key">
                            <dt>{{ item.title }}</dt><dd>{{ totalLabel(item) }}</dd>
                        </div>
                    </dl>
                </article>
            </section>

            <section class="cost-card cost-intervals" aria-labelledby="cost-interval-title">
                <h3 id="cost-interval-title">Cost per interval</h3>
                <dl>
                    <div v-for="item in intervals" :key="item.minutes" :data-interval="item.minutes">
                        <dt>Every {{ item.minutes === 60 ? "hour" : `${item.minutes} minutes` }}
                            <span v-if="selectedInterval === item.minutes">(selected)</span>
                        </dt>
                        <dd>{{ intervalEstimate(item.full_rate) }}</dd>
                        <dd class="cost-interval-observed">
                            {{ intervalEstimate(item.expected_rate) }} at the last 7 days run rate
                        </dd>
                    </div>
                </dl>
                <p v-if="week.unknown_runs">
                    Estimates use known run costs; {{ week.unknown_runs }} run cost Not known.
                </p>
            </section>

            <section class="cost-card cost-savings" aria-label="Savings from quiet wake-ups">
                <div><h3>Saved by skipping quiet wake-ups</h3>
                    <p>{{ costs.quiet_savings.quiet_wakeups }} quiet wake-ups in the last 7 days.</p>
                </div>
                <strong>{{ savingsLabel() }}</strong>
            </section>

            <section class="cost-card" aria-labelledby="wakeup-days-title">
                <h3 id="wakeup-days-title">Wake-ups per day, last 7 days</h3>
                <div class="wakeup-chart" role="list" aria-label="Daily wake-ups; dark bars are skipped as quiet">
                    <div
                        v-for="day in wakeups"
                        :key="day.date"
                        class="wakeup-day"
                        role="listitem"
                        :title="wakeupTitle(day)"
                    >
                        <strong>{{ day.total }}</strong>
                        <div class="wakeup-track">
                            <span class="wakeup-other" :style="{height: wakeupHeight(day.total - day.quiet)}" />
                            <span class="wakeup-quiet" :style="{height: wakeupHeight(day.quiet)}" />
                        </div>
                        <small>{{ wakeupDate(day.date) }}</small>
                    </div>
                </div>
                <p>Dark bars show wake-ups skipped as quiet.</p>
            </section>

            <section class="cost-card" aria-labelledby="cost-trend-title">
                <h3 id="cost-trend-title">Daily cost, last 30 days</h3>
                <div class="trend-chart" role="img" aria-label="Daily known cost for 30 days with the daily cap line">
                    <span
                        v-for="day in trend"
                        :key="day.date"
                        class="trend-day"
                        :class="{'trend-unknown': day.unknown_runs > 0}"
                        :data-trend-day="day.date"
                        :data-cost-status="day.unknown_runs ? 'unknown' : 'known'"
                        :title="dayCostTitle(day)"
                        :style="{height: costHeight(day)}"
                    />
                    <span v-if="dailyCap !== null" class="cost-cap-line" data-cost-cap-line
                          :style="{bottom: `${Math.min(100, dailyCap / trendScale * 100)}%`}">
                        <span>Daily cap {{ money(dailyCap) }}</span>
                    </span>
                </div>
                <p class="trend-caption">
                    <span>30 days ago</span>
                    <span>Outlined bars have cost Not known.</span>
                    <span>Today</span>
                </p>
            </section>
        </template>
    </section>
</template>

<style scoped>
.supervisor-costs {
    display: grid;
    gap: 14px;
}

.cost-heading h2,
.cost-heading p,
.cost-card h3,
.cost-period h3 {
    margin: 0;
}

.cost-heading h2 {
    font-size: 18px;
}

.cost-heading p,
.cost-card p,
.cost-period p,
.cost-period small,
.trend-caption {
    color: var(--text-3);
    font-size: 12px;
}

.cost-heading p {
    margin-top: 5px;
}

.cost-periods,
.cost-lists {
    display: grid;
    gap: 10px;
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.cost-period,
.cost-card,
.cost-empty,
.cost-problem,
.cost-off {
    padding: 14px;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: var(--surface);
}

.cost-period-heading,
.cost-savings {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
}

.cost-period h3,
.cost-card h3 {
    font-size: 14px;
}

.cost-period p {
    margin: 4px 0 8px;
}

.cost-period small {
    display: block;
    margin-top: 6px;
}

.cost-track {
    height: 8px;
    overflow: hidden;
    border-radius: 99px;
    background: var(--surface-2);
}

.cost-track span {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: var(--accent);
}

.cost-track[data-incomplete="true"] {
    outline: 1px dashed var(--warn);
}

.cost-card dl {
    display: grid;
    gap: 9px;
    margin: 12px 0 0;
}

.cost-card dl > div {
    display: flex;
    justify-content: space-between;
    gap: 14px;
}

.cost-card dt,
.cost-card dd {
    margin: 0;
    font-size: 13px;
}

.cost-card dt {
    color: var(--text-2);
}

.cost-card dd {
    text-align: right;
    font-weight: 600;
    white-space: nowrap;
}

.cost-unknown-note,
.cost-interval-observed {
    color: var(--text-3);
    font-weight: 400 !important;
}

.cost-intervals dl > div {
    display: grid;
    grid-template-columns: 1fr auto auto;
}

.cost-intervals dt span {
    color: var(--accent);
    font-size: 11px;
}

.cost-savings {
    align-items: center;
}

.cost-savings p {
    margin: 5px 0 0;
}

.wakeup-chart {
    display: grid;
    grid-template-columns: repeat(7, minmax(24px, 1fr));
    gap: 8px;
    align-items: end;
    min-height: 110px;
    margin-top: 12px;
}

.wakeup-day {
    display: grid;
    justify-items: center;
    gap: 4px;
    color: var(--text-3);
    font-size: 11px;
}

.wakeup-track {
    display: flex;
    flex-direction: column-reverse;
    justify-content: flex-start;
    width: min(100%, 28px);
    height: 72px;
    overflow: hidden;
    border-radius: 4px;
    background: var(--surface-2);
}

.wakeup-other,
.wakeup-quiet {
    display: block;
    min-height: 0;
}

.wakeup-other {
    background: var(--accent);
}

.wakeup-quiet {
    background: var(--text-2);
}

.trend-chart {
    position: relative;
    display: flex;
    align-items: end;
    gap: 3px;
    height: 126px;
    margin-top: 12px;
    padding-bottom: 2px;
    border-bottom: 1px solid var(--line);
}

.trend-day {
    flex: 1;
    min-width: 3px;
    background: var(--accent);
}

.trend-unknown {
    border: 1px solid var(--warn);
    background: transparent;
}

.cost-cap-line {
    position: absolute;
    right: 0;
    left: 0;
    border-top: 2px dashed var(--danger);
    color: var(--danger);
    font-size: 10px;
    pointer-events: none;
}

.cost-cap-line span {
    position: absolute;
    right: 0;
    bottom: 3px;
    padding: 1px 4px;
    background: var(--surface);
}

.trend-caption {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin: 6px 0 0;
}

@media (max-width: 720px) {
    .cost-periods,
    .cost-lists {
        grid-template-columns: 1fr;
    }

    .cost-intervals dl > div {
        grid-template-columns: 1fr auto;
    }

    .cost-interval-observed {
        grid-column: 1 / -1;
        text-align: left !important;
    }
}
</style>
