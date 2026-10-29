<script setup>
import {computed, ref, watch} from "vue";
import {api} from "../api/client.js";
import AgentStartButton from "../chat/AgentStartButton.vue";
import AgentStopButton from "../chat/AgentStopButton.vue";
import {ago} from "../format/time.js";
import {seconds} from "../domain/row.js";
import {store} from "../state/store.js";

const props = defineProps({plan: {type: Object, required: true}, readOnly: Boolean});
const environmentStatus = computed(() => (store.summary?.environments || []).find((row) => row.environment.name === props.plan.chat) || null);
const environment = computed(() => environmentStatus.value?.environment || (store.rows.environments || []).find((row) => row.name === props.plan.chat) || null);
const current = computed(() => environmentStatus.value?.agent || null);
const planSummary = computed(() => (store.organization?.plans || []).find((row) => row.id === props.plan.id) || null);
const lastActionTime = ref(props.plan.plan_agent_last_action_at || null);
const lastActionText = ref("");
watch(current, (agent) => {
    const action = agent?.doing || agent?.tool_work || agent?.last_message;
    if (action) lastActionText.value = action;
}, {immediate: true});
watch(() => current.value?.heard_at, (at) => at && (lastActionTime.value = at), {immediate: true});
watch(() => props.plan.plan_agent_last_action_at, (at) => at && (lastActionTime.value = at), {immediate: true});
const running = computed(() => environmentStatus.value
    ? Boolean(current.value && current.value.status !== "stopped")
    : planSummary.value?.plan_agent_state === "running");
const branch = computed(() => current.value?.branch || environment.value?.branch || "");
const lastAction = computed(() => lastActionText.value || "No action reported");
const lastActionAt = computed(() => ago(seconds(current.value?.heard_at || lastActionTime.value)));
const status = computed(() => {
    if (!props.plan.chat) return "Not started";
    if (!environmentStatus.value && !planSummary.value) return "Status not reported";
    return running.value ? "Running" : "Stopped";
});
const canStart = computed(() => Boolean(environment.value?.id && props.plan.state === "started" && status.value === "Stopped"));
const work = computed(() => environmentStatus.value?.task?.title || current.value?.doing || "");

function start(provider) {
    return api.launchAgent(environment.value.id, provider);
}

function stop() {
    return api.stopAgentIn(environment.value.id);
}
</script>

<template>
    <section class="plan-agent-section" aria-label="Plan agent">
        <h3>Plan agent</h3>
        <template v-if="plan.chat">
            <div class="plan-agent-details">
                <span :class="['plan-agent-state', {running}]">{{ status }}</span>
                <span>Environment: {{ plan.chat }}</span>
                <span v-if="branch">Branch: {{ branch }}</span>
                <span>Last action: {{ lastAction }}<template v-if="lastActionAt"> · {{ lastActionAt }}</template></span>
            </div>
            <div class="plan-agent-actions">
                <a class="plan-agent-chat" :href="api.page(plan.chat)">Open its chat</a>
                <template v-if="!readOnly && environment?.id && running">
                    <AgentStopButton :environment="plan.chat" :work="work" :stop="stop" quiet />
                </template>
                <template v-else-if="!readOnly && canStart">
                    <AgentStartButton :environment="plan.chat" :start="start" />
                </template>
                <span v-else-if="!readOnly && !running && ['draft', 'ready', 'reviewing', 'approved', 'paused'].includes(plan.state)" class="plan-agent-start-note">Start the plan to start its agent.</span>
            </div>
        </template>
        <p v-else class="plan-agent-start-note"><span class="plan-agent-state">Not started.</span> The Plan agent is created when this plan starts.</p>
    </section>
</template>

<style scoped>
.plan-agent-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 8px 0 16px;
    padding: 12px 14px;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: var(--panel);
}

.plan-agent-section h3 {
    margin: 0;
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.plan-agent-details,
.plan-agent-actions {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px 14px;
    color: var(--text-2);
    font-size: 12px;
}

.plan-agent-state {
    color: var(--text-3);
    font-weight: 600;
}

.plan-agent-state.running {
    color: var(--progress);
}

.plan-agent-chat {
    color: var(--accent-text);
    text-decoration: none;
}

.plan-agent-chat:hover {
    text-decoration: underline;
}

.plan-agent-start-note {
    margin: 0;
    color: var(--text-3);
    font-size: 12px;
}
</style>
