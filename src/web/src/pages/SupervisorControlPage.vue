<script setup>
import {computed, onMounted, ref} from "vue";
import {api} from "../api/client.js";
import {refreshSupervisorWaitingCount} from "../composables/navigation.js";
import {supervisorGrantChange} from "./supervisorGrantChange.js";

const WAKE_EVENTS = [
    ["failed_check", "Failed check"],
    ["stalled_task", "Stalled task"],
    ["stale_worker", "Stale worker"],
    ["message_to_supervisor", "New message"],
    ["question_to_supervisor", "Question to the supervisor"],
];
const LIMITS = [
    ["max_turns_per_day", "Turns per day"],
    ["max_input_tokens_per_turn", "Input tokens per turn"],
    ["max_output_tokens_per_turn", "Output tokens per turn"],
    ["max_provider_requests_per_turn", "Provider requests per turn"],
    ["max_turn_seconds", "Seconds per turn"],
    ["max_cost_microusd_per_day", "Daily cost cap (USD)"],
    ["max_bundles_per_project_day", "Bundles per project per day"],
    ["max_bundles_per_episode_day", "Bundles per episode per day"],
    ["max_new_diagnostics_per_episode", "New diagnostics per episode"],
];

const control = ref(null);
const plans = ref([]);
const heldTasks = ref([]);
const loading = ref(true);
const problem = ref("");
const relatedProblem = ref("");
const proposalProblem = ref("");
const proposalAction = ref("");
const saving = ref(false);
const restoreReviewed = ref(false);
const grant = computed(() => control.value?.grant);
const proposals = computed(() => control.value?.proposals || []);
const rules = computed(() => control.value?.rules || []);
const areaControls = computed(() => (control.value?.areas || []).map((area) => {
    const verbs = area.verbs.map((verb) => {
        const setting = grant.value.capabilities[verb.capability] || {on: false, mode: verb.mode || "act"};
        return {...verb, enabled: setting.on, mode: setting.mode};
    });
    const master = grant.value.capabilities[`area:${area.key}`];
    const capabilities = area.capabilities || verbs.map((verb) => verb.capability);
    const enabled = master ? master.on : capabilities.some((capability) => grant.value.capabilities[capability]?.on)
        || !area.capabilities && area.enabled;
    return {...area, enabled, verbs};
}));
const decisionCount = computed(() => control.value?.needs_decision?.length || 0);
const canTurnOn = computed(() => control.value?.status === "on" || grant.value?.paused === true);
const decisionControls = computed(() => (control.value?.needs_decision || []).map((decision) => {
    const setting = grant.value.capabilities[decision.capability] || {on: true, mode: "propose"};
    return {...decision, on: setting.on, mode: setting.mode};
}));

function rowsOf(result) {
    return Array.isArray(result) ? result : (result && result.rows) || [];
}

function copyGrant(source) {
    return {
        ...source,
        watched_plans: source.watched_plans === "all" ? "all" : [...source.watched_plans],
        capabilities: Object.fromEntries(Object.entries(source.capabilities).map(([key, value]) => [key, {...value}])),
        event_wakeups: [...source.event_wakeups],
        limits: {...source.limits},
    };
}

async function load() {
    loading.value = true;
    problem.value = "";
    relatedProblem.value = "";
    try {
        control.value = await api.supervisorControl();
    } catch (error) {
        control.value = null;
        problem.value = error.message || "Only the environment owner can see Control.";
        loading.value = false;
        return;
    }
    loading.value = false;
    try {
        const [planRows, taskRows] = await Promise.all([
            api.list("plans", {limit: 100}),
            api.list("tasks", {limit: 100}),
        ]);
        plans.value = rowsOf(planRows);
        heldTasks.value = rowsOf(taskRows).filter((task) => task.supervisor_reserved);
    } catch (error) {
        relatedProblem.value = error.message || "Plans and held tasks could not be read.";
    }
}

async function saveGrant(next) {
    if (saving.value) return;
    saving.value = true;
    problem.value = "";
    try {
        const result = await api.supervisorChange(
            supervisorGrantChange(control.value, {kind: "configure", grant: next}),
        );
        control.value.grant_version = result.grant_version;
        control.value.grant = next;
    } catch (error) {
        problem.value = error.message || "The supervisor grant could not be changed.";
    } finally {
        saving.value = false;
    }
}

function editGrant(change) {
    const next = copyGrant(grant.value);
    change(next);
    return saveGrant(next);
}

function setInterval(event) {
    const value = Number(event.target.value);
    return editGrant((next) => { next.wake_interval_minutes = value; });
}

function setEvent(key, enabled) {
    return editGrant((next) => {
        next.event_wakeups = enabled
            ? [...new Set([...next.event_wakeups, key])]
            : next.event_wakeups.filter((event) => event !== key);
    });
}

function setWatchedPlans(all) {
    return editGrant((next) => {
        next.watched_plans = all ? "all" : (next.watched_plans === "all" ? [] : next.watched_plans);
    });
}

function setPlan(planId, enabled) {
    return editGrant((next) => {
        const ids = new Set(next.watched_plans === "all" ? [] : next.watched_plans);
        if (enabled) ids.add(Number(planId));
        else ids.delete(Number(planId));
        next.watched_plans = [...ids].sort((left, right) => left - right);
    });
}

function setLimit(key, event) {
    const scale = key === "max_cost_microusd_per_day" ? 1_000_000 : 1;
    const value = Math.round(Number(event.target.value) * scale);
    if (!Number.isInteger(value) || value < 1) return;
    return editGrant((next) => { next.limits[key] = value; });
}

function limitValue(key) {
    const scale = key === "max_cost_microusd_per_day" ? 1_000_000 : 1;
    return grant.value.limits[key] / scale;
}

function setArea(area, enabled) {
    return editGrant((next) => {
        next.capabilities[`area:${area.key}`] = {on: enabled, mode: "act"};
    });
}

function setVerb(verb, field, value) {
    return editGrant((next) => {
        const current = next.capabilities[verb.capability] || {on: false, mode: verb.mode || "act"};
        next.capabilities[verb.capability] = {...current, [field]: value};
    });
}

function setDecision(decision, value) {
    return editGrant((next) => {
        next.capabilities[decision.capability] = {
            on: value !== "off",
            mode: value === "off" ? "propose" : value,
        };
    });
}

async function changeGrant(change) {
    if (saving.value) return;
    saving.value = true;
    problem.value = "";
    try {
        await api.supervisorChange(supervisorGrantChange(control.value, change));
        restoreReviewed.value = false;
        await load();
    } catch (error) {
        problem.value = error.message || "The supervisor grant could not be changed.";
    } finally {
        saving.value = false;
    }
}

function replaceGrant() {
    if (control.value.restore_review && !restoreReviewed.value) {
        problem.value = "Review the restored installation before replacing the grant.";
        return;
    }
    const change = {kind: "replace", enrollment: control.value.replacement_enrollment};
    if (control.value.restore_review) change.restore_review = control.value.restore_review;
    return changeGrant(change);
}

function turnOnOrOff() {
    return changeGrant({kind: control.value.status === "on" ? "off" : "on"});
}

async function releaseTask(task) {
    if (saving.value) return;
    saving.value = true;
    problem.value = "";
    try {
        await api.change("tasks", task.id, {supervisor_reserved: false});
        const rows = await api.list("tasks", {limit: 100});
        heldTasks.value = rowsOf(rows).filter((row) => row.supervisor_reserved);
    } catch (error) {
        problem.value = error.message || "The held task could not be released.";
    } finally {
        saving.value = false;
    }
}

async function decideProposal(proposal, decision) {
    if (proposalAction.value) return;
    proposalAction.value = `${proposal.receipt_id}:${decision}`;
    proposalProblem.value = "";
    try {
        await api.supervisorProposal(proposal.plan_id, proposal.receipt_id, decision);
        await refreshSupervisorWaitingCount();
        await load();
    } catch (error) {
        proposalProblem.value = error.message || "The proposal could not be decided.";
    } finally {
        proposalAction.value = "";
    }
}

async function removeRule(rule) {
    if (saving.value) return;
    saving.value = true;
    problem.value = "";
    try {
        await api.supervisorRemoveRule(rule.id);
        await load();
    } catch (error) {
        problem.value = error.message || "The rule could not be removed.";
    } finally {
        saving.value = false;
    }
}

function setTaskPlan(plan) {
    return grant.value.watched_plans !== "all" && grant.value.watched_plans.some((id) => Number(id) === Number(plan.id));
}

function date(value) {
    return new Date(value).toLocaleString();
}

onMounted(load);
</script>

<template>
    <section class="supervisor-control" :data-supervisor-controls="!loading && control ? '' : null" aria-labelledby="supervisor-control-title">
        <p v-if="loading" role="status">Loading Supervisor Control.</p>
        <section v-else-if="!control" data-control-denied role="alert" class="control-problem">
            <h2>Control is not available</h2>
            <p>{{ problem }}</p>
        </section>
        <template v-else>
            <header class="control-heading">
                <div>
                    <h2 id="supervisor-control-title">Control</h2>
                    <p>Set when the supervisor wakes and what it may do in this environment.</p>
                </div>
                <button type="button" :disabled="saving || grant.revoked || !canTurnOn" @click="turnOnOrOff">
                    {{ grant.revoked ? "Grant revoked" : control.status === "on" ? "Turn off" : grant.paused ? "Turn on" : "Supervisor off" }}
                </button>
            </header>

            <p v-if="problem" role="alert" class="control-problem">{{ problem }}</p>
            <p v-if="relatedProblem" role="status" class="control-note">{{ relatedProblem }}</p>
            <p class="control-status" :data-status="control.status">Supervisor {{ control.status }}</p>

            <section class="control-card" aria-labelledby="control-proposals-title" data-waiting-proposals>
                <h3 id="control-proposals-title">Waiting for you <span>{{ proposals.length }}</span></h3>
                <p v-if="proposalProblem" role="alert" class="control-problem">{{ proposalProblem }}</p>
                <p v-if="!proposals.length" class="control-note">No proposals are waiting for you.</p>
                <article v-for="proposal in proposals" :key="proposal.receipt_id" class="control-proposal"
                         :data-proposal="proposal.receipt_id">
                    <header>
                        <strong>{{ proposal.plan_title }}</strong>
                        <time :datetime="proposal.created_at">{{ date(proposal.created_at) }}</time>
                    </header>
                    <p>{{ proposal.rationale }}</p>
                    <ul>
                        <li v-for="action in proposal.actions" :key="action.title">
                            {{ action.title }} · {{ action.area }} · Tier {{ action.tier }}
                        </li>
                    </ul>
                    <div class="control-proposal-actions">
                        <button type="button" data-proposal-decision="accept"
                                :disabled="!!proposalAction" @click="decideProposal(proposal, 'accept')">Accept</button>
                        <button type="button" data-proposal-decision="decline"
                                :disabled="!!proposalAction" @click="decideProposal(proposal, 'decline')">Decline</button>
                    </div>
                </article>
            </section>

            <section class="control-card" aria-labelledby="control-rules-title" data-supervisor-rules>
                <h3 id="control-rules-title">Rules from your corrections</h3>
                <p v-if="!rules.length" class="control-note">No correction rules.</p>
                <article v-for="rule in rules" :key="rule.id" class="control-rule" :data-supervisor-rule="rule.id">
                    <p>{{ rule.text }}</p>
                    <small>{{ rule.reason }}</small>
                    <button type="button" data-rule-remove :disabled="saving" @click="removeRule(rule)">Remove the rule</button>
                </article>
            </section>

            <section class="control-card" aria-labelledby="control-wakeup-title">
                <h3 id="control-wakeup-title">When it wakes up</h3>
                <label>Wake up every
                    <select aria-label="Wake up every" :value="grant.wake_interval_minutes" :disabled="saving" @change="setInterval">
                        <option :value="15">Every 15 minutes</option>
                        <option :value="30">Every 30 minutes</option>
                        <option :value="60">Every hour</option>
                    </select>
                </label>
                <fieldset>
                    <legend>Wake up on</legend>
                    <label v-for="[key, title] in WAKE_EVENTS" :key="key">
                        <input type="checkbox" :checked="grant.event_wakeups.includes(key)" :disabled="saving"
                               @change="setEvent(key, $event.target.checked)">
                        {{ title }}
                    </label>
                </fieldset>
                <fieldset>
                    <legend>Watched plans</legend>
                    <div class="control-choice-row">
                        <button type="button" :aria-pressed="grant.watched_plans === 'all'" :disabled="saving"
                                @click="setWatchedPlans(true)">All plans</button>
                        <button type="button" :aria-pressed="grant.watched_plans !== 'all'" :disabled="saving"
                                @click="setWatchedPlans(false)">Chosen plans</button>
                    </div>
                    <div v-if="grant.watched_plans !== 'all'" class="control-plan-list">
                        <label v-for="plan in plans" :key="plan.id">
                            <input type="checkbox" :checked="setTaskPlan(plan)" :disabled="saving"
                                   @change="setPlan(plan.id, $event.target.checked)">
                            Plan {{ plan.id }}: {{ plan.title }}
                        </label>
                    </div>
                </fieldset>
            </section>

            <section class="control-card" aria-labelledby="control-limits-title">
                <h3 id="control-limits-title">Limits</h3>
                <div class="control-limit-grid">
                    <label v-for="[key, title] in LIMITS" :key="key">{{ title }}
                        <input type="number" :min="key === 'max_cost_microusd_per_day' ? '0.01' : '1'"
                               :step="key === 'max_cost_microusd_per_day' ? '0.01' : '1'"
                               :aria-label="title" :value="limitValue(key)" :disabled="saving"
                               @change="setLimit(key, $event)">
                    </label>
                </div>
            </section>

            <section class="control-card" aria-labelledby="control-areas-title">
                <h3 id="control-areas-title">What it may do, by area</h3>
                <div class="control-area-grid">
                    <article v-for="area in areaControls" :key="area.key" class="control-area" data-capability-area :data-area="area.key">
                        <header>
                            <label><input type="checkbox" :checked="area.enabled" :disabled="saving"
                                          :aria-label="`Enable ${area.title}`" @change="setArea(area, $event.target.checked)">
                                <strong>{{ area.title }}</strong></label>
                            <span v-if="!area.verbs.length" class="control-tier-only">All tier 3</span>
                        </header>
                        <div v-for="verb in area.verbs" :key="verb.capability" class="control-verb">
                            <span>{{ verb.title }}</span>
                            <span class="control-tier">Tier {{ verb.tier }}</span>
                            <label class="control-verb-on"><input type="checkbox" :checked="verb.enabled" :disabled="saving"
                                :aria-label="`On: ${verb.title}`" @change="setVerb(verb, 'on', $event.target.checked)">On</label>
                            <select :aria-label="`${verb.title} mode`" :value="verb.mode" :disabled="saving || verb.tier === 3"
                                    @change="setVerb(verb, 'mode', $event.target.value)">
                                <option value="propose">Proposes</option>
                                <option value="act">Acts</option>
                            </select>
                        </div>
                        <p v-if="area.note" class="control-note">{{ area.note }}</p>
                    </article>
                </div>
            </section>

            <section class="control-decision" aria-labelledby="control-decision-title">
                <h3 id="control-decision-title">Needs your decision <span>Tier 3</span></h3>
                <p>Choose what the supervisor may do for each tier 3 verb. Changing its own grant: <strong>Never allowed</strong>.</p>
                <ul>
                    <li v-for="item in decisionControls.slice(0, 5)" :key="item.capability">
                        <span class="decision-title">{{ item.title }} <small>{{ item.area }}</small></span>
                        <select :aria-label="`Decision: ${item.title}`" :value="!item.on ? 'off' : item.mode" :disabled="saving"
                                @change="setDecision(item, $event.target.value)">
                            <option value="off">Not allowed</option>
                            <option value="propose">Proposes only</option>
                            <option value="act">May act</option>
                        </select>
                    </li>
                </ul>
                <details v-if="decisionCount > 5">
                    <summary>Show all {{ decisionCount }} tier 3 verbs</summary>
                    <ul>
                        <li v-for="item in decisionControls" :key="item.capability">
                            <span class="decision-title">{{ item.title }} <small>{{ item.area }}</small></span>
                            <select :aria-label="`Decision: ${item.title}`" :value="!item.on ? 'off' : item.mode" :disabled="saving"
                                    @change="setDecision(item, $event.target.value)">
                                <option value="off">Not allowed</option>
                                <option value="propose">Proposes only</option>
                                <option value="act">May act</option>
                            </select>
                        </li>
                    </ul>
                </details>
            </section>

            <section class="control-card" aria-labelledby="control-held-title">
                <h3 id="control-held-title">Waiting for you</h3>
                <p v-if="!heldTasks.length" class="control-note">No held tasks.</p>
                <article v-for="task in heldTasks" :key="task.id" class="control-held-task">
                    <span><strong>Task {{ task.id }}</strong> · {{ task.title }} · plan {{ task.plan_id }}</span>
                    <button type="button" :disabled="saving" @click="releaseTask(task)">Release held task</button>
                </article>
            </section>

            <section v-if="control.restore_review" class="control-review" aria-labelledby="control-review-title">
                <h3 id="control-review-title">Review restored installation</h3>
                <p>Confirm the restored installation evidence before replacing the grant.</p>
                <dl>
                    <dt>Installation epoch</dt><dd>{{ control.restore_review.epoch }}</dd>
                    <dt>Evidence watermark</dt><dd>{{ control.restore_review.evidence_watermark_ms ?? "Unavailable" }}</dd>
                    <dt>Evidence RPO gap</dt><dd>{{ control.restore_review.evidence_rpo_gap_ms ?? "Unavailable" }}</dd>
                </dl>
                <label><input v-model="restoreReviewed" type="checkbox" :disabled="saving">
                    {{ control.restore_review.accept_unavailable_evidence ? "I accept that restoration evidence is unavailable." : "I reviewed the restored installation evidence." }}
                </label>
            </section>

            <section class="control-card" aria-labelledby="control-grant-title">
                <h3 id="control-grant-title">Grant</h3>
                <p>Valid until {{ date(grant.valid_until_ms) }}</p>
                <p class="control-note">Replacing rotates the grant credential. The credential is never shown here.</p>
                <div class="control-actions">
                    <button type="button" :disabled="saving || grant.revoked" @click="replaceGrant">Replace grant</button>
                    <button type="button" class="control-revoke" :disabled="saving || grant.revoked" @click="changeGrant({kind: 'revoke'})">Revoke grant</button>
                </div>
                <p class="control-note">Only the environment owner can change the supervisor.</p>
            </section>
        </template>
    </section>
</template>

<style scoped>
.supervisor-control { display: grid; gap: 14px; }
.control-heading, .control-area header, .control-held-task, .control-actions, .control-choice-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.control-heading h2, .control-heading p, .control-card h3, .control-decision h3, .control-review h3 { margin: 0; }
.control-heading p, .control-note, .control-card > p, .control-decision > p, .control-review > p { color: var(--text-3); font-size: 13px; }
.control-card, .control-decision, .control-review { border: 1px solid var(--border); border-radius: 10px; background: var(--panel, var(--side)); padding: 16px; }
.control-card { display: grid; gap: 14px; }
.control-card label, .control-review label { display: flex; align-items: center; gap: 8px; }
.control-card > label { justify-content: space-between; max-width: 400px; }
.control-card select, .control-card input[type="number"] { min-height: 34px; border: 1px solid var(--border); border-radius: 7px; background: var(--background); color: var(--text); padding: 5px 9px; }
.control-card fieldset { border: 0; border-top: 1px solid var(--border); padding: 12px 0 0; display: flex; flex-wrap: wrap; gap: 12px 20px; }
.control-card legend { padding-right: 8px; font-weight: 600; }
.control-proposal { display: grid; gap: 8px; padding-top: 12px; border-top: 1px solid var(--border); }
.control-proposal header, .control-proposal-actions { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.control-proposal time { color: var(--text-3); font-size: 12px; }
.control-proposal p, .control-proposal ul { margin: 0; }
.control-proposal ul { padding-left: 20px; }
.control-proposal-actions { justify-content: flex-start; }
.control-rule { display: grid; gap: 8px; padding-top: 12px; border-top: 1px solid var(--border); }
.control-rule p, .control-rule small { margin: 0; }
.control-rule small { color: var(--text-3); }
.control-choice-row { justify-content: flex-start; }
.control-choice-row button[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); }
.control-plan-list { display: grid; gap: 8px; flex-basis: 100%; }
.control-limit-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.control-limit-grid label { display: grid; align-items: start; font-size: 13px; }
.control-area-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.control-area { border: 1px solid var(--border); border-radius: 8px; padding: 10px; min-width: 0; }
.control-area header { padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.control-tier, .control-tier-only, .control-decision h3 span, .control-decision li b { color: var(--text-3); font-size: 11px; }
.control-verb { display: grid; grid-template-columns: minmax(0, 1fr) auto auto auto; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
.control-verb-on { white-space: nowrap; }
.control-verb select { max-width: 110px; }
.control-note { margin: 8px 0 0; }
.control-decision { border-color: var(--danger, #b33); }
.control-decision h3 { display: flex; gap: 8px; align-items: center; }
.control-decision ul { padding-left: 20px; display: grid; gap: 7px; }
.control-decision li { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.control-decision .decision-title { color: var(--text); margin: 0; }
.control-decision .decision-title small { color: var(--text-3); margin-left: 8px; }
.control-decision summary { cursor: pointer; }
.control-held-task { padding-top: 10px; border-top: 1px solid var(--border); }
.control-review { border-color: var(--accent); }
.control-review dl { display: grid; grid-template-columns: max-content 1fr; gap: 7px 12px; font-size: 13px; }
.control-review dt { color: var(--text-3); }
.control-review dd { margin: 0; }
.control-actions { justify-content: flex-start; padding-top: 12px; }
.control-revoke { color: var(--danger, #b33); }
.control-problem { color: var(--danger, #b33); }
.control-status { text-transform: capitalize; }
@media (max-width: 760px) {
    .control-limit-grid, .control-area-grid { grid-template-columns: 1fr; }
    .control-heading, .control-held-task { align-items: flex-start; flex-direction: column; }
    .control-verb { grid-template-columns: minmax(0, 1fr) auto; }
}
</style>
