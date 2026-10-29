<script setup>
import {computed, ref, watch} from "vue";
import {api} from "../api/client.js";
import AgentInspector from "../agents/AgentInspector.vue";
import TranscriptInspector from "../agents/TranscriptInspector.vue";
import WorkerQueue from "../agents/WorkerQueue.vue";
import Btn from "../kit/Btn.vue";
import EmptyState from "../kit/EmptyState.vue";
import {usePoll} from "../composables/poll.js";
import {scopeOfChat, scopeIn} from "../composables/scope.js";
import {useTranscript} from "../composables/transcript.js";
import {ago, clock} from "../format/time.js";
import {roleInstanceTitle, roleInstances} from "../domain/roleInstances.js";
import {providerName} from "../domain/agents.js";
import {stateAt, workerActions, workerActivity, workerIcon, workerLine, workerMoves, workerName, workerState} from "../domain/workers.js";
import {cardinalityLine, modelLine} from "../domain/organizationFormat.js";
import {route, href} from "../route.js";
import {store} from "../state/store.js";
import {holding} from "../sync/rows.js";

const contract = ref(null);
const contractLoading = ref(true);
const contractProblem = ref("");
const snapshot = ref(null);
const instancesLoading = ref(true);
const instancesProblem = ref("");
const transcriptView = ref(null);
const key = computed(() => `${route.value.domain}/${route.value.role}`);
const selectedKey = computed(() => route.value.instance || "");

async function readContract(wanted) {
    contract.value = null;
    contractLoading.value = true;
    contractProblem.value = "";
    if (!route.value.domain || !route.value.role) {
        contractLoading.value = false;
        return;
    }
    try {
        const got = await api.organizationRole(route.value.domain, route.value.role);
        if (key.value === wanted) contract.value = got;
    } catch (error) {
        if (key.value === wanted) contractProblem.value = error.message;
    } finally {
        if (key.value === wanted) contractLoading.value = false;
    }
}

watch(key, readContract, {immediate: true});

usePoll("organization.role.instances", {
    params: () => ({domain: route.value.domain, role: route.value.role}),
    take: (got) => {
        if (got.key !== key.value) return;
        snapshot.value = got;
        instancesLoading.value = false;
        instancesProblem.value = "";
    },
    failed: (error) => {
        instancesProblem.value = error.message;
        instancesLoading.value = false;
    },
    active: () => Boolean(route.value.domain && route.value.role),
});

watch(key, () => {
    snapshot.value = null;
    instancesLoading.value = true;
    instancesProblem.value = "";
});

const instances = computed(() => (contract.value && snapshot.value ? roleInstances(contract.value, snapshot.value) : []));
const selected = computed(() => instances.value.find((instance) => instance.key === selectedKey.value) || instances.value[0] || null);
const olderWorkers = computed(() => instances.value.filter((instance) => instance.legacy));
const queue = computed(() => selected.value?.worker?.queue || []);
const task = computed(() => selected.value?.worker?.task || null);
const title = computed(() => contract.value?.title || route.value.role || "Role");
const model = computed(() => {
    const instance = selected.value;
    return instance?.worker ? workerLine(instance.worker) : instance?.agent ? [providerName(instance.agent.provider), instance.agent.model].filter(Boolean).join(" · ") : modelLine(contract.value?.models);
});
const status = computed(() => {
    const instance = selected.value;
    if (!instance) return "No instance is running";
    if (instance.kind === "seat") return "Organization plan seat · transcript only";
    if (instance.kind === "solo") return instance.agent?.doing || "Working as this Role in a solo plan";
    return workerActivity(instance.worker, instance.agent);
});

function pick(instanceKey) {
    location.hash = href.rolePage(route.value.domain, route.value.role, instanceKey);
}

function agentInfo(instance) {
    const worker = instance.worker;
    const agent = instance.agent;
    const finished = worker && workerState(worker) === "finished";
    const stateKey = worker ? (finished ? "stopped" : workerState(worker) === "running" ? "busy" : "waiting") : agent?.status === "stopped" ? "stopped" : "busy";
    const dot = worker
        ? ({running: "running", finished: "done", unfinished: "failed"})[workerState(worker)] || "queued"
        : agent?.status === "stopped" ? "done" : ["working", "busy", "compacting"].includes(agent?.status) ? "running" : "queued";
    const actions = worker ? workerActions(worker, store.people.device).filter((action) => action.key === "stop") : [];
    return {
        kind: instance.legacy ? "Older worker row" : "Role instance",
        name: instance.name,
        title: [instance.plan?.title || (instance.plan_id && `Plan ${instance.plan_id}`), task?.title || (instance.task_id && `Task ${instance.task_id}`)].filter(Boolean).join(" · "),
        state: {
            key: stateKey,
            dot,
            word: worker ? workerActivity(worker, agent) : agent?.status === "stopped" ? "Stopped" : "Working as this Role",
        },
        facts: [model.value || "Not reported", `Role ${contract.value.id}`, ...(instance.plan_id ? [`Plan ${instance.plan_id}`] : []), ...(instance.legacy ? [`Worker ${worker.id}`] : [])],
        counts: {subagents: 0, skills: Object.keys(agent?.skills_loaded || {}).length},
        link: null,
        actions,
    };
}

const selectedAgentInfo = computed(() => (selected.value ? agentInfo(selected.value) : null));
const chatScope = computed(() => {
    const instance = selected.value;
    if (instance?.kind !== "worker" || !instance.worker.session) return null;
    const client = api.in(instance.env);
    return scopeOfChat(instance.worker.session, (text) => client.act("workers", instance.worker.id, "message", {text}), client);
});
const run = (key) => {
    const instance = selected.value;
    return key === "stop" && instance?.worker
        ? api.in(instance.env).act("workers", instance.worker.id, "stop")
        : Promise.resolve();
};

watch(selected, (instance) => {
    if (!instance?.agent?.id) return;
    const hold = instance.env === api.env() ? holding : scopeIn(instance.env).holding;
    hold("agents", [instance.agent.id]).catch(() => {});
}, {immediate: true});

const scroller = computed(() => transcriptView.value?.scroller || null);
const transcripts = {
    env: () => selected.value?.env || route.value.env,
    transcript: (worker, _session, fields) => api.in(selected.value.env).workerTranscript(worker, fields),
};
const transcript = useTranscript(() => selected.value?.worker?.id || 0, "", scroller, transcripts, () => selected.value?.kind === "seat");
const transcriptState = computed(() => {
    const worker = selected.value?.worker;
    return worker ? {icon: workerIcon(worker), word: workerActivity(worker, selected.value.agent), since: `since ${ago(stateAt(worker)) || "just now"}`} : {icon: "done", word: "No worker", since: ""};
});
const transcriptParts = computed(() => {
    const worker = selected.value?.worker;
    return worker ? [{key: "brief", title: "Brief", text: worker.brief, sub: `sent at ${clock(worker.created_at)}`, none: "No brief"}] : [];
});
const transcriptFacts = computed(() => {
    const instance = selected.value;
    return instance ? [workerLine(instance.worker) || "Model not reported", ...(instance.plan_id ? [`Plan ${instance.plan_id}`] : []), ...(instance.task_id ? [`Task ${instance.task_id}`] : [])].filter(Boolean) : [];
});
const transcriptSpeakers = computed(() => ({agent: selected.value?.name || title.value, human: "The agent"}));

</script>

<template>
    <main class="role-page" aria-label="Role">
        <header class="role-management-bar">
            <div class="role-management-title">
                <h1>{{ title }}</h1>
                <p>{{ contract?.domain || route.domain }} · {{ cardinalityLine(contract?.cardinality || "") }}</p>
            </div>
            <div class="role-management-status" role="status">{{ status }}</div>
            <span class="role-management-model">{{ model }}</span>
            <Btn kind="ghost" small :href="href.role(route.domain, route.role)">Role contract</Btn>
        </header>

        <p v-if="contractProblem || instancesProblem" class="role-page-error" role="alert">{{ contractProblem || instancesProblem }}</p>
        <EmptyState v-if="contractLoading || instancesLoading" class="role-page-empty" :loading="true" title="Reading Role instances" />
        <EmptyState v-else-if="!contract" class="role-page-empty" title="Role not found">This Role is not in the organization folder.</EmptyState>
        <EmptyState v-else-if="!instances.length" class="role-page-empty" :title="`No instance of ${contract.title} is running`">
            Role instances appear here when a plan or worker starts one.
        </EmptyState>
        <template v-else>
            <label v-if="contract.cardinality === 'many'" class="role-instance-picker">
                Instance
                <select :value="selected?.key" @change="pick($event.target.value)">
                    <option v-for="instance in instances" :key="instance.key" :value="instance.key">{{ instance.legacy ? `Older worker · ${roleInstanceTitle(instance)}` : roleInstanceTitle(instance) }}</option>
                </select>
            </label>
            <section class="role-instance-layout" :class="{'with-queue': queue.length}">
                <div class="role-instance-inspector">
                    <TranscriptInspector
                        v-if="selected.kind === 'seat'"
                        ref="transcriptView"
                        :name="`${title} · ${selected.name}`"
                        :state="transcriptState"
                        :moves="workerMoves(selected.worker)"
                        :facts="transcriptFacts"
                        :parts="transcriptParts"
                        :env="selected.env"
                        :transcript="transcript"
                        :speakers="transcriptSpeakers"
                    >
                        <template #top>Role · {{ contract.domain }} · Plan {{ selected.plan_id }}</template>
                    </TranscriptInspector>
                    <EmptyState v-else-if="selected.kind === 'worker' && !selected.worker.session" title="No worker chat yet">
                        Its chat appears once the worker has a session.
                    </EmptyState>
                    <AgentInspector
                        v-else-if="selected.agent && selectedAgentInfo"
                        :key="selected.key"
                        :info="selectedAgentInfo"
                        :env="selected.env"
                        :agent="selected.agent"
                        :chat-scope="chatScope"
                        :run="run"
                    />
                    <EmptyState v-else class="role-page-empty" title="No agent chat yet">This instance has no agent session to open.</EmptyState>
                </div>
                <aside v-if="queue.length" class="role-instance-queue" aria-label="Role queue">
                    <h2>Queue</h2>
                    <WorkerQueue :queue="queue" :env="selected.env" />
                </aside>
            </section>
            <section v-if="contract.cardinality !== 'many' && olderWorkers.length" class="role-older-workers" aria-label="Older worker rows">
                <h2>Older worker rows</h2>
                <button v-for="instance in olderWorkers" :key="instance.key" type="button" @click="pick(instance.key)">
                    {{ instance.name }} · Worker {{ instance.worker.id }}
                </button>
            </section>
        </template>
    </main>
</template>

<style scoped>
.role-page {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: 12px;
    min-height: 0;
    height: 100%;
}

.role-management-bar {
    display: flex;
    flex: none;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 14px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
}

.role-management-title {
    min-width: 180px;
}

.role-management-title h1 {
    margin: 0;
    font-size: 17px;
}

.role-management-title p {
    margin: 3px 0 0;
    color: var(--text-3);
    font-size: 12px;
}

.role-management-status {
    color: var(--text-2);
    font-size: 12.5px;
}

.role-management-model {
    flex: 1;
    color: var(--text-3);
    font-size: 12px;
}

.role-page-error {
    margin: 0 16px;
    color: var(--danger);
    font-size: 12.5px;
}

.role-page-empty {
    position: relative;
    flex: 1;
    min-height: 180px;
}

.role-instance-picker {
    display: flex;
    flex: none;
    flex-direction: column;
    gap: 5px;
    max-width: 420px;
    padding: 0 16px;
    color: var(--text-2);
    font-size: 12px;
}

.role-instance-picker select {
    min-height: 34px;
    padding: 5px 8px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text);
    font: inherit;
}

.role-instance-layout {
    display: grid;
    flex: 1;
    grid-template-columns: minmax(0, 1fr);
    min-height: 300px;
}

.role-instance-layout.with-queue {
    grid-template-columns: minmax(0, 1fr) minmax(210px, 270px);
}

.role-instance-inspector {
    display: flex;
    min-width: 0;
    min-height: 0;
}

.role-instance-inspector > :deep(*) {
    flex: 1;
    min-width: 0;
}

.role-instance-queue {
    min-width: 0;
    overflow-y: auto;
    border-left: 1px solid var(--border);
}

.role-instance-queue h2,
.role-older-workers h2 {
    margin: 0;
    padding: 12px 16px 6px;
    color: var(--text-2);
    font-size: 12px;
    font-weight: 600;
}

.role-older-workers {
    display: flex;
    flex: none;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    padding: 0 12px 10px;
}

.role-older-workers h2 {
    padding: 6px 4px;
}

.role-older-workers button {
    padding: 5px 8px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg-2, var(--bg));
    color: var(--text-2);
    font: inherit;
    font-size: 12px;
    cursor: pointer;
}

@media (max-width: 700px) {
    .role-instance-layout.with-queue {
        display: flex;
        flex-direction: column;
    }

    .role-instance-queue {
        border-top: 1px solid var(--border);
        border-left: 0;
    }
}
</style>
