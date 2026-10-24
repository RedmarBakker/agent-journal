<script setup>
import {computed, ref} from "vue";
import Btn from "../kit/Btn.vue";
import Icon from "../kit/Icon.vue";
import InspectorColumn from "./InspectorColumn.vue";
import InspectorSummary from "./InspectorSummary.vue";
import InspectorTop from "./InspectorTop.vue";
import TranscriptTurns from "./TranscriptTurns.vue";
import {useTranscript} from "../composables/transcript.js";
import {ending} from "../domain/agentState.js";
import {briefOf, reportOf} from "../domain/transcript.js";
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
const facts = computed(() => [props.subagent.model || "Its parent's model", props.subagent.type ? `${props.subagent.type} subagent` : "General subagent"]);
const parts = computed(() => [
    {key: "brief", title: "Brief", text: brief.value, sub: "", none: "Brief not read yet"},
    {key: "report", title: "Report", text: report.value ? report.value.text : "", sub: report.value ? `handed back at ${clock(report.value.time)}` : "", none: "Report not written yet"},
]);
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
        <InspectorSummary :name="name" :state="state" :moves="moves" :facts="facts" :parts="parts" :env="env">
            <template #stamp>Subagent of agent {{ agent.id }}</template>
        </InspectorSummary>
        <div class="cols">
            <InspectorColumn title="Transcript">
                <TranscriptTurns ref="turnsView" :transcript="transcript" :speakers="speakers" :env="env" />
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
    grid-template-columns: minmax(0, 1fr);
    min-height: 0;
    border-top: 1px solid var(--border);
}
</style>
