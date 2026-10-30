<script setup>
import {computed, ref} from "vue";
import Btn from "../kit/Btn.vue";
import Dialog from "../kit/Dialog.vue";
import {useScope} from "../composables/scope.js";

const props = defineProps({planId: {type: Number, required: true}, sprint: {type: Object, required: true}, readOnly: Boolean});
const emit = defineEmits(["moved"]);
const scope = useScope();
const open = ref(false);
const loading = ref(false);
const busy = ref(false);
const problem = ref("");
const sprints = ref([]);
const nextSprintId = ref("");
const reason = ref("");
const eligibleSprints = computed(() => sprints.value.filter((sprint) =>
    sprint.state !== "closed" && sprint.id !== props.sprint.id && Date.parse(sprint.starts_at) >= Date.parse(props.sprint.ends_at)));
const fixedSprint = computed(() => props.sprint.state !== "closed");

async function show() {
    open.value = true;
    problem.value = "";
    if (fixedSprint.value) return;
    loading.value = true;
    try {
        sprints.value = await scope.api.sprints();
        nextSprintId.value = String(eligibleSprints.value[0]?.id || "");
    } catch (error) {
        problem.value = error.message;
    } finally {
        loading.value = false;
    }
}

async function carry() {
    if (!nextSprintId.value || !reason.value.trim()) {
        problem.value = "Choose a later sprint and explain the move.";
        return;
    }
    busy.value = true;
    problem.value = "";
    try {
        await scope.api.carryPlan(props.sprint.id, props.planId, Number(nextSprintId.value), reason.value.trim());
        open.value = false;
        emit("moved");
    } catch (error) {
        problem.value = error.message;
    } finally {
        busy.value = false;
    }
}
</script>

<template>
    <Btn v-if="!readOnly" small @click="show">Move to another sprint</Btn>
    <Dialog v-if="!readOnly" :open="open" modal small title="Move to another sprint" @close="open = false">
        <p v-if="fixedSprint" class="sprint-move-note">Sprint {{ sprint.id }} is still open. Its commitment is fixed until it closes.</p>
        <template v-else>
            <p v-if="loading" class="sprint-move-note">Reading later sprints.</p>
            <p v-else-if="!eligibleSprints.length" class="sprint-move-note">There is no later open sprint yet. Create one before moving this plan.</p>
            <form v-else class="sprint-move-form" @submit.prevent="carry">
                <label>
                    Later sprint
                    <select v-model="nextSprintId" required>
                        <option v-for="sprint in eligibleSprints" :key="sprint.id" :value="String(sprint.id)">
                            Sprint {{ sprint.id }} · {{ sprint.starts_on }} to {{ sprint.ends_on }}
                        </option>
                    </select>
                </label>
                <label>
                    Reason
                    <textarea v-model="reason" required rows="3" placeholder="Why is this plan moving?" />
                </label>
                <p v-if="problem" class="sprint-move-error" role="alert">{{ problem }}</p>
            </form>
        </template>
        <p v-if="problem && fixedSprint" class="sprint-move-error" role="alert">{{ problem }}</p>
        <template v-if="!fixedSprint" #foot>
            <Btn kind="ghost" @click="open = false">Cancel</Btn>
            <Btn v-if="eligibleSprints.length" kind="primary" :busy="busy" @click="carry">Move plan</Btn>
        </template>
    </Dialog>
</template>

<style scoped>
.sprint-move-note,
.sprint-move-error {
    margin: 0;
    color: var(--text-2);
    font-size: 12px;
}

.sprint-move-form {
    display: grid;
    gap: 12px;
}

.sprint-move-form label {
    display: grid;
    gap: 5px;
    color: var(--text-2);
    font-size: 12px;
}

.sprint-move-form select,
.sprint-move-form textarea {
    width: 100%;
    padding: 8px 9px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text);
    font: inherit;
}

.sprint-move-error {
    color: var(--danger);
}
</style>
