<script setup>
import {computed, ref, watch} from "vue";
import {useScope} from "../composables/scope.js";
import {seconds} from "../domain/row.js";
import {ago} from "../format/time.js";
import {store} from "../state/store.js";

const props = defineProps({plan: {type: Object, required: true}, initial: {type: Object, default: null}});
const scope = useScope();
const history = ref({current_role: "", steps: []});
const loading = ref(false);
const error = ref("");
const roles = computed(() => (store.organization?.domains || []).flatMap((domain) => domain.roles || []));
const liveAgent = computed(() => (store.summary?.environments || []).find((row) => row.environment.name === props.plan.chat)?.agent || null);
const currentRole = computed(() => {
    const top = liveAgent.value?.stack?.[0];
    return liveAgent.value?.stack?.length ? (top?.name === "role_work" ? top.values?.role || "" : "") : history.value.current_role;
});

function roleTitle(id) {
    return roles.value.find((role) => role.id === id)?.title || id;
}

function taskTitle(step) {
    return step.task ? `Task ${step.task}${step.title ? ` · ${step.title}` : ""}` : "No task was in hand";
}

watch(() => props.plan.id, async (id) => {
    if (props.initial) {
        history.value = props.initial;
        loading.value = false;
        return;
    }
    loading.value = true;
    error.value = "";
    try {
        history.value = await scope.api.planRoles(id);
    } catch (e) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
}, {immediate: true});
</script>

<template>
    <section class="plan-role-history" aria-label="Roles the Plan agent has taken on">
        <h3>Roles the Plan agent has taken on</h3>
        <p v-if="currentRole" class="plan-role-current">Current Role: {{ roleTitle(currentRole) }}</p>
        <p v-else class="plan-role-current">No Role is active now.</p>
        <p v-if="error" class="plan-role-error" role="alert">{{ error }}</p>
        <p v-else-if="loading && !history.steps.length" class="plan-role-empty">Loading Role history…</p>
        <ol v-else-if="history.steps.length" class="plan-role-steps">
            <li v-for="(step, index) in history.steps" :key="`${step.time}-${step.role}-${index}`">
                <span>{{ roleTitle(step.role) }}</span>
                <span>{{ taskTitle(step) }}</span>
                <time v-if="step.time">{{ ago(seconds(step.time)) }}</time>
            </li>
        </ol>
        <p v-else class="plan-role-empty">No Roles have been taken on yet.</p>
    </section>
</template>

<style scoped>
.plan-role-history {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 8px 0 16px;
    padding: 12px 14px;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: var(--panel);
}

.plan-role-history h3 {
    margin: 0;
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.plan-role-current,
.plan-role-empty,
.plan-role-error {
    margin: 0;
    color: var(--text-3);
    font-size: 12px;
}

.plan-role-steps {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin: 0;
    padding-left: 20px;
    color: var(--text-2);
    font-size: 12px;
}

.plan-role-steps li {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
}

.plan-role-steps time {
    color: var(--text-3);
}

.plan-role-error {
    color: var(--danger);
}
</style>
