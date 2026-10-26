<script setup>
import {computed, ref, watch} from "vue";
import ChatDock from "../kit/ChatDock.vue";
import CloseButton from "../kit/CloseButton.vue";
import Dot from "../kit/Dot.vue";
import OutputLines from "../kit/OutputLines.vue";
import {useScope} from "../composables/scope.js";
import {undock} from "../actions/docking.js";
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
const shown = ref(false);
const pages = useOutputPages((...page) => scope.api.readOutput(card.value.output, ...page));

const takeDown = () => undock(scope, props.message);

async function read() {
    if (!colleague.value) await pages.poll();
}

function toggle() {
    opened.value = !opened.value;
    if (opened.value) {
        shown.value = true;
        read();
    }
}

watch(
    () => props.message.data,
    () => opened.value && read()
);
</script>

<template>
    <ChatDock label="Watched output" :folded="folded" kind="watch-dock">
        <template #head>
            <span class="watch-dock-state" :data-state="runState" :style="{'--tone': STATE_TONES[runState]}">
                <Dot solid :size="8" :kind="runState" :pulsing="runState === 'running'" />
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

.watch-dock-state {
    display: flex;
    flex: none;
    justify-content: center;
    width: 16px;
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
    color: var(--text-2);
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
    padding: 0 15px 8px 39px;
    color: var(--text-3);
    font-size: 11px;
    line-height: 1.5;
    list-style: none;
    overflow-wrap: anywhere;
}

.watch-dock-lines {
    margin: 0;
    padding: 0 15px 8px;
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
