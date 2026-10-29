<script setup>
import {computed, ref} from "vue";
import Btn from "../kit/Btn.vue";
import PlanCritique from "./PlanCritique.vue";
import PlanModePicker from "./PlanModePicker.vue";
import PlanTestingPicker from "./PlanTestingPicker.vue";
import {actsOf} from "../domain/acts.js";

const props = defineProps({plan: {type: Object, required: true}, error: {type: String, default: ""}});
const emit = defineEmits(["run"]);
const acts = computed(() => actsOf(props.plan));
const critiquing = ref(false);
const choosingTesting = ref(false);
const choosingMode = ref(false);
const modeChangeable = computed(() => ["draft", "paused"].includes(props.plan.state));
const testing = computed(() => props.plan.testing?.[0] || "no testing template");
</script>

<template>
    <div class="actions">
        <template v-for="(act, i) in acts" :key="act.name">
            <Btn :kind="act.danger ? 'danger' : i === 0 ? 'primary' : 'ghost'" @click="emit('run', act.name)">{{ act.label }}</Btn>
        </template>
        <template v-if="plan.state === 'ready'">
            <Btn kind="ghost" @click="critiquing = true">Ask for a critique</Btn>
        </template>
        <template v-if="!['done', 'cancelled'].includes(plan.state)">
            <Btn kind="ghost" title="Choose how the agent tests while it follows this plan" @click="choosingTesting = true">Testing: {{ testing }}</Btn>
        </template>
        <template v-if="!['done', 'cancelled'].includes(plan.state)">
            <Btn kind="ghost" :disabled="!modeChangeable" :title="modeChangeable ? 'Choose how the plan is worked' : 'The mode can be changed while the plan is a draft or paused'" @click="choosingMode = true">Mode: {{ plan.mode }}</Btn>
        </template>
        <span class="error">{{ error }}</span>
    </div>
    <template v-if="choosingTesting">
        <PlanTestingPicker :plan="plan" @close="choosingTesting = false" />
    </template>
    <template v-if="choosingMode">
        <PlanModePicker :plan="plan" @close="choosingMode = false" />
    </template>
    <template v-if="critiquing">
        <PlanCritique :plan="plan" @close="critiquing = false" />
    </template>
</template>

<style scoped>
.note {
    color: var(--text-3);
    font-size: 12px;
}

.actions {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 16px;
}

.error {
    color: var(--danger);
    font-size: 12px;
}
</style>
