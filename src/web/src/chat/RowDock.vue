<script setup>
import {computed, ref} from "vue";
import Btn from "../kit/Btn.vue";
import ChatDock from "../kit/ChatDock.vue";
import CloseButton from "../kit/CloseButton.vue";
import FoldSign from "../kit/FoldSign.vue";
import Icon from "../kit/Icon.vue";
import TextDisplay from "../kit/TextDisplay.vue";
import {useScope} from "../composables/scope.js";
import {undock} from "../actions/docking.js";
import {dockedRef} from "../domain/docks.js";
import {meta} from "../domain/tables.js";
import {peek} from "../route.js";
import {openUpdate} from "../state/overlays.js";

const props = defineProps({message: Object, folded: Boolean});
const scope = useScope();
const card = computed(() => props.message.data);
const row = computed(() => dockedRef(props.message));
const kind = computed(() => meta(row.value.table));
const buttons = computed(() => (card.value.dock?.buttons || []).filter((b) => b.act !== "close"));
// a card with a summary folds to its title on a click on it, and opens its row with Open; one with none opens its row on a click
const shut = ref(false);
const folds = computed(() => shut.value || (props.folded && card.value.dock?.folds !== false));
const opensItself = computed(() => !buttons.value.some((b) => b.act === "open"));

const dock = ref(null);
const takeDown = () => undock(scope, props.message);

const open = () => peek(row.value.table, row.value.id);
const openUpdateHere = () => openUpdate(row.value.id, dock.value?.card?.closest(".thread"), dock.value?.card);
const OWN = {open, close: takeDown, open_update: openUpdateHere};
const press = (button) => (OWN[button.act] || (() => scope.api.act(row.value.table, row.value.id, button.act)))();
const headingClicked = () => (card.value.summary ? (shut.value = !shut.value) : open());
</script>

<template>
    <ChatDock ref="dock" :label="kind.title" :folded="folds">
        <template #head>
            <Icon :name="kind.icon" class="row-dock-icon" />
            <button
                type="button"
                class="row-dock-heading"
                :aria-expanded="card.summary ? !folds : null"
                :title="card.summary ? (folds ? 'Show more' : 'Fold to one line') : `Open the ${kind.title.toLowerCase()}`"
                @click="headingClicked"
            >
                <span class="row-dock-title">{{ card.heading }}</span>
                <template v-if="card.summary">
                    <FoldSign :open="!folds" />
                </template>
            </button>
            <span class="row-dock-acts chat-dock-acts">
                <template v-if="card.summary && opensItself">
                    <Btn small @click="open">Open</Btn>
                </template>
                <template v-for="button in buttons" :key="button.act">
                    <Btn small @click="press(button)">{{ button.label }}</Btn>
                </template>
            </span>
            <CloseButton :title="`Hide from chat; the ${kind.title.toLowerCase()} stays on its page`" @click="takeDown" />
        </template>
        <template v-if="card.summary">
            <button type="button" class="row-dock-summary" @click="open">
                <TextDisplay inline :text="card.summary" />
            </button>
        </template>
    </ChatDock>
</template>

<style scoped>
.row-dock-icon {
    flex: none;
    color: var(--text-3);
}

.row-dock-heading {
    display: flex;
    flex: 0 1 auto;
    align-items: center;
    gap: 9px;
    min-width: 0;
    padding: 0;
    border: 0;
    background: none;
    color: var(--text);
    font: inherit;
    font-weight: 500;
    cursor: pointer;
}

.row-dock-title {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
}

.row-dock-heading:hover .fold,
.row-dock-heading:focus-visible .fold {
    color: var(--text-2);
}

.row-dock-acts {
    flex: none;
    display: flex;
    align-items: center;
    gap: 4px;
    margin-left: auto;
}

.row-dock-summary {
    display: block;
    width: 100%;
    overflow: hidden;
    padding: 0 12px 10px 35px;
    border: 0;
    background: none;
    color: var(--text-2);
    font: inherit;
    font-size: 12px;
    text-align: left;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: pointer;
}
</style>
