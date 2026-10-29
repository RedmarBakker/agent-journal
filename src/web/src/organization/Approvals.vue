<script setup>
import {computed, ref} from "vue";
import {usePressing} from "../composables/pressing.js";
import {useScope} from "../composables/scope.js";
import {useSharedNow} from "../composables/now.js";
import {actorName} from "../domain/people.js";
import {closedAt} from "../domain/row.js";
import {store} from "../state/store.js";
import Btn from "../kit/Btn.vue";

const props = defineProps({
    approval: {type: Object, required: true},
    question: {type: String, default: ""},
});

const scope = useScope();
const now = useSharedNow();
const {pressing, failure, run} = usePressing();
const localAnswer = ref(null);
const current = computed(() => ({...props.approval, ...localAnswer.value}));
const expired = computed(() => current.value.decision === "pending" && closedAt(current.value, now.value) > 0);
const waiting = computed(() => current.value.decision === "pending" && !expired.value);
const decision = computed(() => {
    const value = expired.value ? "expired" : current.value.decision;
    return ({approved: "Approved", refused: "Refused", expired: "Expired"})[value] || "";
});
const answerer = computed(() =>
    current.value.decision && current.value.decision !== "pending" && current.value.updater
        ? actorName(current.value.updater, store.people, current.value.environment_id)
        : ""
);

async function answer(choice) {
    if (!waiting.value) return;
    await run(choice, async () => {
        localAnswer.value = await scope.api.act("approvals", current.value.id, choice);
    });
}
</script>

<template>
    <article :class="['approval-card', {answered: !waiting}]" :data-approval-id="approval.id">
        <div class="approval-top">
            <span class="approval-kind">Approval</span>
        </div>
        <h3 class="approval-title">{{ question || "Approval required" }}</h3>
        <p class="approval-context">
            Role: {{ current.role }} · Plan: {{ current.plan_id }} · Task: {{ current.task_id }}
        </p>
        <template v-if="waiting">
            <div class="approval-actions">
                <Btn kind="primary" small :busy="pressing === 'approve'" :disabled="Boolean(pressing)" @click.stop="answer('approve')">Approve</Btn>
                <Btn kind="danger" small :busy="pressing === 'refuse'" :disabled="Boolean(pressing)" @click.stop="answer('refuse')">Refuse</Btn>
            </div>
            <p v-if="failure" class="approval-error" role="alert">{{ failure }}</p>
        </template>
        <div v-else-if="decision" class="approval-answer">
            <p>{{ decision }}<template v-if="answerer"> by {{ answerer }}</template></p>
        </div>
    </article>
</template>

<style scoped>
.approval-card {
    display: flex;
    flex-direction: column;
    gap: 7px;
    padding: 11px 12px;
    border: 1px solid var(--border-2);
    border-left: 3px solid var(--warn);
    border-radius: 9px;
    background: var(--raised);
}

.approval-card.answered {
    border-left-color: var(--text-3);
}

.approval-top {
    display: flex;
    align-items: baseline;
    gap: 8px;
}

.approval-kind {
    color: var(--warn);
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.approval-title {
    margin: 0;
    color: var(--text);
    font-size: 13.5px;
    font-weight: 550;
    line-height: 1.4;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.approval-context,
.approval-answer p {
    margin: 0;
    color: var(--text-2);
    font-size: 12px;
    line-height: 1.45;
}

.approval-context {
    color: var(--text-3);
}

.approval-actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}

.approval-error {
    margin: 0;
    color: var(--danger);
    font-size: 12px;
}

.approval-answer {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

@media (max-width: 600px) {
    .approval-actions :deep(.btn) {
        min-height: 40px;
    }
}
</style>
