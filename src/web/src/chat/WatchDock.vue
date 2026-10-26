<script setup>
import {computed, ref, watch} from "vue";
import ChatDock from "../kit/ChatDock.vue";
import Btn from "../kit/Btn.vue";
import CloseButton from "../kit/CloseButton.vue";
import Icon from "../kit/Icon.vue";
import {store} from "../state/store.js";
import MarkIcon from "../kit/MarkIcon.vue";
import OutputLines from "../kit/OutputLines.vue";
import {useScope} from "../composables/scope.js";
import {keepDocked, undock} from "../actions/docking.js";
import {useColleague} from "../composables/colleague.js";
import {createdAt} from "../domain/row.js";
import {watchLines} from "../domain/watchStatus.js";
import {elapsed} from "../format/time.js";
import {useSharedNow} from "../composables/now.js";
import {useOutputPages} from "../composables/outputPages.js";

const SHOWN_LINES = 6;

const props = defineProps({message: {type: Object, required: true}, folded: Boolean});
const scope = useScope();
const {colleague} = useColleague();
const card = computed(() => props.message.data);
// the badge on the dock's icon and its progress bar, in the colour of the state of its run: running, passed (good) or failed (bad)
const STATE_TONES = {running: "var(--tone-work)", good: "var(--tone-good)", bad: "var(--tone-bad)"};
// the dock's icon: the terminal while its run goes, a tick once it passed, a cross once it failed
const STATE_ICONS = {running: "terminal", good: "tick", bad: "cross"};
// how the run ended, as its card reports it, or as its colour said on a card from before cards reported their outcome
const ENDED = {passed: "good", failed: "bad"};
const endedTone = computed(() => ENDED[card.value.outcome] || card.value.tone || "good");
const runState = computed(() => (card.value.ending ? endedTone.value : "running"));
const printed = computed(() => watchLines((card.value.lines?.length ? card.value.lines : [card.value.detail]).filter(Boolean)));
const lines = computed(() => printed.value.steps.slice(-SHOWN_LINES));
// what is happening now is told while the run goes on, one line for the journal and one for each plugin
const statuses = computed(() => (card.value.ending ? [] : printed.value.statuses));
const width = computed(() => `${Math.round((card.value.fraction || 0) * 100)}%`);

const now = useSharedNow();
const ranFor = computed(() => (card.value.began_at ? elapsed((card.value.ended_at || now.value) - card.value.began_at) : ""));

const opened = ref(false);
const foldedByHand = ref(false);
const shown = ref(false);
const pages = useOutputPages((...page) => scope.api.readOutput(card.value.output, ...page));

const takeDown = () => undock(scope, props.message);
// a question about this run starts in the composer with the run quoted, and the message sent refers to the run's row for the agent to read
const askedRow = computed(() => (card.value.output ? `command_outputs:${card.value.output}` : `checks:${card.value.check}`));
const askAbout = () => (store.quoting = {text: props.message.text, ref: "", refers: [askedRow.value], label: "Asking about"});

async function read() {
    if (!colleague.value && card.value.output) await pages.poll();
}

function toggle() {
    opened.value = !opened.value;
    if (opened.value) {
        shown.value = true;
        read();
    }
    if (card.value.auto_docked) keepDocked(scope, props.message);
}

watch(
    () => props.message.data,
    () => opened.value && read()
);
</script>

<template>
    <ChatDock label="Watched output" :folded="folded || foldedByHand" kind="watch-dock">
        <template #head>
            <span class="watch-dock-state" :data-state="runState" :style="{'--tone': STATE_TONES[runState]}">
                <MarkIcon :name="STATE_ICONS[runState]" />
            </span>
            <button type="button" class="watch-dock-label" :aria-expanded="opened" :title="[card.line, opened ? 'Fold the output' : 'Show the whole output'].filter(Boolean).join('\n\n')" @click="toggle">{{ message.text }}</button>
            <template v-if="card.count">
                <span class="watch-dock-figure">{{ card.count }}</span>
            </template>
            <template v-if="card.ending">
                <span class="watch-dock-ending">{{ card.ending }}</span>
            </template>
            <template v-if="ranFor">
                <span class="watch-dock-figure watch-dock-timer">{{ ranFor }}</span>
            </template>
            <button type="button" class="watch-dock-fold" :aria-expanded="!foldedByHand" @click="foldedByHand = !foldedByHand">{{ foldedByHand ? "Unfold" : "Fold" }}</button>
            <Btn kind="icon" class="watch-dock-ask" title="Ask about this" aria-label="Ask about this" @click="askAbout"><Icon name="bubble" /></Btn>
            <CloseButton title="Take the watched output down from above the chat" @click="takeDown" />
        </template>
        <template v-if="statuses.length">
            <ul class="watch-dock-statuses">
                <template v-for="status in statuses" :key="status">
                    <li>{{ status }}</li>
                </template>
            </ul>
        </template>
        <div :class="['watch-dock-more', {open: opened}]">
            <div class="watch-dock-more-inner">
                <template v-if="shown && colleague">
                    <p class="watch-dock-elsewhere">This output stays on {{ colleague }}'s machine; its card shows how it goes.</p>
                </template>
                <template v-else-if="shown && pages.loaded.value">
                    <OutputLines class="watch-dock-output" :lines="pages.lines.value" @older="pages.older" />
                </template>
                <template v-else-if="shown">
                    <ul class="watch-dock-lines">
                        <template v-for="line in lines" :key="line">
                            <li>{{ line }}</li>
                        </template>
                    </ul>
                </template>
            </div>
        </div>
        <template v-if="card.fraction > 0">
            <div class="watch-dock-bar" :data-figure-bar="card.ending ? endedTone : ''" :data-figure-began="createdAt(message)">
                <div class="watch-dock-fill" :style="{width, background: STATE_TONES[runState]}" :data-figure-progress="card.ending ? null : ''"></div>
            </div>
        </template>
    </ChatDock>
</template>

<style scoped>
.watch-dock-more {
    display: grid;
    grid-template-rows: 0fr;
    opacity: 0;
    transition:
        grid-template-rows var(--move),
        opacity var(--fade);
}

.watch-dock-more.open {
    grid-template-rows: 1fr;
    opacity: 1;
}

.watch-dock-more-inner {
    min-height: 0;
    overflow: hidden;
}

.watch-dock-fold {
    flex: none;
    padding: 2px 8px;
    border: 1px solid var(--border-2);
    border-radius: 6px;
    background: none;
    color: var(--text-2);
    font: inherit;
    font-size: 11px;
    cursor: pointer;
}

.watch-dock-fold:hover {
    color: var(--text);
    border-color: var(--border-3);
}

.watch-dock-state {
    display: flex;
    flex: none;
    justify-content: center;
    width: 16px;
    color: var(--tone);
}

.watch-dock-elsewhere {
    margin: 0;
    padding: 6px 15px 10px;
    font-size: 11px;
    color: var(--text-3);
}

.watch-dock-output {
    max-height: 240px;
    margin: 0 15px 8px;
    padding: 6px 8px;
    overflow: auto;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text-2);
    font-size: 11px;
    line-height: 1.5;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.watch-dock-label {
    flex: 1 1 auto;
    min-width: 0;
    padding: 0;
    border: none;
    background: none;
    font: inherit;
    text-align: left;
    cursor: pointer;
    overflow: hidden;
    color: var(--text);
    font-size: 12px;
    font-weight: 500;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.watch-dock-figure,
.watch-dock-ending {
    flex: none;
    color: var(--text-3);
    font-size: 11px;
    font-variant-numeric: tabular-nums;
}

.watch-dock-statuses {
    margin: 0;
    padding: 0 12px 10px 35px;
    color: var(--text-3);
    font-size: 11px;
    line-height: 1.5;
    list-style: none;
    overflow-wrap: anywhere;
}

.watch-dock-lines {
    margin: 0;
    padding: 0 12px 10px 35px;
    color: var(--text-3);
    font-family: var(--mono, monospace);
    font-size: 11px;
    line-height: 1.5;
    list-style: none;
    overflow-wrap: anywhere;
}

/* the bar lies along the card's foot, adding no height, so the title stays in the middle of the card */
.watch-dock-bar {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    height: 2px;
    border-radius: 1px;
    background: var(--border);
    overflow: hidden;
}

.watch-dock-fill {
    height: 100%;
    transition: width 0.4s ease;
}
</style>
