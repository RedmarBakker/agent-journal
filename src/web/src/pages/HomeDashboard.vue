<script setup>
import {computed, onMounted, ref} from "vue";
import {useScope} from "../composables/scope.js";
import {asking, fieldsOf, isSet, variableOf} from "../domain/secrets.js";
import {finishEstimate, estimatedCost, nearPlanCap} from "../domain/homeDashboard.js";
import {seconds} from "../domain/row.js";
import {ago} from "../format/time.js";
import {href, peek} from "../route.js";
import Approvals from "../organization/Approvals.vue";
import Btn from "../kit/Btn.vue";
import DeliveryForecastLabel from "../organization/DeliveryForecastLabel.vue";
import {forecastForPlan} from "../domain/deliveryForecast.js";
import {pointLabel} from "../domain/taskSizing.js";
import {planAgents} from "../domain/planAgents.js";

const scope = useScope();
const loading = ref(true);
const problem = ref("");
const organization = ref({plans: []});
const waiting = ref([]);
const workers = ref([]);
const workerTasks = ref({});
const planTasks = ref({});
const dashboard = ref({blocked_tasks: [], latest_merges: []});
const now = computed(() => Date.now());
const plans = computed(() => organization.value.plans || []);
const sprintForecasts = computed(() => organization.value.sprint_forecasts || []);
const runningPlans = computed(() => plans.value.filter((plan) => plan.plan_agent_state === "running"));
const dashboardPlans = computed(() => planAgents.value
    ? plans.value.filter((plan) => plan.state === "started")
    : runningPlans.value);
const waitingCount = computed(() => waiting.value.length);
const totalCost = computed(() => estimatedCost(plans.value));
const hasCost = computed(() => plans.value.some((plan) => plan.estimated_api_cost_usd !== null && plan.estimated_api_cost_usd !== undefined));
const blockedTasks = computed(() => dashboard.value.blocked_tasks || []);
const latestMerges = computed(() => dashboard.value.latest_merges || []);
const ACTIVE_WORKER_STATES = new Set(["dispatched", "clocked in", "clocked out"]);

function rowsOf(result) {
    return Array.isArray(result) ? result : (result && result.rows) || [];
}

async function allRows(table) {
    const found = new Map();
    let before = 0;
    let page = await scope.api.list(table, {limit: 49});
    while (page) {
        rowsOf(page).forEach((row) => found.set(row.id, row));
        if (page.is_last_page || !rowsOf(page).length) break;
        const oldest = Math.min(...rowsOf(page).map((row) => row.id));
        if (!oldest || oldest === before) break;
        before = oldest;
        page = await scope.api.list(table, {limit: 49, before});
    }
    return [...found.values()];
}

function dateValue(value) {
    if (typeof value === "number") return value * 1000;
    return value ? new Date(value).getTime() : 0;
}

function pendingApprovals(rows, questions) {
    const questionsById = new Map(questions.map((question) => [question.id, question]));
    return rows
        .filter((row) => row.decision === "pending" && (!row.expires_at || dateValue(row.expires_at) > now.value))
        .map((row) => ({kind: "approval", row, at: row.created_at, question: questionsById.get(row.question_id)?.text || "Approval required"}));
}

function pendingQuestions(rows, approvals) {
    const approvalQuestionIds = new Set(approvals.map((item) => item.row.question_id));
    return rows.filter((row) => !row.answer && !row.closed && !approvalQuestionIds.has(row.id)).map((row) => ({kind: "question", row, at: row.created_at}));
}

function pendingSecrets(rows) {
    return asking(rows.filter((row) => !row.deleted_at)).map((row) => ({kind: "secret", row, at: row.questioned_at}));
}

function waitingRows(approvals, questions, secrets) {
    const approvalsWaiting = pendingApprovals(approvals, questions);
    return [...approvalsWaiting, ...pendingQuestions(questions, approvalsWaiting), ...pendingSecrets(secrets)]
        .sort((first, second) => seconds(second.at) - seconds(first.at));
}

function missingVariable(row) {
    const field = fieldsOf(row).find((one) => one.hidden && !isSet(row, one));
    return field ? field.variable || variableOf(row.title, field.name) : row.title;
}

async function load() {
    try {
        const [org, home, approvals, questions, secrets, workerRows] = await Promise.all([
            scope.api.organization(),
            scope.api.homeDashboard(),
            allRows("approvals"),
            allRows("questions"),
            allRows("secrets"),
            allRows("workers"),
        ]);
        organization.value = org || {plans: []};
        dashboard.value = home || {blocked_tasks: [], latest_merges: []};
        waiting.value = waitingRows(approvals, questions, secrets);

        const active = workerRows.filter((worker) => ACTIVE_WORKER_STATES.has(worker.state));
        const detail = active.length ? rowsOf(await scope.api.list("workers", {ids: active.map((worker) => worker.id)})) : [];
        workers.value = detail;
        const taskIds = [...new Set(detail.map((worker) => worker.task?.task_id).filter(Boolean))];
        const workerTasksRows = taskIds.length ? rowsOf(await scope.api.list("tasks", {ids: taskIds})) : [];
        workerTasks.value = Object.fromEntries(workerTasksRows.map((task) => [task.id, task]));

        const finishRows = await Promise.all(dashboardPlans.value.map(async (plan) => [plan.id, rowsOf(await scope.api.planTasks(plan.id))]));
        planTasks.value = Object.fromEntries(finishRows);
    } catch (error) {
        problem.value = error.message || "The Home dashboard could not be loaded.";
    } finally {
        loading.value = false;
    }
}

function finish(plan) {
    return finishEstimate(plan, planTasks.value[plan.id] || [], now.value);
}

function mode(plan) {
    return plan.mode ? `${plan.mode[0].toUpperCase()}${plan.mode.slice(1)} mode` : "Mode not set";
}

function deliveryForecast(plan) {
    return forecastForPlan(plan.id, sprintForecasts.value);
}

function cost(plan) {
    return plan.estimated_api_cost_usd === null || plan.estimated_api_cost_usd === undefined
        ? "Not reported"
        : `$${Number(plan.estimated_api_cost_usd).toFixed(2)}`;
}

function cap(plan) {
    return Number(plan.cost_cap_usd) > 0 ? `$${Number(plan.cost_cap_usd).toFixed(2)}` : "No cap";
}

function costPercent(plan) {
    return Number(plan.cost_cap_usd) > 0 && Number.isFinite(Number(plan.estimated_api_cost_usd))
        ? Math.min(100, (Number(plan.estimated_api_cost_usd) / Number(plan.cost_cap_usd)) * 100)
        : 0;
}

function startTime(worker) {
    const steps = worker.moves?.steps || [];
    const start = [...steps].reverse().find(([word]) => word === "dispatched" || word === "sent a job");
    return start?.[1] || worker.began || seconds(worker.created_at);
}

function duration(at) {
    const minutes = Math.max(0, Math.floor((now.value / 1000 - seconds(at)) / 60));
    const hours = Math.floor(minutes / 60);
    return hours ? `${hours} h ${minutes % 60} min` : `${minutes} min`;
}

function workerState(worker) {
    return worker.state === "clocked out" ? "Waiting for its check" : "Working";
}

function openRow(table, id) {
    peek(table, id);
}

function questionFor(item) {
    return item.kind === "approval" ? item.question : "";
}

onMounted(load);
</script>

<template>
    <main class="home-dashboard" data-home-dashboard>
        <header class="home-dashboard-header">
            <h1>Home</h1>
            <p>Everything that is going on in this journal, now</p>
        </header>

        <p v-if="problem" class="home-dashboard-problem" role="alert">{{ problem }}</p>

        <section class="home-dashboard-stats" aria-label="Journal summary">
            <article :class="['home-dashboard-stat', {hot: waitingCount > 0}]" data-stat="waiting">
                <span class="value">{{ waitingCount }}</span><span class="label">things wait on you</span>
            </article>
            <article class="home-dashboard-stat" data-stat="plans">
                <span class="value">{{ runningPlans.length }}</span><span class="label">plans running</span>
            </article>
            <article class="home-dashboard-stat" data-stat="workers">
                <span class="value">{{ workers.length }}</span><span class="label">workers working now</span>
            </article>
            <article class="home-dashboard-stat" data-stat="cost">
                <span class="value">{{ hasCost ? `$${totalCost.toFixed(2)}` : "Not reported" }}</span><span class="label">estimated cost so far</span>
            </article>
        </section>

        <section class="home-dashboard-grid" aria-label="Journal dashboard">
            <section class="home-dashboard-card waiting wide" data-dashboard-card="waiting" :class="{hot: waitingCount > 0}">
                <header class="card-head"><h2>Waiting on you</h2><span class="count">{{ waitingCount }}</span></header>
                <p v-if="loading" class="card-empty">Loading what waits on you.</p>
                <p v-else-if="!waiting.length" class="card-empty">Nothing is waiting on you.</p>
                <div v-else class="dashboard-list">
                    <article v-for="item in waiting" :key="`${item.kind}:${item.row.id}`" class="dashboard-row waiting-row" :data-waiting-kind="item.kind">
                        <template v-if="item.kind === 'approval'">
                            <Approvals :approval="item.row" :question="questionFor(item)" />
                        </template>
                        <template v-else>
                            <div class="row-top">
                                <span :class="['kind-tag', item.kind]">{{ item.kind === "question" ? "Question" : "Secret" }}</span>
                                <button type="button" class="row-title" @click="openRow(item.kind === 'question' ? 'questions' : 'secrets', item.row.id)">
                                    {{ item.kind === "question" ? item.row.text : `Fill in ${missingVariable(item.row)}` }}
                                </button>
                                <time class="row-time" :datetime="item.at">{{ ago(seconds(item.at)) }}</time>
                            </div>
                            <div class="row-actions">
                                <Btn v-if="item.kind === 'question'" small @click="openRow('questions', item.row.id)">Answer it</Btn>
                                <Btn v-else small @click="openRow('secrets', item.row.id)">Fill in the secret</Btn>
                            </div>
                        </template>
                    </article>
                </div>
            </section>

            <section class="home-dashboard-card cost narrow" data-dashboard-card="cost">
                <header class="card-head"><h2>Estimated API cost so far</h2><span class="spacer"></span><a :href="href.settings()">Open Settings</a></header>
                <p class="card-note">Estimated from recorded token usage, not billed. Caps are per plan.</p>
                <p v-if="loading" class="card-empty">Loading cost estimates.</p>
                <p v-else-if="!hasCost" class="card-empty">No cost estimate has been reported.</p>
                <div v-else class="dashboard-list">
                    <div class="cost-total"><span>All plans together</span><strong>${{ totalCost.toFixed(2) }}</strong></div>
                    <article v-for="plan in runningPlans" :key="plan.id" :class="['cost-row', { 'near-cap': nearPlanCap(plan) }]" :data-cost-plan-id="plan.id">
                        <div class="cost-line"><span>Plan {{ plan.id }}: {{ plan.title }}</span><strong>{{ cost(plan) }} of {{ cap(plan) }}</strong></div>
                        <div v-if="Number(plan.cost_cap_usd) > 0" class="meter" role="progressbar" :aria-valuenow="costPercent(plan)" aria-valuemin="0" aria-valuemax="100">
                            <span :style="{width: `${costPercent(plan)}%`}"></span>
                        </div>
                        <p v-if="plan.estimated_api_cost_status === 'stale'" class="cost-status">Last estimate is stale.</p>
                    </article>
                    <p v-if="!runningPlans.length" class="card-note">No running plan has a cost cap to show.</p>
                </div>
            </section>

            <section class="home-dashboard-card plans wide" data-dashboard-card="plans">
                <header class="card-head"><h2>{{ planAgents ? "Started plans" : "Running plans" }}</h2><span class="count">{{ dashboardPlans.length }}</span><span class="spacer"></span><a :href="href.page('board')">Open the Board</a></header>
                <p v-if="loading" class="card-empty">{{ planAgents ? "Loading started plans." : "Loading running plans." }}</p>
                <p v-else-if="!dashboardPlans.length" class="card-empty">{{ planAgents ? "No plan has started." : "No plan is running. Start one from the Board or the Plans list." }}</p>
                <div v-else class="dashboard-list">
                    <article v-for="plan in dashboardPlans" :key="plan.id" class="dashboard-row plan-row" :data-plan-id="plan.id">
                        <div class="row-top">
                            <button type="button" class="row-title" @click="openRow('plans', plan.id)">{{ plan.title }}</button>
                            <span class="row-id">Plan {{ plan.id }}</span>
                        </div>
                        <div class="progress-line">
                            <div class="meter"><span :style="{width: `${plan.tasks?.length ? (plan.done / plan.tasks.length) * 100 : 0}%`}"></span></div>
                            <span class="progress-count">{{ plan.done || 0 }} of {{ (plan.tasks || []).length }} tasks done</span>
                        </div>
                        <div class="row-meta">
                            <span class="mode-chip">{{ mode(plan) }}</span>
                            <span class="progress-count">{{ pointLabel(plan) }}</span>
                            <span v-if="planAgents" class="plan-agent-state">Plan agent: {{ plan.plan_agent_state || "not started" }}</span>
                            <a v-if="planAgents && plan.chat" class="plan-agent-chat" :href="scope.api.page(plan.chat)" :title="`Plan agent in ${plan.chat}`">Open its chat</a>
                            <time v-if="finish(plan)" class="expected-finish" :datetime="finish(plan).date">Expected to finish {{ finish(plan).label }}</time>
                            <span v-else class="no-finish-date">No finish date yet: no task has finished</span>
                        </div>
                        <DeliveryForecastLabel :forecast="deliveryForecast(plan)" :sprint="deliveryForecast(plan)?.sprint || null" :plan="plan" />
                    </article>
                    <p class="card-footnote">Finish date is a simple estimate from tasks completed per day so far.</p>
                </div>
            </section>

            <section class="home-dashboard-card workers narrow" data-dashboard-card="workers">
                <header class="card-head"><h2>Workers working now</h2><span class="count">{{ workers.length }}</span></header>
                <p v-if="loading" class="card-empty">Loading workers.</p>
                <p v-else-if="!workers.length" class="card-empty">No worker is out.</p>
                <div v-else class="dashboard-list">
                    <article v-for="worker in workers" :key="worker.id" class="dashboard-row worker-row" :data-worker-id="worker.id">
                        <div class="row-top"><span class="row-title">Task {{ worker.task?.task_id || "—" }}: {{ workerTasks[worker.task?.task_id]?.title || "No task in hand" }}</span></div>
                        <div class="row-meta">
                            <span>{{ worker.role || worker.name }}</span>
                            <span v-if="worker.plan_id">· plan {{ worker.plan_id }}</span>
                            <span>· {{ workerState(worker) }}</span>
                            <span class="out-duration">out for {{ duration(startTime(worker)) }}</span>
                        </div>
                    </article>
                </div>
            </section>

            <section class="home-dashboard-card blocked phone-fourth" data-dashboard-card="blocked">
                <header class="card-head"><h2>Blocked tasks</h2><span class="count">{{ blockedTasks.length }}</span></header>
                <p v-if="loading" class="card-empty">Loading blocked tasks.</p>
                <p v-else-if="!blockedTasks.length" class="card-empty">No tasks are blocked.</p>
                <div v-else class="dashboard-list">
                    <article v-for="task in blockedTasks" :key="task.id" class="dashboard-row blocked-row" :data-blocked-task-id="task.id">
                        <div class="row-top"><button type="button" class="row-title" @click="openRow('tasks', task.id)">Task {{ task.id }}: {{ task.title }}</button><span v-if="task.plan_id" class="row-id">Plan {{ task.plan_id }}</span></div>
                        <p class="wait-reason">Waiting on {{ (task.wait_reasons || []).join("; ") }}</p>
                    </article>
                </div>
            </section>

            <section class="home-dashboard-card merges" data-dashboard-card="merges">
                <header class="card-head"><h2>Latest merges</h2><span class="count">{{ latestMerges.length }}</span><span class="spacer"></span><a :href="href.page('workers')">Show all merges</a></header>
                <p v-if="loading" class="card-empty">Loading recent merges.</p>
                <p v-else-if="!latestMerges.length" class="card-empty">No recent merges.</p>
                <div v-else class="dashboard-list">
                    <article v-for="merge in latestMerges" :key="`${merge.task_id}:${merge.merged_at}`" class="dashboard-row merge-row" :data-merge-task-id="merge.task_id">
                        <div class="row-top"><span class="row-title">Task {{ merge.task_id }}: {{ merge.task_title }}</span><time class="row-time" :datetime="merge.merged_at">{{ ago(seconds(merge.merged_at)) }}</time></div>
                        <div class="row-meta"><span v-if="merge.plan_id">Plan {{ merge.plan_id }} · </span><span>{{ merge.branch }}</span><span>· by {{ merge.worker }}</span><span class="line-counts"><b>+{{ merge.added }}</b> <i>−{{ merge.removed }}</i></span></div>
                    </article>
                </div>
            </section>
        </section>
    </main>
</template>

<style scoped>
.home-dashboard {
    height: 100%;
    min-height: 0;
    overflow: auto;
    padding: 20px 24px 36px;
    color: var(--text);
}

.home-dashboard-header {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 12px;
}

.home-dashboard-header h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

.home-dashboard-header p,
.card-note,
.card-footnote,
.cost-status {
    margin: 0;
    color: var(--text-3);
    font-size: 12px;
}

.home-dashboard-problem {
    margin: 0 0 12px;
    color: var(--danger);
    font-size: 12px;
}

.home-dashboard-stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 14px;
}

.home-dashboard-stat {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: var(--raised);
}

.home-dashboard-stat .value {
    font-size: 20px;
    font-weight: 600;
    line-height: 1.2;
    font-variant-numeric: tabular-nums;
}

.home-dashboard-stat .label {
    color: var(--text-3);
    font-size: 11.5px;
}

.home-dashboard-stat.hot .value {
    color: var(--warn);
}

.home-dashboard-grid {
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    gap: 14px;
    align-items: start;
}

.home-dashboard-card {
    grid-column: span 6;
    min-width: 0;
    overflow: hidden;
    border: 1px solid var(--border-2);
    border-radius: 9px;
    background: var(--bg);
}

.home-dashboard-card.wide {
    grid-column: span 7;
}

.home-dashboard-card.narrow {
    grid-column: span 5;
}

.home-dashboard-card.hot {
    border-color: var(--warn);
}

.card-head {
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 42px;
    padding: 9px 14px;
    border-bottom: 1px solid var(--border);
}

.hot .card-head {
    background: color-mix(in srgb, var(--warn) 8%, transparent);
}

.card-head h2 {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
}

.card-head .count {
    color: var(--text-3);
    font-size: 12px;
}

.card-head .spacer {
    flex: 1;
}

.card-head a {
    color: var(--accent-text);
    font-size: 12px;
    text-decoration: none;
}

.card-head a:hover {
    text-decoration: underline;
}

.plan-agent-chat {
    color: var(--accent-text);
    font-size: 12px;
    text-decoration: none;
}

.card-empty {
    display: flex;
    align-items: center;
    min-height: 58px;
    margin: 0;
    padding: 16px 14px;
    color: var(--text-3);
    font-size: 12.5px;
}

.dashboard-list {
    display: flex;
    flex-direction: column;
}

.dashboard-row,
.cost-row {
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 0;
    padding: 10px 14px;
    border-bottom: 1px solid var(--line);
}

.dashboard-row:last-child,
.cost-row:last-child {
    border-bottom: 0;
}

.row-top,
.row-meta,
.row-actions,
.progress-line,
.cost-line {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.row-top {
    align-items: baseline;
}

.row-title {
    min-width: 0;
    padding: 0;
    border: 0;
    background: none;
    color: var(--text);
    font: inherit;
    font-size: 13px;
    font-weight: 550;
    line-height: 1.35;
    text-align: left;
    overflow-wrap: anywhere;
}

button.row-title {
    cursor: pointer;
}

button.row-title:hover {
    color: var(--accent-text);
}

.row-id,
.row-time,
.row-meta,
.progress-count {
    color: var(--text-3);
    font-size: 11.5px;
}

.row-time,
.row-id,
.progress-count {
    flex: none;
    white-space: nowrap;
}

.row-meta {
    flex-wrap: wrap;
    font-size: 12px;
}

.kind-tag {
    flex: none;
    width: 62px;
    color: var(--warn);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.kind-tag.question {
    color: var(--accent-text);
}

.kind-tag.secret {
    color: var(--work);
}

.row-actions {
    margin-left: 70px;
    flex-wrap: wrap;
}

.row-actions :deep(.btn) {
    height: 27px;
}

.waiting-row :deep(.approval-card) {
    padding: 0;
    border: 0;
    background: transparent;
}

.waiting-row :deep(.approval-top) {
    display: none;
}

.waiting-row :deep(.approval-context) {
    margin-left: 70px;
}

.waiting-row :deep(.approval-actions) {
    margin-left: 70px;
}

.progress-line {
    gap: 10px;
}

.meter {
    flex: 1;
    min-width: 60px;
    height: 6px;
    overflow: hidden;
    border-radius: 99px;
    background: var(--chip);
}

.meter span {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: var(--progress);
}

.mode-chip {
    padding: 2px 8px;
    border: 1px solid var(--border-2);
    border-radius: 99px;
    color: var(--text-2);
    font-size: 11px;
}

.expected-finish {
    color: var(--text-2);
    font-size: 12px;
}

.no-finish-date {
    color: var(--text-3);
    font-size: 12px;
}

.card-footnote {
    padding: 8px 14px;
    border-top: 1px solid var(--line);
}

.card-note {
    padding: 8px 14px 0;
}

.cost-total,
.cost-line {
    justify-content: space-between;
    gap: 10px;
    color: var(--text-2);
    font-size: 12.5px;
}

.cost-total {
    display: flex;
    justify-content: space-between;
    padding: 11px 14px;
    border-bottom: 1px solid var(--line);
}

.cost-total strong,
.cost-line strong {
    color: var(--text);
    font-weight: 600;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}

.cost-row .meter span {
    background: var(--progress);
}

.cost-row.near-cap .meter span {
    background: var(--warn);
}

.cost-status {
    color: var(--warn);
}

.wait-reason {
    margin: 0;
    color: var(--text-2);
    font-size: 12px;
}

.out-duration {
    margin-left: auto;
    white-space: nowrap;
}

.line-counts {
    display: inline-flex;
    gap: 6px;
    margin-left: auto;
    white-space: nowrap;
}

.line-counts b {
    color: var(--good);
    font-weight: 500;
}

.line-counts i {
    color: var(--danger);
    font-style: normal;
}

@media (max-width: 760px) {
    .home-dashboard {
        padding: 16px 12px 28px;
    }

    .home-dashboard-header {
        align-items: flex-start;
        flex-direction: column;
        gap: 3px;
    }

    .home-dashboard-stats {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .home-dashboard-grid {
        display: flex;
        flex-direction: column;
        align-items: stretch;
    }

    .home-dashboard-card {
        width: 100%;
        grid-column: auto;
    }

    .home-dashboard-card.waiting { order: 1; }
    .home-dashboard-card.plans { order: 2; }
    .home-dashboard-card.workers { order: 3; }
    .home-dashboard-card.blocked { order: 4; }
    .home-dashboard-card.cost { order: 5; }
    .home-dashboard-card.merges { order: 6; }
}
</style>
