<script setup>
import {computed, ref, watch} from "vue";
import Btn from "../kit/Btn.vue";
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
import {useScope} from "../composables/scope.js";
import {useTranscript} from "../composables/transcript.js";
import {checkedCount, doneCount} from "../domain/workerShift.js";
import {stateAt, WORKER_WORDS, workerActions, workerEnding, workerIcon, workerLine, workerMoves, workerName, workerReport, workerState} from "../domain/workers.js";
import {ago} from "../format/time.js";
import {narrow} from "../platform/view.js";
import {peek} from "../route.js";
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
const facts = computed(() => {
    const row = props.resource;
    return [
        {label: "Model", value: workerLine(row) || "Its profile's model"},
        {label: "Worktree", value: row.worktree ? "Its own" : "The project's checkout"},
        {label: "Files changed", value: row.files, mono: true},
        {label: "Times reused", value: row.reuse_count ? String(row.reuse_count) : ""},
        {label: "Why it was retired", value: row.retire_reason},
    ].filter((fact) => fact.value);
});
const parts = computed(() => [
    {title: "Brief", text: props.resource.brief, none: "No brief."},
    {title: "Report", text: workerReport(props.resource), none: "Not written yet. The worker writes it when it clocks out."},
]);

const checked = computed(() => checkedCount(task.value));
const unchecked = computed(() => task.value.points.length - checked.value);
const done = computed(() => doneCount(task.value));
const hasTask = computed(() => Boolean(task.value.task_id));

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
const shown = ref("all");
const SHOWN = [
    {key: "all", label: "All"},
    {key: "messages", label: "Messages"},
];

const tab = ref("points");
const tabs = computed(() => [
    {key: "points", label: "Points", count: `${checked.value} of ${task.value.points.length}`},
    {key: "transcript", label: "Transcript"},
    {key: "todos", label: "To-do list", count: `${done.value} of ${task.value.todos.length}`},
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
        <InspectorTop @close="emit('close')">Workers › Worker {{ resource.id }}</InspectorTop>
        <InspectorSummary :name="name" :state="state" :moves="workerMoves(resource)" :facts="facts" :parts="parts">
            <template #stamp>
                Worker {{ resource.id }}
                <template v-if="hasTask">
                    ·
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
        <div :class="['cols', {tasked: hasTask && !narrow}]">
            <template v-if="hasTask && (!narrow || tab === 'points')">
                <InspectorColumn :title="narrow ? '' : 'Points'" :count="`${checked} of ${task.points.length} checked`">
                    <WorkerPoints :task="task" :worker="resource.id" :api="api" :checking="resource.state === 'clocked out'" />
                </InspectorColumn>
            </template>
            <template v-if="!hasTask || !narrow || tab === 'transcript'">
                <InspectorColumn :title="narrow ? '' : 'Transcript'">
                    <template #end>
                        <Segmented :options="SHOWN" :value="shown" @pick="shown = $event" />
                    </template>
                    <TranscriptTurns ref="turnsView" :transcript="transcript" :speakers="speakers" :messages="shown === 'messages'" :env="env" />
                </InspectorColumn>
            </template>
            <template v-if="hasTask && (!narrow || tab === 'todos')">
                <InspectorColumn :title="narrow ? '' : 'To-do list'" :count="`${done} of ${task.todos.length} done`">
                    <WorkerTodos :todos="task.todos" />
                </InspectorColumn>
            </template>
        </div>
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
}

.cols.tasked,
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
