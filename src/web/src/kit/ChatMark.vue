<script setup>
import {computed, ref, useAttrs} from "vue";
import ChatMarkStatus from "./ChatMarkStatus.vue";
import Icon from "./Icon.vue";
import TextDisplay from "./TextDisplay.vue";
import {clock} from "../format/time.js";

defineOptions({inheritAttrs: false});
const props = defineProps({mark: {type: Object, required: true}, open: {type: Boolean, default: undefined}});

const attrs = useAttrs();
const passed = computed(() => Object.fromEntries(Object.entries(attrs).filter(([name]) => name !== "onClick")));
// a mark is one line: its second line shows once a click opens it, and a second click folds it again; a mark given `open` is opened by its owner
const expanded = ref(false);
const hasSecondLine = computed(() => Boolean(props.mark.detail || props.mark.command));
const owned = computed(() => props.open !== undefined);
const folded = computed(() => (owned.value ? !props.open : hasSecondLine.value && !expanded.value));
const tag = computed(() => (attrs.onClick || hasSecondLine.value || owned.value ? "button" : "span"));

function clicked(event) {
    if (folded.value && !owned.value) {
        expanded.value = true;
        return;
    }
    if (attrs.onClick) attrs.onClick(event);
    else expanded.value = false;
}
const shade = computed(() => props.mark.color || (props.mark.tone ? `var(--tone-${props.mark.tone})` : ""));
// a mark's progress bar is drawn in the mark's own tint, and in the working colour on a mark with none
const barShade = computed(() => shade.value || "var(--tone-work)");
// a run's bar shows while the run is active: a process or watch card that has ended, finished or failed, or any ended mark, has none
const running = computed(() => !props.mark.ending && !props.mark.ended);
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
        :class="['mark', {worked: mark.worker, tinted: shade, filled: mark.tone === 'bad', console: mark.command, nested: mark.depth > 0, [`ended-${mark.state}`]: mark.ended}]"
        :style="tint"
        :title="hover"
        :data-figure-mark="mark.key"
        :data-folded="folded ? '' : null"
        :data-open="owned && open ? '' : null"
        @click="clicked"
    >
        <Icon :name="mark.icon || 'dot'" />
        <template v-if="mark.worker">
            <span class="worker">{{ mark.worker }}</span>
        </template>
        <span class="head">
            <TextDisplay :text="mark.label" inline :row-names="false" />
            <template v-if="mark.name">
                <strong>{{ mark.name }}</strong>
            </template>
            <template v-if="mark.state || mark.started">
                <ChatMarkStatus :mark="mark" />
            </template>
            <template v-if="mark.figure">
                <span class="figure">{{ mark.figure }}</span>
            </template>
        </span>
        <template v-if="(mark.figure || mark.counting) && running">
            <span class="progress" :style="{width: `${Math.round((mark.fraction || 0) * 100)}%`, background: barShade}"></span>
        </template>
        <template v-if="mark.settled">
            <span class="settled">{{ mark.settled }}</span>
        </template>
        <template v-if="mark.detail && !folded">
            <TextDisplay class="detail" :text="mark.detail" inline :row-names="false" />
        </template>
        <template v-if="mark.command && !folded">
            <code class="detail command" :title="mark.command">{{ mark.command }}</code>
        </template>
        <template v-if="mark.card">
            <TextDisplay class="card" :text="mark.card" :row-names="false" />
        </template>
        <slot />
    </component>
</template>

<style scoped>
.mark.nested {
    position: relative;
    margin-left: calc(var(--depth) * 16px);
}

.mark.nested::before {
    content: "";
    position: absolute;
    top: 2px;
    bottom: 2px;
    left: -9px;
    width: 2px;
    border-radius: 1px;
    background: var(--mark, var(--border-3));
    opacity: 0.7;
}

.mark {
    display: inline-grid;
    grid-template-columns: auto minmax(0, 1fr);
    column-gap: 6px;
    row-gap: 1px;
    align-items: center;
    max-width: 100%;
    padding: 3px 9px;
    border: 1px solid var(--border-2);
    border-radius: 6px;
    background: none;
    color: var(--text-3);
    font: inherit;
    font-size: 11px;
    line-height: 1.4;
    text-align: left;
}

button.mark {
    cursor: pointer;
}

.mark.worked {
    grid-template-columns: auto auto minmax(0, 1fr);
}

.mark {
    interpolate-size: allow-keywords;
    transition: width 0.3s ease;
}

.mark[data-open] {
    width: min(100%, 640px);
}

button.mark:hover {
    color: var(--text-2);
}

.mark.tinted {
    border-color: color-mix(in srgb, var(--mark) 35%, transparent);
    background: color-mix(in srgb, var(--mark) 7%, transparent);
}

.mark .ico {
    align-self: start;
    width: 12px;
    height: 12px;
    margin-top: 2px;
}

.mark.tinted .ico {
    color: var(--mark);
}

.mark.filled {
    border-color: color-mix(in srgb, var(--danger) 55%, var(--border-2));
    background: color-mix(in srgb, var(--danger) 9%, transparent);
}

.mark:has(.progress) {
    position: relative;
    overflow: hidden;
}

.figure {
    margin-left: auto;
    padding-left: 8px;
    color: var(--text-3);
    font-variant-numeric: tabular-nums;
}

.progress {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 2px;
    opacity: 0.8;
    transition: width 0.4s ease;
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

.mark.ended-done {
    border-color: color-mix(in srgb, var(--tone-good) 40%, var(--border-2));
    background: color-mix(in srgb, var(--tone-good) 7%, transparent);
}

.mark.ended-failed {
    border-color: color-mix(in srgb, var(--danger) 55%, var(--border-2));
    background: color-mix(in srgb, var(--danger) 9%, transparent);
}

.head :deep(.md) {
    color: inherit;
    line-height: inherit;
}

.mark .head :deep(code) {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    padding: 0 6px;
    text-overflow: ellipsis;
    vertical-align: bottom;
    white-space: nowrap;
    border: 1px solid color-mix(in srgb, var(--mark, var(--border-3)) 45%, transparent);
    border-radius: 999px;
    background: color-mix(in srgb, var(--mark, var(--border-3)) 14%, transparent);
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
    color: color-mix(in srgb, var(--text-3) 80%, transparent);
    font-size: 10px;
    line-height: 1.4;
    overflow-wrap: anywhere;
}
</style>
