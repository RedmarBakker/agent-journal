<script setup>
import {computed, ref} from "vue";
import {useScope} from "../composables/scope.js";
import Btn from "../kit/Btn.vue";
import ChoiceList from "../kit/ChoiceList.vue";
import Dialog from "../kit/Dialog.vue";

const props = defineProps({plan: {type: Object, required: true}});
const emit = defineEmits(["close"]);
const scope = useScope();
const picking = ref("");
const failure = ref("");

const choices = computed(() => [
    {value: "organization", label: "Organization", hint: "The Plan agent writes no code: it coordinates Domain agents, who coordinate the Roles that do the work.", current: props.plan.mode === "organization"},
    {value: "solo", label: "Solo", hint: "The Plan agent does the work itself, taking on one Role at a time.", current: props.plan.mode === "solo"},
]);

async function pick(mode) {
    picking.value = mode;
    failure.value = "";
    try {
        await scope.api.setPlanMode(props.plan.id, mode);
        emit("close");
    } catch (e) {
        failure.value = e.message;
    } finally {
        picking.value = "";
    }
}
</script>

<template>
    <Dialog title="How the plan is worked" @close="emit('close')">
        <p class="plan">plan {{ plan.id }} · {{ plan.title }}</p>
        <p class="guide">The mode can be changed while the plan is a draft or paused, never while it runs.</p>
        <ChoiceList stacked :choices="choices" :busy="(value) => picking === value" @pick="pick" />
        <template v-if="failure">
            <p class="failure">{{ failure }}</p>
        </template>
        <div class="actions">
            <Btn small @click="emit('close')">Close</Btn>
        </div>
    </Dialog>
</template>

<style scoped>
.plan {
    margin: 0 0 8px;
    color: var(--text-2);
}

.guide {
    margin: 0 0 12px;
    color: var(--text-3);
    font-size: 12px;
}

.failure {
    color: var(--danger);
    font-size: 12px;
}

.actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
}
</style>
