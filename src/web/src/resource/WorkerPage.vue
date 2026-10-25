<script setup>
import {computed, ref, watch} from "vue";
import Btn from "../kit/Btn.vue";
import PaneGrid from "../kit/PaneGrid.vue";
import Segmented from "../kit/Segmented.vue";
import SwitchCase from "../kit/SwitchCase.vue";
import TextInput from "../kit/TextInput.vue";
import AgentInspectorBands from "../agents/AgentInspectorBands.vue";
import InspectorColumn from "../agents/InspectorColumn.vue";
import InspectorSummary from "../agents/InspectorSummary.vue";
import InspectorTop from "../agents/InspectorTop.vue";
import TranscriptTurns from "../agents/TranscriptTurns.vue";
import WorkerPoints from "../agents/WorkerPoints.vue";
import WorkerTodos from "../agents/WorkerTodos.vue";
import {useInspectorActions} from "../composables/inspectorActions.js";
import {useWorkerLayout} from "../composables/paneLayout.js";
import {useScope} from "../composables/scope.js";
import {useTranscript} from "../composables/transcript.js";
import {checkedCount, doneCount, todoTotal} from "../domain/workerTurn.js";
import {stateAt, WORKER_WORDS, workerActions, workerEnding, workerIcon, workerLine, workerMoves, workerName, workerQueueLine, workerReport, workerReportsWhen, workerReusesLine, workerState} from "../domain/workers.js";
import {ago, clock} from "../format/time.js";
import {narrow} from "../platform/view.js";
import {go, peek} from "../route.js";
import {store} from "../state/store.js";

const props = defineProps({resource: Object});
const emit = defineEmits(["close"]);
const {env, api, rows, holding} = useScope();
const name = computed(() => workerName(props.resource));
const task = computed(() => props.resource.task || {task_id: null, points: [], todos: [], proofs: []});
const held = computed(() => rows("tasks").find((row) => row.id === task.value.task_id) || null);
watch(
    () => task.value.task_id,
    (id) => id && holding("tasks", [id]),
    {immediate: true}
);

const finished = computed(() => workerState(props.resource) === "finished");
const state = computed(() => ({
    icon: workerIcon(props.resource),
    word: finished.value ? workerEnding(props.resource) : WORKER_WORDS[workerState(props.resource)],
    since: `since ${ago(stateAt(props.resource)) || "just now"}`,
}));
const worktree = (row) => (row.worktree ? (row.branch ? `Own worktree, branch ${row.branch}` : "Own worktree") : "The project's checkout");
const pool = (row) => (row.pool_request ? (row.device ? `Runs on machine ${row.device}, from request ${row.pool_request}` : `Waiting for a machine to take request ${row.pool_request}`) : "");
const facts = computed(() => {
    const row = props.resource;
    return [workerLine(row) || "Its profile's model", worktree(row), pool(row), workerReusesLine(row), workerQueueLine(row) || workerReportsWhen(row), row.retire_reason ? `Retired: ${row.retire_reason}` : ""].filter(Boolean);
});
const parts = computed(() => [
    {key: "brief", title: "Brief", text: props.resource.brief, sub: `sent at ${clock(props.resource.created_at)}`, none: "No brief"},
    {key: "report", title: "Report", text: workerReport(props.resource), sub: "written when it clocked out", none: "Report not written yet"},
]);

const checked = computed(() => checkedCount(task.value));
const unchecked = computed(() => task.value.points.length - checked.value);
const done = computed(() => doneCount(task.value));
const hasTask = computed(() => Boolean(task.value.task_id));
// the tasks waiting in the worker's queue, in the order it takes them up
const queue = computed(() => props.resource.queue || []);
const todos = computed(() => todoTotal(task.value, queue.value));

const ACTIONS = {
    send: (id, brief) => api.act("workers", id, "send", {brief}),
    stop: (id) => api.act("workers", id, "stop"),
    complete: (id) => api.act("workers", id, "complete"),
    merge: (id) => api.act("workers", id, "merge"),
    release: (id) => api.act("workers", id, "release"),
    message: (id, text) => api.act("workers", id, "message", {text}),
};
const actions = computed(() => workerActions(props.resource, store.people.device));
const {refusal, question, asking, perform, choose} = useInspectorActions(
    () => actions.value,
    (key, answer) => ACTIONS[key](props.resource.id, answer)
);
const heldBack = (action) => action.key === "merge" && unchecked.value > 0;

// The worker's own conversation, read from its transcript.
const transcripts = {env: () => api.env(), transcript: (_agent, _session, fields) => api.workerTranscript(props.resource.id, fields)};
const turnsView = ref(null);
const scroller = computed(() => turnsView.value && turnsView.value.scroller);
const transcript = useTranscript(() => "worker", "", scroller, transcripts);
const speakers = computed(() => ({agent: name.value, human: "The agent"}));
const {measured, panes, resize} = useWorkerLayout();
const TITLES = {points: "Points", transcript: "Transcript", todos: "To-dos"};
const counts = computed(() => ({points: `${checked.value} of ${task.value.points.length} checked`, todos: `${done.value} of ${todos.value} done`, transcript: ""}));

const tab = ref("points");
const tabs = computed(() => [
    {key: "points", label: "Points", count: `${checked.value} of ${task.value.points.length}`},
    {key: "transcript", label: "Transcript"},
    {key: "todos", label: "To-dos", count: `${done.value} of ${todos.value}`},
]);

const message = ref("");
const writable = computed(() => actions.value.length > 0 && !finished.value);
async function send() {
    const text = message.value.trim();
    if (!text) return;
    await perform("message", text);
    message.value = "";
}
</script>

<template>
    <div :class="['worker-page', {narrow}]">
        <InspectorTop @close="emit('close')">
            Workers › Worker {{ resource.id }}
            <Btn small class="home-link" @click="go('worker', resource.id)">Open its home view</Btn>
        </InspectorTop>
        <InspectorSummary :name="name" :state="state" :moves="workerMoves(resource)" :facts="facts" :parts="parts" :env="env">
            <template #stamp>
                <template v-if="hasTask">
                    <a href="#" class="task-link" @click.prevent="peek('tasks', task.task_id)">
                        Task {{ task.task_id }}<template v-if="held">: {{ held.title }}</template>
                    </a>
                </template>
            </template>
        </InspectorSummary>
        <template v-if="narrow && hasTask">
            <div class="tabs">
                <Segmented :options="tabs" :value="tab" @pick="tab = $event" />
            </div>
        </template>
        <template v-if="hasTask && !narrow">
            <PaneGrid class="cols" :panes="panes" :splits="measured.splits" @resize="resize">
                <template #pane="p">
                    <InspectorColumn :title="TITLES[p.pane.active]" :count="counts[p.pane.active]">
                        <SwitchCase :value="p.pane.active">
                            <template #points>
                                <WorkerPoints :task="task" :worker="resource.id" :api="api" :checking="resource.state === 'clocked out'" />
                            </template>
                            <template #transcript>
                                <TranscriptTurns ref="turnsView" :transcript="transcript" :speakers="speakers" :env="env" />
                            </template>
                            <template #todos>
                                <WorkerTodos :todos="task.todos" :queue="queue" />
                            </template>
                        </SwitchCase>
                    </InspectorColumn>
                </template>
            </PaneGrid>
        </template>
        <template v-else>
            <div class="cols">
                <template v-if="hasTask && tab === 'points'">
                    <InspectorColumn title="" :count="counts.points">
                        <WorkerPoints :task="task" :worker="resource.id" :api="api" :checking="resource.state === 'clocked out'" />
                    </InspectorColumn>
                </template>
                <template v-if="!hasTask || tab === 'transcript'">
                    <InspectorColumn :title="narrow ? '' : 'Transcript'">
                        <TranscriptTurns ref="turnsView" :transcript="transcript" :speakers="speakers" :env="env" />
                    </InspectorColumn>
                </template>
                <template v-if="hasTask && tab === 'todos'">
                    <InspectorColumn title="" :count="counts.todos">
                        <WorkerTodos :todos="task.todos" :queue="queue" />
                    </InspectorColumn>
                </template>
            </div>
        </template>
        <AgentInspectorBands :confirm="question && question.confirm" :refusal="refusal" @cancel="asking = ''" @confirmed="(answer) => perform(question.key, answer)" />
        <template v-if="actions.length || writable">
            <div :class="['bottom', {tasked: hasTask && !narrow}]">
                <div class="dock">
                    <template v-for="action in actions" :key="action.key">
                        <Btn
                            :kind="action.key === 'merge' ? 'primary' : 'ghost'"
                            :disabled="asking === action.key || heldBack(action)"
                            v-tip="action.title"
                            @click="choose(action.key)"
                        >
                            {{ action.label }}
                        </Btn>
                        <template v-if="heldBack(action)">
                            <span class="note">{{ unchecked }} unchecked</span>
                        </template>
                    </template>
                </div>
                <template v-if="writable">
                    <form class="write" @submit.prevent="send">
                        <TextInput class="message" :value="message" :placeholder="`Message to ${name}`" @input="message = $event.target.value" />
                    </form>
                </template>
            </div>
        </template>
    </div>
</template>

<style scoped>
.worker-page {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
    background: var(--raised);
}

.task-link {
    color: var(--accent-text);
    text-decoration: none;
}

.task-link:hover {
    color: var(--text);
}

.tabs {
    flex: none;
    padding: 12px 16px 4px;
}

.cols {
    display: grid;
    flex: 1;
    grid-template-columns: minmax(0, 1fr);
    min-height: 0;
    border-top: 1px solid var(--border);
}

.cols :deep(.pane) {
    background: var(--raised);
}

.bottom.tasked {
    grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr) 260px;
}

.bottom {
    display: grid;
    flex: none;
    grid-template-columns: minmax(0, 1fr);
    border-top: 1px solid var(--border);
}

.dock {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    padding: 10px 16px;
}

.note {
    color: var(--text-3);
    font-size: 12px;
}

.write {
    padding: 10px 16px 12px;
}

.message {
    width: 100%;
    height: 34px;
}

.bottom.tasked .write {
    grid-column: 2 / -1;
    border-left: 1px solid var(--border);
}

.narrow .write {
    border-top: 1px solid var(--border);
}
</style>
