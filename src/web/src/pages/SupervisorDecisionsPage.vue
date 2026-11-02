<script setup>
import {computed, ref, watch} from "vue";
import {api} from "../api/client.js";
import {refreshSupervisorWaitingCount} from "../composables/navigation.js";

const RESULTS = ["Acted", "Proposed", "Nothing to do", "Skipped as quiet", "Skipped", "Handed to you", "In progress"];
const history = ref([]);
const areas = ref([]);
const plans = ref([]);
const planId = ref("");
const area = ref("");
const tier = ref("");
const result = ref("");
const nextHistoryBefore = ref("");
const historyStatus = ref("");
const loading = ref(true);
const loadingOlder = ref(false);
const owner = ref(false);
const problem = ref("");
const undoProblem = ref("");
const undoing = ref("");
const proposalProblem = ref("");
const decidingProposal = ref("");
const feedbackProblem = ref({});
const feedbackStatus = ref({});
const savingFeedback = ref("");
const makingRule = ref("");
let read = 0;
let historyLoad = Promise.resolve();
let historyRefresh = Promise.resolve();

const hasHistory = computed(() => history.value.length > 0);

function rowsOf(answer) {
    return Array.isArray(answer) ? answer : (answer && answer.rows) || [];
}

function areaTitle(value) {
    return value.split("-").map((word) => `${word[0].toUpperCase()}${word.slice(1)}`).join(" ");
}

function planTitle(id) {
    if (!id) return "Whole environment";
    const plan = plans.value.find((item) => String(item.id) === String(id));
    return plan ? `Plan ${id}: ${plan.title}` : `Plan ${id}`;
}

function when(value) {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function cost(value) {
    if (!value || value.status === "unknown" || value.usd === null) return "Not known";
    return `$${Number(value.usd).toFixed(2)}`;
}

function changeValue(value) {
    if (value === null || value === undefined) return "None";
    return typeof value === "object" ? JSON.stringify(value) : String(value);
}

function firstActionForReceipt(row, action) {
    return row.actions.find((item) => item.receipt_id === action.receipt_id) === action;
}

async function loadPlans() {
    try {
        plans.value = rowsOf(await api.list("plans", {limit: 49}));
    } catch (error) {
        problem.value = error.message || "Plan choices could not be read.";
    }
}

function checkOwner() {
    api.supervisorControl().then(
        () => { owner.value = true; },
        () => { owner.value = false; },
    );
}

function feedbackFor(row) {
    return row.feedback || {useful: null, comment: "", correction: "", rule_id: null};
}

function historyRow(row) {
    const feedback = feedbackFor(row);
    return {...row, feedback, savedCorrection: feedback.correction || ""};
}

function readHistory(historyBefore) {
    return api.supervisorHistory({
        planId: planId.value,
        area: area.value,
        tier: tier.value,
        result: result.value,
        before: historyBefore,
    });
}

function trackHistoryRefresh(pending) {
    historyRefresh = Promise.all([historyRefresh, pending]).then(() => undefined);
    return pending;
}

function loadHistory() {
    const request = ++read;
    loading.value = true;
    problem.value = "";
    history.value = [];
    nextHistoryBefore.value = "";
    historyLoad = (async () => {
        try {
            const answer = await readHistory("");
            if (request !== read) return;
            historyStatus.value = answer.status || "";
            history.value = (answer.history || []).map(historyRow);
            areas.value = answer.areas || [];
            nextHistoryBefore.value = answer.next_before || "";
        } catch (error) {
            if (request === read) problem.value = error.message || "The supervisor history could not be read.";
        } finally {
            if (request === read) loading.value = false;
        }
    })();
    return historyLoad;
}

async function saveFeedback(row) {
    if (savingFeedback.value) return;
    savingFeedback.value = row.id;
    feedbackProblem.value = {...feedbackProblem.value, [row.id]: ""};
    feedbackStatus.value = {...feedbackStatus.value, [row.id]: ""};
    try {
        const answer = await api.supervisorFeedback(row.id, {
            useful: row.feedback.useful,
            comment: row.feedback.comment,
            correction: row.feedback.correction,
        });
        row.feedback = answer.feedback;
        row.savedCorrection = answer.feedback.correction;
        feedbackStatus.value = {...feedbackStatus.value, [row.id]: "Feedback saved."};
    } catch (error) {
        feedbackProblem.value = {...feedbackProblem.value, [row.id]: error.message || "Feedback could not be saved."};
    } finally {
        savingFeedback.value = "";
    }
}

async function makeRule(row) {
    if (makingRule.value) return;
    makingRule.value = row.id;
    feedbackProblem.value = {...feedbackProblem.value, [row.id]: ""};
    feedbackStatus.value = {...feedbackStatus.value, [row.id]: ""};
    try {
        const answer = await api.supervisorFeedbackRule(row.id);
        row.feedback.rule_id = answer.rule.id;
        feedbackStatus.value = {...feedbackStatus.value, [row.id]: "Correction added as a rule."};
    } catch (error) {
        feedbackProblem.value = {...feedbackProblem.value, [row.id]: error.message || "The correction could not be added as a rule."};
    } finally {
        makingRule.value = "";
    }
}

async function loadOlder() {
    if (loadingOlder.value) return;
    while (undoing.value || decidingProposal.value) await historyRefresh;
    while (loading.value) await historyLoad;
    if (!nextHistoryBefore.value || loadingOlder.value) return;
    const request = read;
    const cursor = nextHistoryBefore.value;
    loadingOlder.value = true;
    undoProblem.value = "";
    try {
        const answer = await readHistory(cursor);
        if (request !== read) return;
        history.value = [...history.value, ...(answer.history || []).map(historyRow)];
        nextHistoryBefore.value = answer.next_before || "";
    } catch (error) {
        if (request === read) undoProblem.value = error.message || "Older history could not be read.";
    } finally {
        loadingOlder.value = false;
    }
}

function undo(row, action) {
    const key = `${row.id}:${action.receipt_id}`;
    undoing.value = key;
    undoProblem.value = "";
    const pending = (async () => {
        try {
            await api.supervisorUndo(row.plan_id, action.receipt_id);
            await loadHistory();
        } catch (error) {
            undoProblem.value = error.message || "The action could not be undone.";
        } finally {
            undoing.value = "";
        }
    })();
    return trackHistoryRefresh(pending);
}

function decideProposal(row, action, decision) {
    const key = `${row.id}:${action.receipt_id}`;
    decidingProposal.value = key;
    proposalProblem.value = "";
    const pending = (async () => {
        try {
            await api.supervisorProposal(row.plan_id, action.receipt_id, decision);
            await refreshSupervisorWaitingCount();
            await loadHistory();
        } catch (error) {
            proposalProblem.value = error.message || "The proposal could not be decided.";
        } finally {
            decidingProposal.value = "";
        }
    })();
    return trackHistoryRefresh(pending);
}

watch([planId, area, tier, result], loadHistory, {immediate: true});
loadPlans();
checkOwner();
</script>

<template>
    <section class="supervisor-decisions" data-supervisor-decisions aria-labelledby="supervisor-decisions-title">
        <header class="decisions-heading">
            <div>
                <h2 id="supervisor-decisions-title">Decisions and actions</h2>
                <p>What the supervisor saw, chose and did, with its reasons and receipts.</p>
            </div>
        </header>

        <p v-if="problem" class="history-problem" role="alert" data-history-fault>{{ problem }}</p>
        <p v-if="undoProblem" class="history-problem" role="alert">{{ undoProblem }}</p>
        <p v-if="proposalProblem" class="history-problem" role="alert">{{ proposalProblem }}</p>
        <p v-if="!problem && historyStatus === 'off'" class="history-off" role="status">
            <strong>The supervisor is off.</strong> History stays readable.
        </p>

        <div class="history-filters" aria-label="History filters">
            <label>Plan
                <select v-model="planId" aria-label="Plan">
                    <option value="">All plans</option>
                    <option v-for="plan in plans" :key="plan.id" :value="String(plan.id)">
                        Plan {{ plan.id }}: {{ plan.title }}
                    </option>
                </select>
            </label>
            <label>Area
                <select v-model="area" aria-label="Area">
                    <option value="">All areas</option>
                    <option v-for="value in areas" :key="value" :value="value">{{ areaTitle(value) }}</option>
                </select>
            </label>
            <label>Tier
                <select v-model="tier" aria-label="Tier">
                    <option value="">All tiers</option>
                    <option value="1">Tier 1</option>
                    <option value="2">Tier 2</option>
                    <option value="3">Tier 3</option>
                </select>
            </label>
            <label>Result
                <select v-model="result" aria-label="Result">
                    <option value="">All results</option>
                    <option v-for="value in RESULTS" :key="value" :value="value">{{ value }}</option>
                </select>
            </label>
        </div>

        <p v-if="loading" class="history-loading" role="status">Loading decisions and actions.</p>
        <p v-else-if="!problem && !hasHistory" class="history-empty" role="status">No decisions yet.</p>
        <div v-else class="history-list">
            <article v-for="row in history" :key="row.id" class="history-row" :data-history-row="row.id">
                <header class="history-row-heading">
                    <span class="history-meta"><span class="history-meta-label">When</span>
                        <time :datetime="row.created_at">{{ when(row.created_at) }}</time>
                    </span>
                    <span class="history-meta history-woken-by"><span class="history-meta-label">Woken by</span>
                        <span>{{ row.woken_by }}</span>
                    </span>
                    <span class="history-meta history-plan"><span class="history-meta-label">Plan</span>
                        <span>{{ planTitle(row.plan_id) }}</span>
                    </span>
                    <span class="history-meta">
                        <span class="history-meta-label">Result</span>
                        <span class="history-result" :data-result="row.result">
                            {{ row.result }}<template v-if="row.quiet_count">: {{ row.quiet_count }} wake-ups</template>
                        </span>
                    </span>
                    <span class="history-meta history-cost"><span class="history-meta-label">Cost</span>
                        <span>{{ cost(row.cost) }}</span>
                    </span>
                </header>

                <dl class="history-details">
                    <div><dt>What it saw</dt><dd>{{ row.what_saw }}</dd></div>
                    <div><dt>What it chose</dt><dd>{{ row.what_chose }}</dd></div>
                    <div><dt>Why</dt><dd>{{ row.why }}</dd></div>
                </dl>

                <section class="history-feedback" :data-feedback-for="row.id" aria-label="Feedback">
                    <div class="history-feedback-choice" aria-label="Was this useful?">
                        <button type="button" data-feedback-useful :aria-pressed="row.feedback.useful === true"
                                :disabled="savingFeedback === row.id" @click="row.feedback.useful = true">Useful</button>
                        <button type="button" data-feedback-not-useful :aria-pressed="row.feedback.useful === false"
                                :disabled="savingFeedback === row.id" @click="row.feedback.useful = false">Not useful</button>
                    </div>
                    <label>Comment
                        <textarea v-model="row.feedback.comment" aria-label="Comment" maxlength="4000" />
                    </label>
                    <label>Correction
                        <textarea v-model="row.feedback.correction" aria-label="Correction" maxlength="4000" />
                    </label>
                    <div class="history-feedback-actions">
                        <button type="button" data-feedback-save :disabled="savingFeedback === row.id || row.feedback.useful === null"
                                @click="saveFeedback(row)">{{ savingFeedback === row.id ? "Saving feedback" : "Save feedback" }}</button>
                        <button v-if="owner && row.feedback.correction.trim() && row.feedback.correction === row.savedCorrection && !row.feedback.rule_id"
                                type="button" data-feedback-rule :disabled="makingRule === row.id"
                                @click="makeRule(row)">{{ makingRule === row.id ? "Adding rule" : "Turn this correction into a rule" }}</button>
                    </div>
                    <p v-if="feedbackProblem[row.id]" role="alert">{{ feedbackProblem[row.id] }}</p>
                    <p v-if="feedbackStatus[row.id]" role="status">{{ feedbackStatus[row.id] }}</p>
                </section>

                <section
                    v-for="action in row.actions"
                    :key="`${row.id}:${action.receipt_id}:${action.title}`"
                    class="history-action"
                >
                    <header>
                        <strong>{{ action.title }}</strong>
                        <span>{{ action.area }}</span>
                        <span class="history-tier">Tier {{ action.tier }}</span>
                    </header>
                    <dl v-if="action.changes?.length" class="history-changes">
                        <div v-for="change in action.changes" :key="change.field">
                            <dt>{{ change.field }}</dt>
                            <dd><span>Before</span> {{ changeValue(change.before) }}</dd>
                            <dd><span>After</span> {{ changeValue(change.after) }}</dd>
                        </div>
                    </dl>
                    <div class="history-receipt">Receipt {{ action.receipt_id }} · {{ action.receipt_status }}</div>
                    <p v-if="action.proposal_decision && firstActionForReceipt(row, action)" class="history-proposal-result">
                        {{ action.proposal_decision === "accepted" ? "Accepted" : "Declined" }}
                    </p>
                    <div v-if="owner && action.receipt_status === 'proposed' && !action.proposal_decision && firstActionForReceipt(row, action)"
                         class="history-proposal-actions">
                        <button type="button" data-proposal-decision="accept"
                                :disabled="decidingProposal === `${row.id}:${action.receipt_id}`"
                                @click="decideProposal(row, action, 'accept')">Accept</button>
                        <button type="button" data-proposal-decision="decline"
                                :disabled="decidingProposal === `${row.id}:${action.receipt_id}`"
                                @click="decideProposal(row, action, 'decline')">Decline</button>
                    </div>
                    <button
                        v-if="owner && action.tier === 1 && action.receipt_status === 'applied'"
                        type="button"
                        :disabled="!action.undo_available || undoing === `${row.id}:${action.receipt_id}`"
                        @click="undo(row, action)"
                    >{{ undoing === `${row.id}:${action.receipt_id}` ? "Undoing" : "Undo" }}</button>
                </section>
            </article>
        </div>

        <button
            v-if="nextHistoryBefore"
            type="button"
            class="history-older"
            aria-label="Load 100 older rows"
            :disabled="loadingOlder"
            @click="loadOlder"
        >{{ loadingOlder ? "Loading older rows" : "Load 100 older rows" }}</button>
    </section>
</template>

<style scoped>
.supervisor-decisions {
    display: grid;
    gap: 14px;
}

.decisions-heading,
.history-row-heading,
.history-action > header,
.history-filters {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}

.decisions-heading,
.history-row-heading {
    justify-content: space-between;
}

.decisions-heading h2 {
    margin: 0;
    font-size: 18px;
}

.decisions-heading p {
    margin: 5px 0 0;
    color: var(--text-3);
    font-size: 13px;
}

.history-filters,
.history-row,
.history-off,
.history-empty,
.history-problem {
    padding: 14px;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: var(--surface);
}

.history-filters label {
    display: grid;
    gap: 5px;
    color: var(--text-3);
    font-size: 12px;
}

.history-filters select {
    min-width: 145px;
    padding: 7px 9px;
    border: 1px solid var(--line);
    border-radius: 7px;
    background: var(--surface);
    color: var(--text);
}

.history-list {
    display: grid;
    gap: 10px;
}

.history-row-heading {
    justify-content: flex-start;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--line);
    color: var(--text-3);
    font-size: 12px;
}

.history-result {
    color: var(--text);
    font-weight: 600;
}

.history-meta {
    display: grid;
    gap: 3px;
}

.history-meta-label {
    color: var(--text-3);
    font-size: 10px;
    font-weight: 400;
    text-transform: uppercase;
}

.history-cost {
    margin-left: auto;
    color: var(--text);
    font-variant-numeric: tabular-nums;
}

.history-details,
.history-changes {
    display: grid;
    gap: 9px;
    margin: 12px 0 0;
}

.history-details > div {
    display: grid;
    grid-template-columns: 112px 1fr;
    gap: 8px;
}

.history-details dt,
.history-changes dt {
    color: var(--text-3);
    font-size: 12px;
}

.history-details dd,
.history-changes dd {
    margin: 0;
    font-size: 13px;
    overflow-wrap: anywhere;
}

.history-action {
    display: grid;
    gap: 8px;
    margin-top: 12px;
    padding: 10px 12px;
    border-left: 2px solid var(--accent);
    background: var(--surface-2);
}

.history-action > header {
    color: var(--text-3);
    font-size: 12px;
}

.history-action > header strong {
    color: var(--text);
}

.history-tier {
    color: var(--text);
}

.history-changes > div {
    display: grid;
    grid-template-columns: 95px 1fr 1fr;
    gap: 8px;
}

.history-changes dd span {
    color: var(--text-3);
}

.history-feedback {
    display: grid;
    gap: 9px;
    margin-top: 12px;
    padding: 10px 12px;
    border: 1px solid var(--line);
    border-radius: 8px;
}

.history-feedback-choice,
.history-feedback-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.history-feedback label {
    display: grid;
    gap: 5px;
    color: var(--text-3);
    font-size: 12px;
}

.history-feedback textarea {
    min-height: 54px;
    padding: 8px;
    border: 1px solid var(--line);
    border-radius: 7px;
    background: var(--surface);
    color: var(--text);
    resize: vertical;
}

.history-feedback button {
    padding: 7px 11px;
    border: 1px solid var(--line);
    border-radius: 7px;
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
}

.history-receipt,
.history-undone {
    color: var(--text-3);
    font-size: 12px;
}

.history-proposal-result {
    margin: 0;
    color: var(--text-3);
}

.history-proposal-actions {
    display: flex;
    gap: 8px;
}

.history-action button,
.history-older {
    justify-self: start;
    padding: 7px 11px;
    border: 1px solid var(--line);
    border-radius: 7px;
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
}

.history-off {
    color: var(--text-2);
}

.history-problem {
    color: var(--danger);
}

.history-empty,
.history-loading {
    color: var(--text-3);
}

@media (max-width: 640px) {
    .history-details > div,
    .history-changes > div {
        grid-template-columns: 1fr;
    }

    .history-filters label,
    .history-filters select {
        width: 100%;
    }
}
</style>
