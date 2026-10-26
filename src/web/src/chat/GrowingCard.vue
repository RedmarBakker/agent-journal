<script setup>
import {computed, ref} from "vue";
import Icon from "../kit/Icon.vue";
import MarkIcon from "../kit/MarkIcon.vue";
import {useMarkMotion} from "../composables/markMotion.js";

// a one-line card in the chat that grows in place to its whole text on a click and folds on a second: a worker's report, a message to or from a subagent;
// an incoming one, a message another agent sent, has its icon at the far right and its title against it
const props = defineProps({
    title: {type: String, required: true},
    text: {type: String, default: ""},
    icon: {type: String, default: "agents"},
    person: {type: String, default: ""},
    bad: Boolean,
    action: {type: String, default: ""},
    incoming: Boolean,
});
const emit = defineEmits(["act"]);
const opened = ref(false);
// it opens as a mark does: its text out, its new size, its text in, its top where it was (composables/markMotion.js)
const wrap = ref(null);
const {folded, phase} = useMarkMotion(wrap, () => !opened.value);
// the avatar: the first letter of the other agent's name, as Lady Lovelace's L
const initial = computed(() => (props.person.trim().split(/\s+/).pop() || "").charAt(0).toUpperCase());
// the message in its paragraphs, split where a blank line stands
const paragraphs = computed(() => props.text.split(/\n\s*\n/).filter((part) => part.trim()));
</script>

<template>
    <div ref="wrap" :class="['growing-card-wrap', phase, {open: !folded, bad, incoming}]">
        <button type="button" class="growing-card" :aria-expanded="opened" @click="opened = !opened">
            <span class="growing-card-avatar">
                <template v-if="bad">
                    <MarkIcon name="cross" />
                </template>
                <template v-else-if="initial">{{ initial }}</template>
                <template v-else>
                    <Icon :name="icon" :size="12" />
                </template>
            </span>
            <span class="growing-card-title">{{ title }}</span>
            <span class="growing-card-chevron"><MarkIcon name="chevron" /></span>
        </button>
        <div class="growing-card-more">
            <div class="growing-card-body">
                <template v-for="(part, i) in paragraphs" :key="i">
                    <p class="growing-card-text">{{ part }}</p>
                </template>
                <template v-if="action">
                    <button type="button" class="growing-card-action" @click="emit('act')">{{ action }}</button>
                </template>
            </div>
        </div>
    </div>
</template>

<style scoped>
.growing-card-wrap {
    display: flex;
    flex-direction: column;
    width: fit-content;
    max-width: 560px;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 11px;
    background: var(--raised);
    transition: border-color 0.15s ease;
}

.growing-card-wrap.bad {
    border-color: color-mix(in srgb, var(--danger) 50%, var(--border-2));
    background: color-mix(in srgb, var(--danger) 7%, var(--raised));
}

.growing-card-wrap:hover {
    border-color: var(--border-3);
}

.growing-card-avatar {
    display: grid;
    flex: none;
    place-items: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: color-mix(in srgb, var(--group-agent) 20%, transparent);
    color: var(--group-agent);
    font-size: 10px;
    font-weight: 600;
}

.growing-card-wrap.bad .growing-card-avatar {
    background: color-mix(in srgb, var(--danger) 20%, transparent);
    color: var(--danger);
}

.growing-card-avatar :deep(svg) {
    width: 12px;
    height: 12px;
}

.growing-card-chevron {
    display: grid;
    margin-left: 2px;
    color: var(--text-4);
    transition: transform 0.3s cubic-bezier(0.2, 0.9, 0.25, 1);
}

.growing-card-chevron :deep(svg) {
    width: 11px;
    height: 11px;
}

.growing-card-wrap.open .growing-card-chevron {
    transform: rotate(90deg);
}

.growing-card-wrap.incoming .growing-card-chevron {
    margin: 0 2px 0 0;
    transform: rotate(180deg);
}

.growing-card-wrap.incoming.open .growing-card-chevron {
    transform: rotate(90deg);
}

.growing-card {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 7px 11px 7px 8px;
    border: 0;
    background: none;
    color: var(--text);
    font: inherit;
    font-size: 12px;
    text-align: left;
    cursor: pointer;
}

.growing-card-title {
    font-weight: 500;
}

.growing-card-wrap.incoming {
    margin-left: auto;
}


.growing-card-wrap.incoming .growing-card {
    flex-direction: row-reverse;
    padding: 7px 8px 7px 11px;
    text-align: right;
}

.growing-card-wrap:not(.open) .growing-card-more {
    display: none;
}

.growing-card-more {
    transition: opacity 0.16s ease;
}

.growing-card-wrap.leaving .growing-card-more {
    opacity: 0;
    transition-duration: 0.12s;
}

.growing-card-wrap.resizing .growing-card-more {
    visibility: hidden;
    opacity: 0;
}

.growing-card-wrap.entering .growing-card-more {
    animation: arrive 0.16s ease;
}

@keyframes arrive {
    from {
        opacity: 0;
    }
}

.growing-card-body {
    min-height: 0;
    padding: 0 14px 0 39px;
    overflow: hidden;
    color: var(--text-2);
    font-size: 12.5px;
    line-height: 1.55;
}

.growing-card-wrap.open .growing-card-body {
    padding: 0 14px 11px 39px;
}

.growing-card-wrap.incoming.open .growing-card-body {
    padding: 0 39px 11px 14px;
}

.growing-card-text {
    margin: 0 0 6px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.growing-card-action {
    margin-top: 9px;
    padding: 0;
    font-size: 12px;
    border: 0;
    background: none;
    color: var(--accent-text);
    font: inherit;
    cursor: pointer;
}
</style>
