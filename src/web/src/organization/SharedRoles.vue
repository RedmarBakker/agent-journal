<script setup>
import {computed, onMounted, ref} from "vue";
import {api} from "../api/client.js";
import {usePoll} from "../composables/poll.js";
import {useSharedNow} from "../composables/now.js";
import {clock, span} from "../format/time.js";
import {seconds} from "../domain/row.js";
import {workerState} from "../domain/workers.js";
import {peekThere} from "../route.js";
import EmptyState from "../kit/EmptyState.vue";
import OrganizationRolePanel from "../pages/OrganizationRolePanel.vue";

const RUNNING_ROLE_STATES = new Set(["dispatched", "clocked in", "clocked out", "ended without clocking out", "reported"]);
const RECENT_JOBS = 5;
const organization = ref(null);
const organizationLoading = ref(true);
const organizationProblem = ref("");
const snapshot = ref(null);
const instancesLoading = ref(true);
const instancesProblem = ref("");
const selectedKey = ref("");
const contract = ref(null);
const contractLoading = ref(false);
const contractProblem = ref("");
const now = useSharedNow();
let contractRequest = 0;

const journalRoles = computed(() => (organization.value?.domains || []).flatMap((domain) =>
    (domain.roles || []).filter((role) => role.cardinality === "journal").map((role) => ({domain, role, key: `${domain.id}/${role.id}`}))
));

async function readOrganization() {
    try {
        organization.value = await api.organization();
        organizationProblem.value = "";
    } catch (error) {
        organizationProblem.value = error.message;
    } finally {
        organizationLoading.value = false;
    }
}

onMounted(readOrganization);

usePoll("organization.roles.shared", {
    params: () => ({roles: journalRoles.value.map(({role}) => role.id)}),
    take: (got) => {
        snapshot.value = got;
        instancesLoading.value = false;
        instancesProblem.value = "";
    },
    failed: (error) => {
        instancesProblem.value = error.message;
        instancesLoading.value = false;
    },
    active: () => journalRoles.value.length > 0,
});

const tasksByKey = computed(() => new Map((snapshot.value?.tasks || []).map((task) => [`${task.environment}:${task.id}`, task])));
const plansByKey = computed(() => new Map((snapshot.value?.plans || []).map((plan) => [`${plan.environment}:${plan.id}`, plan])));
const rows = computed(() => journalRoles.value.map((item) => {
    const worker = (snapshot.value?.workers || []).find((row) => row.role === item.role.id && RUNNING_ROLE_STATES.has(row.state)) || null;
    const taskAt = (id) => id ? tasksByKey.value.get(`${worker?.environment}:${id}`) || null : null;
    const current = taskAt(worker?.task?.task_id);
    const queue = (worker?.queue || []).map((task) => ({...task, detail: taskAt(task.id)}));
    const recent = (worker?.worked || []).slice(-RECENT_JOBS).reverse().map((job) => ({
        ...job,
        environment: worker.environment,
        detail: taskAt(job.id),
    }));
    return { ...item, worker, current, queue, recent, running: Boolean(worker && workerState(worker) === "running") };
}));
const selected = computed(() => rows.value.find((row) => row.key === selectedKey.value) || null);

function planFor(environment, task) {
    return task?.plan_id ? plansByKey.value.get(`${environment}:${task.plan_id}`) || null : null;
}

function planLine(environment, task) {
    if (!task) return "Plan details not reported";
    if (!task.plan_id) return "No plan";
    const plan = planFor(environment, task);
    return plan?.title ? `Plan ${task.plan_id}: ${plan.title}` : `Plan ${task.plan_id}`;
}

function driverLine(environment, task) {
    const plan = planFor(environment, task);
    return plan ? [plan.driver, plan.driver_agent].filter(Boolean).join(" · ") || "Not reported" : "Not reported";
}

function startedAt(task) {
    const at = seconds(task?.started_at);
    return at ? `Started ${clock(at)}` : "Start time not reported";
}

// Queueing delegates the task and updates its served updated_at timestamp; the worker queue does not expose its link timestamp.
function waited(task) {
    const at = seconds(task?.updated_at);
    return at ? `${span(Math.max(0, now.value - at))} · since ${clock(at)}` : "Not reported";
}

function openTask(environment, id) {
    if (id) peekThere(environment, "tasks", id);
}

async function openRole(row) {
    selectedKey.value = row.key;
    contract.value = null;
    contractProblem.value = "";
    contractLoading.value = true;
    const request = ++contractRequest;
    try {
        const detail = await api.organizationRole(row.domain.id, row.role.id);
        if (selectedKey.value === row.key && contractRequest === request) contract.value = detail;
    } catch (error) {
        if (selectedKey.value === row.key && contractRequest === request) contractProblem.value = error.message;
    } finally {
        if (contractRequest === request) contractLoading.value = false;
    }
}

function closeRole() {
    contractRequest += 1;
    selectedKey.value = "";
    contract.value = null;
    contractProblem.value = "";
    contractLoading.value = false;
}
</script>

<template>
    <main class="shared-roles-page" aria-label="Shared Roles">
        <header class="shared-roles-head">
            <div>
                <h1>Shared Roles</h1>
                <p>One worker shared across all plans</p>
            </div>
        </header>

        <p v-if="organizationProblem || instancesProblem" class="shared-roles-error" role="alert">{{ organizationProblem || instancesProblem }}</p>
        <EmptyState v-if="organizationLoading || (journalRoles.length > 0 && instancesLoading)" :loading="true" title="Reading Shared Roles" />
        <EmptyState v-else-if="!organization" title="Organization not available">The organization folder could not be read.</EmptyState>
        <EmptyState v-else-if="!journalRoles.length" title="No shared Roles">Roles with journal cardinality appear here.</EmptyState>
        <EmptyState v-else-if="!snapshot" title="Role status unavailable">Shared Role status could not be read.</EmptyState>
        <section v-else class="shared-roles-table-wrap" aria-label="Journal-cardinality Roles">
            <table class="shared-roles-table">
                <thead>
                    <tr><th>Role</th><th>Status</th><th>Current job</th><th>Queue</th></tr>
                </thead>
                <tbody>
                    <tr v-for="row in rows" :key="row.key">
                        <th scope="row">
                            <button class="shared-role-open" type="button" @click="openRole(row)">
                                <span>{{ row.role.title }}</span>
                                <small>{{ row.domain.title }}</small>
                            </button>
                        </th>
                        <td><span :class="['shared-role-state', row.running ? 'running' : 'idle']">{{ row.running ? "Running" : "Idle" }}</span></td>
                        <td>
                            <template v-if="row.worker?.task?.task_id">
                                <button class="shared-task-link" type="button" @click="openTask(row.worker.environment, row.worker.task.task_id)">
                                    Task {{ row.worker.task.task_id }}: {{ row.current?.title || "details not reported" }}
                                </button>
                                <span class="shared-job-subline">{{ planLine(row.worker.environment, row.current) }} · {{ startedAt(row.current) }}</span>
                            </template>
                            <span v-else class="shared-muted">No current job</span>
                        </td>
                        <td>
                            <ul v-if="row.queue.length" class="shared-queue-list">
                                <li v-for="queued in row.queue" :key="queued.id" class="shared-queue-job">
                                    <button class="shared-task-link" type="button" @click="openTask(row.worker.environment, queued.id)">Task {{ queued.id }}: {{ queued.detail?.title || queued.title }}</button>
                                    <span class="shared-job-subline">{{ planLine(row.worker.environment, queued.detail) }}</span>
                                    <span class="shared-job-subline">Driver: {{ driverLine(row.worker.environment, queued.detail) }}</span>
                                    <span class="shared-job-subline">Waited: {{ waited(queued.detail) }}</span>
                                </li>
                            </ul>
                            <span v-else class="shared-muted">No jobs queued</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </section>

        <OrganizationRolePanel
            v-if="selectedKey"
            :role="contract"
            :loading="contractLoading"
            :problem="contractProblem"
            @close="closeRole"
        >
            <template #after-contract>
                <section class="role-section shared-recent-jobs">
                    <h3>Recent jobs</h3>
                    <ul v-if="selected?.recent.length">
                        <li v-for="job in selected.recent" :key="job.id">
                            <button class="shared-task-link" type="button" @click="openTask(job.environment, job.id)">Task {{ job.id }}: {{ job.title }}</button>
                            <span class="shared-job-subline">Outcome: {{ job.detail?.outcome || job.state }}</span>
                        </li>
                    </ul>
                    <p v-else class="role-none">No recent jobs are reported.</p>
                </section>
            </template>
        </OrganizationRolePanel>
    </main>
</template>

<style scoped>
.shared-roles-page {
    display: flex;
    flex-direction: column;
    gap: 14px;
    min-width: 0;
    min-height: 0;
    height: 100%;
    padding: 16px 20px 28px;
}

.shared-roles-head {
    flex: none;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

.shared-roles-head h1 {
    margin: 0;
    font-size: 20px;
}

.shared-roles-head p {
    margin: 5px 0 0;
    color: var(--text-3);
    font-size: 12.5px;
}

.shared-roles-error {
    margin: 0;
    color: var(--danger);
    font-size: 12.5px;
}

.shared-roles-table-wrap {
    min-width: 0;
    overflow: auto;
}

.shared-roles-table {
    width: 100%;
    min-width: 850px;
    border-collapse: collapse;
    text-align: left;
}

.shared-roles-table th,
.shared-roles-table td {
    padding: 11px 12px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}

.shared-roles-table thead th {
    position: sticky;
    top: 0;
    background: var(--bg);
    color: var(--text-3);
    font-size: 11.5px;
    font-weight: 600;
}

.shared-role-open {
    display: flex;
    flex-direction: column;
    gap: 3px;
    padding: 0;
    border: 0;
    background: none;
    color: var(--accent-text);
    font: inherit;
    font-weight: 600;
    text-align: left;
    cursor: pointer;
}

.shared-role-open:hover,
.shared-task-link:hover {
    color: var(--text);
    text-decoration: underline;
}

.shared-role-open small {
    color: var(--text-3);
    font-size: 11.5px;
    font-weight: 400;
}

.shared-role-state {
    display: inline-flex;
    padding: 3px 7px;
    border-radius: 999px;
    font-size: 11.5px;
}

.shared-role-state.running {
    background: var(--accent);
    color: var(--bg);
}

.shared-role-state.idle {
    background: var(--bg-2);
    color: var(--text-2);
}

.shared-task-link {
    padding: 0;
    border: 0;
    background: none;
    color: var(--accent-text);
    font: inherit;
    text-align: left;
    cursor: pointer;
}

.shared-job-subline {
    display: block;
    margin-top: 4px;
    color: var(--text-3);
    font-size: 11.5px;
    font-weight: 400;
}

.shared-muted {
    color: var(--text-4);
    font-size: 12px;
}

.shared-queue-list {
    display: grid;
    gap: 10px;
    margin: 0;
    padding: 0;
    list-style: none;
}

.shared-queue-job + .shared-queue-job {
    padding-top: 9px;
    border-top: 1px solid var(--border);
}

.shared-recent-jobs ul {
    display: grid;
    gap: 8px;
    margin: 0;
    padding-left: 19px;
}
</style>
