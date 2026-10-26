<script setup>
import {computed, ref, useAttrs} from "vue";
import Icon from "./Icon.vue";
import MarkIcon from "./MarkIcon.vue";
import TextDisplay from "./TextDisplay.vue";
import {clock, elapsed, span} from "../format/time.js";
import {useSharedNow} from "../composables/now.js";
import {useMarkMotion} from "../composables/markMotion.js";

defineOptions({inheritAttrs: false});
const props = defineProps({mark: {type: Object, required: true}, open: {type: Boolean, default: undefined}});

const attrs = useAttrs();
const passed = computed(() => Object.fromEntries(Object.entries(attrs).filter(([name]) => name !== "onClick")));
// a mark is one line: its second line shows once a click opens it, and a second click folds it again; a mark given `open` is opened by its owner
const expanded = ref(false);
const hasSecondLine = computed(() => Boolean(props.mark.detail || props.mark.command || props.mark.body));
const owned = computed(() => props.open !== undefined);
const wanted = computed(() => (owned.value ? !props.open : hasSecondLine.value && !expanded.value));
const tag = computed(() => (attrs.onClick || hasSecondLine.value || owned.value ? "button" : "span"));
const root = ref(null);
const {folded, phase} = useMarkMotion(root, () => wanted.value);

function clicked(event) {
    if (wanted.value && !owned.value) {
        expanded.value = true;
        return;
    }
    if (attrs.onClick) attrs.onClick(event);
    else expanded.value = false;
}
// how a mark's work ended, where it reports it: an ended mark whose state is a failure is red, any other ended mark green
const FAILED_STATES = ["failed", "unfinished", "stopped"];
const outcome = computed(() => props.mark.tone || (props.mark.ended ? (FAILED_STATES.includes(props.mark.state) ? "danger" : "good") : ""));
// the colour of a mark's icon: its outcome's where it has one, else its group's, which says whose mark it is
const shade = computed(() => {
    if (props.mark.color) return props.mark.color;
    if (props.mark.asks) return "var(--asks)";
    if (outcome.value) return `var(--tone-${outcome.value})`;
    return props.mark.group ? `var(--group-${props.mark.group})` : "";
});
// a mark's progress bar is drawn in the mark's own colour, and in the working colour on a mark with none
const barShade = computed(() => shade.value || "var(--tone-work)");
// a run's bar shows while the run is active: a process or watch card that has ended, finished or failed, or any ended mark, has none
const running = computed(() => !props.mark.ending && !props.mark.ended);
// a running card whose reader counts no progress shows how long its run has gone, in place of a bar nobody can work out
const now = useSharedNow();
const ranFor = computed(() => (props.mark.began_at && running.value && !props.mark.figure && !props.mark.counting ? elapsed(now.value - props.mark.began_at) : ""));
// how long the work a mark stands for has run: counting up while it runs, and once it ended for how long it ran
const took = computed(() => {
    const {started, ended} = props.mark;
    if (!started) return ranFor.value;
    return ended ? `ran ${span(ended - started, true)}` : span(now.value - started, true);
});
// how much a mark matters, which its shape says: a failure, a warning or a request for the user is filled, work still running is
// outlined, and an event or work that ended well is a quiet line
const ATTENTION_TONES = ["bad", "danger", "warn"];
const weight = computed(() => {
    if (ATTENTION_TONES.includes(outcome.value) || props.mark.asks) return "attention";
    if (running.value && (props.mark.active || props.mark.figure || props.mark.counting || props.mark.began_at || (props.mark.started && !props.mark.ended))) return "process";
    return "event";
});
const FAILED_TONES = ["bad", "danger"];
const failed = computed(() => FAILED_TONES.includes(outcome.value));
// the sign at the end of a mark: a spinner while its work runs, a tick once it passed, a cross once it failed
const sign = computed(() => {
    if (weight.value === "process") return "running";
    if (failed.value) return "cross";
    return outcome.value === "good" ? "tick" : "";
});
const status = computed(() => Boolean(props.mark.figure || took.value || props.mark.docked || sign.value));
const hover = computed(() => [props.mark.title, props.mark.time ? clock(props.mark.time) : ""].filter(Boolean).join(" · "));
const tint = computed(() => ({
    ...(shade.value ? {"--mark": shade.value} : {}),
    ...(props.mark.depth ? {"--depth": props.mark.depth} : {}),
}));
</script>

<template>
    <component
        :is="tag"
        v-bind="passed"
        :type="tag === 'button' ? 'button' : undefined"
        ref="root"
        :class="['mark', `w-${weight}`, phase, {failed, struck: mark.struck, worked: mark.worker, tinted: shade, console: mark.command, nested: mark.depth > 0}]"
        :style="tint"
        :title="hover"
        :data-figure-mark="mark.key"
        :data-folded="folded ? '' : null"
        :data-open="owned && open ? '' : null"
        @click="clicked"
    >
        <template v-if="mark.markIcon">
            <MarkIcon class="ico" :name="mark.markIcon" />
        </template>
        <template v-else>
            <Icon :name="mark.icon || 'dot'" />
        </template>
        <template v-if="mark.worker">
            <span class="worker">{{ mark.worker }}</span>
        </template>
        <span class="head">
            <TextDisplay :text="mark.label" inline :row-names="false" />
            <template v-if="mark.name">
                <strong>{{ mark.name }}</strong>
            </template>
        </span>
        <template v-if="status">
            <span class="status">
                <template v-if="mark.figure">
                    <span class="figure">{{ mark.figure }}</span>
                </template>
                <template v-if="took">
                    <span class="ran-for">{{ took }}</span>
                </template>
                <template v-if="mark.docked">
                    <span>In the dock</span>
                </template>
                <template v-if="sign === 'running'">
                    <span class="spin" aria-label="Still running"></span>
                </template>
                <template v-else-if="sign">
                    <MarkIcon class="sign" :name="sign" />
                </template>
            </span>
        </template>
        <template v-if="(mark.figure || mark.counting) && running">
            <span class="progress" :style="{width: `${Math.round((mark.fraction || 0) * 100)}%`, background: barShade}"></span>
        </template>
        <template v-if="mark.settled">
            <span class="settled">{{ mark.settled }}</span>
        </template>
        <template v-if="mark.detail && !folded">
            <TextDisplay class="detail" :text="mark.detail" inline :row-names="false" />
        </template>
        <template v-if="mark.body && !folded">
            <div class="detail body">
                <template v-if="mark.bodyLabel">
                    <p class="body-label">{{ mark.bodyLabel }}</p>
                </template>
                <TextDisplay :text="mark.body" :row-names="false" />
            </div>
        </template>
        <template v-if="mark.command && !folded">
            <code class="detail command" :title="mark.command">{{ mark.command }}</code>
        </template>
        <template v-if="mark.card">
            <TextDisplay class="card" :text="mark.card" :row-names="false" />
        </template>
        <slot :shown="!folded" />
    </component>
</template>

<style scoped>
.mark.nested {
    position: relative;
    margin-left: calc(var(--depth) * 18px);
    overflow: visible;
}

.mark.nested::before {
    content: "";
    position: absolute;
    top: -3px;
    bottom: -3px;
    left: -8px;
    width: 1px;
    background: var(--border-3);
}

.mark {
    display: inline-grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    column-gap: 7px;
    row-gap: 1px;
    align-items: center;
    max-width: 100%;
    padding: 2px 6px;
    border: 1px solid transparent;
    border-radius: 7px;
    background: none;
    color: var(--text-3);
    font: inherit;
    font-size: 11.5px;
    line-height: 1.45;
    text-align: left;
    transition:
        background 0.15s ease,
        border-color 0.15s ease;
}

/* work still running is outlined */
.mark.w-process {
    padding: 3px 9px;
    border-color: var(--border-2);
}

/* what needs the user, a failure, a warning or a request, is filled in its colour */
.mark.w-attention {
    padding: 5px 10px;
    border-color: color-mix(in srgb, var(--mark, var(--danger)) 42%, var(--border-2));
    background: color-mix(in srgb, var(--mark, var(--danger)) 8%, transparent);
    color: var(--text-2);
}

button.mark {
    cursor: pointer;
}

.mark.worked {
    grid-template-columns: auto auto minmax(0, 1fr) auto;
}

/* an opened mark grows wider to the room its contents need */
.mark[data-open],
.mark:not([data-folded]):has(.body) {
    width: 560px;
}

.mark[data-open] .head,
.mark[data-open] .head :deep(.md) {
    white-space: normal;
}

/* while a mark opens or closes (composables/markMotion.js) its contents fade out and stay out until it has its new size, so no text
   wraps as it moves; its top row stays */
.mark > :not(.ico, .head, .worker, .status, .progress) {
    transition: opacity 0.16s ease;
}

.mark.leaving > :not(.ico, .head, .worker, .status, .progress) {
    opacity: 0;
    transition-duration: 0.12s;
}

.mark.resizing {
    overflow: hidden;
}

.mark.resizing > :not(.ico, .head, .worker, .status, .progress) {
    visibility: hidden;
    opacity: 0;
}

.mark.resizing .head,
.mark.resizing .head :deep(.md) {
    white-space: nowrap;
}

.mark.entering > :not(.ico, .head, .worker, .status, .progress) {
    animation: arrive 0.16s ease;
}

@keyframes arrive {
    from {
        opacity: 0;
    }
}

button.mark.w-event:hover {
    background: var(--hover);
}

.mark .ico {
    align-self: start;
    width: 13px;
    height: 13px;
    margin-top: 2px;
}

.mark.tinted .ico {
    color: var(--mark);
}

.mark:has(.progress) {
    position: relative;
    overflow: hidden;
}

/* the status at the end of a mark: its figure, how long it ran, whether it is in the dock, and its sign */
.status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding-left: 4px;
    color: var(--text-4);
    font-size: 10.5px;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
}

.status .sign {
    width: 11px;
    height: 11px;
    color: var(--mark, var(--text-3));
    stroke-width: 1.8;
}

.spin {
    width: 9px;
    height: 9px;
    border: 1.5px solid color-mix(in srgb, var(--mark, var(--tone-work)) 30%, transparent);
    border-top-color: var(--mark, var(--tone-work));
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.mark.failed {
    border-color: color-mix(in srgb, var(--danger) 48%, var(--border-2));
    background: color-mix(in srgb, var(--danger) 9%, transparent);
}

.mark.struck .head {
    text-decoration: line-through;
    text-decoration-color: var(--text-4);
}

.progress {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 2px;
    opacity: 0.85;
    transition: width 0.5s ease;
}

.worker {
    padding-left: 6px;
    border-left: 1px solid var(--border-2);
    color: var(--text-2);
    white-space: nowrap;
}

.head {
    display: flex;
    align-items: baseline;
    gap: 5px;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.settled {
    color: var(--tone-good);
    font-weight: 600;
}

.mark.console .head {
    margin: 0 -9px;
    padding: 0 9px 3px;
    border-bottom: 1px solid var(--border-2);
}

.head :deep(.md) {
    overflow: hidden;
    color: inherit;
    line-height: inherit;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.mark .head :deep(code) {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    padding: 0 6px;
    text-overflow: ellipsis;
    vertical-align: bottom;
    white-space: nowrap;
    border-radius: 4px;
    background: var(--chip);
    color: var(--text-2);
    font-size: 10.5px;
}

.head strong {
    color: var(--text-2);
    font-weight: 500;
}

.mark .detail :deep(.row-pill) {
    font-family: inherit;
    line-height: inherit;
}

.mark .detail :deep(.row-pill .ico) {
    width: 10px;
    height: 10px;
}

.mark .command {
    min-width: 0;
    overflow: hidden;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.mark .card {
    grid-column: 1 / -1;
    font-size: 13px;
}

.mark .card :deep(.row-card) {
    margin: 5px 0 2px;
}

.mark .detail {
    grid-column: 1 / -1;
    padding-left: 20px;
    color: var(--text-2);
    font-size: 12px;
    line-height: 1.45;
    overflow-wrap: anywhere;
    white-space: normal;
}



/* an opened mark grows in place to its text, each label above the text it names */
.mark .body {
    padding-bottom: 4px;
    color: var(--text-2);
    font-size: 12px;
}

.body-label {
    margin: 6px 0 2px;
    color: var(--text-4);
    font-size: 10.5px;
}
</style>
