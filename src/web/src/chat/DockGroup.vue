<script setup>
import {ref} from "vue";
import ChatDockCard from "../kit/ChatDock.vue";
import FoldSign from "../kit/FoldSign.vue";
import MarkIcon from "../kit/MarkIcon.vue";
import ChatDock from "./ChatDock.vue";
import RunChip from "./RunChip.vue";
import {keepDocked} from "../actions/docking.js";
import {useScope} from "../composables/scope.js";

// Several runs docked at once, in one compact row with a chip per run: a click on its title opens every run's card, and a click on a
// chip opens that run's card, folds the others and keeps it
const props = defineProps({runs: {type: Array, required: true}, folded: Boolean});
const scope = useScope();
const open = ref(false);
const chosen = ref(0);

function toggle() {
    chosen.value = 0;
    open.value = !open.value;
}

function choose(message) {
    chosen.value = message.id;
    open.value = true;
    if (message.data.auto_docked) keepDocked(scope, message);
}

const foldedRun = (message) => props.folded || Boolean(chosen.value && chosen.value !== message.id);
</script>

<template>
    <div class="dock-group">
        <template v-if="open">
            <div class="dock-group-open">
                <div class="dock-group-head">
                    <button type="button" class="dock-group-toggle" aria-expanded="true" title="Fold the runs into one line" @click="toggle">
                        {{ runs.length }} runs
                        <FoldSign open />
                    </button>
                </div>
                <template v-for="run in runs" :key="run.id">
                    <ChatDock :message="run" :folded="foldedRun(run)" />
                </template>
            </div>
        </template>
        <template v-else>
            <ChatDockCard :label="`${runs.length} runs`" kind="dock-group-row">
                <template #head>
                    <button
                        type="button"
                        class="dock-group-toggle"
                        aria-expanded="false"
                        title="Show each run as its own card"
                        @click="toggle"
                    >
                        <MarkIcon name="runs" />
                        {{ runs.length }} runs
                        <FoldSign />
                    </button>
                    <span class="dock-group-chips">
                        <template v-for="run in runs" :key="run.id">
                            <RunChip :message="run" @click="choose(run)" />
                        </template>
                    </span>
                </template>
            </ChatDockCard>
        </template>
    </div>
</template>

<style scoped>
.dock-group-toggle {
    display: flex;
    flex: none;
    align-items: center;
    gap: 8px;
    height: 100%;
    margin-left: -12px;
    padding: 0 0 0 12px;
    border: 0;
    border-radius: 9px 0 0 9px;
    background: none;
    color: var(--text);
    font: inherit;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
    cursor: pointer;
}

.dock-group-toggle :deep(.mark-icon) {
    color: var(--text-3);
}

.dock-group-toggle:hover .fold,
.dock-group-toggle:focus-visible .fold {
    color: var(--text-2);
}

.dock-group-toggle:focus-visible {
    outline: 2px solid color-mix(in srgb, var(--accent-text) 70%, transparent);
    outline-offset: -2px;
}

.dock-group-chips {
    display: flex;
    flex: 1;
    gap: 4px;
    min-width: 0;
}

.dock-group-open {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

/* once open, a line naming how many runs there are folds them back into the row */
.dock-group-head {
    display: flex;
    align-items: center;
    height: 20px;
    margin-bottom: -2px;
}

.dock-group-head .dock-group-toggle {
    margin: 0;
    padding: 0 4px;
    border-radius: 5px;
    color: var(--text-3);
    font-size: 11.5px;
}

.dock-group-head .dock-group-toggle:hover {
    color: var(--text);
}

:global(html.phone .dock-group .chat-dock-head) {
    height: 44px;
    gap: 8px;
}

:global(html.phone .dock-group .dock-group-head) {
    height: 30px;
}
</style>
