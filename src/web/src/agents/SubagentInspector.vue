<script setup>
import {computed, ref} from "vue";
import Btn from "../kit/Btn.vue";
import Icon from "../kit/Icon.vue";
import Segmented from "../kit/Segmented.vue";
import InspectorColumn from "./InspectorColumn.vue";
import InspectorSummary from "./InspectorSummary.vue";
import InspectorTop from "./InspectorTop.vue";
import TranscriptTurns from "./TranscriptTurns.vue";
import {useTranscript} from "../composables/transcript.js";
import {ending} from "../domain/agentState.js";
import {briefOf, reportOf} from "../domain/transcript.js";
import {render} from "../text/index.js";
import "../text/all.js";
import {route} from "../route.js";
import {ago, clock} from "../format/time.js";
import {narrow} from "../platform/view.js";

const props = defineProps({
    subagent: {type: Object, required: true},
    agent: {type: Object, required: true},
    api: {type: Object, required: true},
    env: {type: String, default: ""},
});
const emit = defineEmits(["back", "close"]);
const name = computed(() => props.subagent.task || props.subagent.type || "Subagent");
const turnsView = ref(null);
const scroller = computed(() => turnsView.value && turnsView.value.scroller);
const transcript = useTranscript(() => props.agent.id, props.subagent.session, scroller, props.api);
const {turns} = transcript;
const brief = computed(() => props.subagent.brief || briefOf(turns.value)?.text || "");
const report = computed(() => (props.subagent.running ? null : reportOf(turns.value)));
const speakers = computed(() => ({agent: name.value, human: "The agent"}));

const endWord = computed(() => ending(props.subagent.status, 0).word);
const state = computed(() =>
    props.subagent.running
        ? {icon: "started", word: "Working", since: `since ${ago(props.subagent.time) || "just now"}`}
        : {icon: props.subagent.status === "failed" ? "blocked" : "done", word: endWord.value, since: `since ${ago(props.subagent.ended || props.subagent.time) || "just now"}`}
);
const moves = computed(() => [
    {word: "Started", time: clock(props.subagent.time), at: props.subagent.running ? "now" : ""},
    props.subagent.running ? {word: endWord.value, time: "", at: "later"} : {word: endWord.value, time: clock(props.subagent.ended), at: "now"},
]);
const facts = computed(() => [
    {label: "Model", value: props.subagent.model || "Its parent's model"},
    {label: "Type", value: props.subagent.type || "General"},
]);
const shown = ref("all");
const SHOWN = [
    {key: "all", label: "All"},
    {key: "messages", label: "Messages"},
];
</script>

<template>
    <div :class="['subagent-inspector', {narrow}]">
        <InspectorTop @close="emit('close')">
            <Btn small @click="emit('back')">
                <Icon name="back" :size="12" />
                Main agent
            </Btn>
            Subagents › {{ name }}
        </InspectorTop>
        <InspectorSummary :name="name" :state="state" :moves="moves" :facts="facts">
            <template #stamp>Subagent of agent {{ agent.id }}</template>
        </InspectorSummary>
        <div class="cols">
            <InspectorColumn>
                <div class="head">Brief</div>
                <div class="prose">
                    <template v-if="brief">
                        <div class="text" v-html="render(brief, {types: [], env: env || route.env})" />
                    </template>
                    <template v-else>
                        <p class="text none">Not read yet.</p>
                    </template>
                </div>
                <div class="head">
                    Report
                    <template v-if="report">
                        <span class="count">{{ clock(report.time) }}</span>
                    </template>
                </div>
                <div class="prose">
                    <template v-if="report">
                        <div class="text" v-html="render(report.text, {types: [], env: env || route.env})" />
                    </template>
                    <template v-else>
                        <p class="text none">Not written yet. The subagent hands it back when it ends.</p>
                    </template>
                </div>
            </InspectorColumn>
            <InspectorColumn title="Transcript">
                <template #end>
                    <Segmented :options="SHOWN" :value="shown" @pick="shown = $event" />
                </template>
                <TranscriptTurns ref="turnsView" :transcript="transcript" :speakers="speakers" :messages="shown === 'messages'" :env="env" />
            </InspectorColumn>
        </div>
    </div>
</template>

<style scoped>
.subagent-inspector {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
    background: var(--raised);
}

.cols {
    display: grid;
    flex: 1;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    min-height: 0;
}

.narrow .cols {
    grid-template-columns: minmax(0, 1fr);
    grid-auto-rows: minmax(0, 1fr);
}

.head {
    display: flex;
    flex: none;
    align-items: center;
    gap: 8px;
    height: 34px;
    padding: 0 16px;
    color: var(--text-2);
    font-size: 12.5px;
    font-weight: 500;
}

.prose + .head {
    margin-top: 4px;
    border-top: 1px solid var(--border);
}

.count {
    color: var(--text-4);
    font-weight: 400;
}

.prose {
    padding: 0 16px 16px;
}

.text {
    margin: 0;
    color: var(--text-2);
    overflow-wrap: anywhere;
    text-wrap: pretty;
}

.text :deep(p) {
    margin: 0 0 8px;
}

.text :deep(p:last-child) {
    margin-bottom: 0;
}

.text.none {
    color: var(--text-4);
}
</style>
