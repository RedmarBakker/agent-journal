<script setup>
import {ref} from "vue";
import Icon from "../kit/Icon.vue";

// a one-line card in the chat that grows in place to its whole text on a click and folds on a second: a worker's report, a message to or from a subagent;
// an incoming one, a message another agent sent, has its icon at the far right and its title against it
defineProps({
    title: {type: String, required: true},
    text: {type: String, default: ""},
    icon: {type: String, default: "agents"},
    bad: Boolean,
    action: {type: String, default: ""},
    incoming: Boolean,
});
const emit = defineEmits(["act"]);
const opened = ref(false);
</script>

<template>
    <div :class="['growing-card-wrap', {open: opened, bad, incoming}]">
        <button type="button" class="growing-card" :aria-expanded="opened" @click="opened = !opened">
            <Icon :name="icon" :size="14" />
            <span class="growing-card-title">{{ title }}</span>
        </button>
        <div class="growing-card-more">
            <div class="growing-card-body">
                <p class="growing-card-text">{{ text }}</p>
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
    max-width: 560px;
    border: 1px solid var(--border-2);
    border-radius: 9px;
    background: var(--raised);
}

.growing-card-wrap.bad {
    border-color: var(--bad);
}

.growing-card-wrap:hover {
    border-color: var(--accent);
}

.growing-card {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
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

.growing-card-wrap.incoming .growing-card {
    flex-direction: row-reverse;
    text-align: right;
}

.growing-card-more {
    display: grid;
    grid-template-rows: 0fr;
    opacity: 0;
    transition:
        grid-template-rows var(--move),
        opacity var(--fade);
}

.growing-card-wrap.open .growing-card-more {
    grid-template-rows: 1fr;
    opacity: 1;
}

.growing-card-body {
    min-height: 0;
    padding: 0 10px;
    overflow: hidden;
    font-size: 12px;
}

.growing-card-wrap.open .growing-card-body {
    padding: 0 10px 8px;
}

.growing-card-text {
    margin: 0 0 8px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.growing-card-action {
    padding: 0;
    border: 0;
    background: none;
    color: var(--accent);
    font: inherit;
    cursor: pointer;
}
</style>
