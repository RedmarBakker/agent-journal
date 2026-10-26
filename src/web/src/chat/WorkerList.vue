<script setup>
import {workerCounts, workersBySection} from "../domain/workers.js";
import {momentEntry, workerEntry} from "../domain/agentEntries.js";
import {computed, ref} from "vue";
import AgentDropdown from "./AgentDropdown.vue";
import TestTurns from "./TestTurns.vue";
import {TEST_BUDGET} from "../domain/testTurns.js";
import Segmented from "../kit/Segmented.vue";
import {TESTINGS} from "../domain/modes.js";
import {workTesting} from "../composables/settings.js";
import {saveSettings} from "../actions/settings.js";

const props = defineProps({rows: {type: Array, default: () => []}, loading: Boolean, moments: {type: Array, default: () => []}, momentsLoading: Boolean});
const TABS = [
    {key: "workers", label: "Workers"},
    {key: "activity", label: "Recent activity"},
];
const tab = ref("workers");
const emit = defineEmits(["close"]);
const entries = computed(() => Object.values(workersBySection(props.rows)).flat().map(workerEntry));
const momentEntries = computed(() => props.moments.map(momentEntry));
const counts = computed(() => workerCounts(props.rows));
const countsLine = computed(() =>
    [counts.value.working && `${counts.value.working} working`, counts.value.idle && `${counts.value.idle} idle`]
        .filter(Boolean)
        .join(" · ")
);

const testingOptions = TESTINGS.map((one) => ({...one, tip: {title: one.label, line: one.note}}));
const pickTesting = (key) => saveSettings({workers: {testing: key}});
</script>

<template>
    <AgentDropdown
        title="Workers"
        table="workers"
        :entries="tab === 'workers' ? entries : momentEntries"
        :counts="tab === 'workers' ? countsLine : ''"
        :none="tab === 'workers' ? 'No workers have been sent from here.' : 'No worker has done anything noteworthy yet.'"
        :loading="tab === 'workers' ? loading : momentsLoading"
        @close="emit('close')"
    >
        <div class="workers-tabs">
            <Segmented :options="TABS" :value="tab" fill @pick="tab = $event" />
        </div>
        <template v-if="tab === 'workers'">
            <div class="workers-testing">
                <span class="workers-testing-label">How workers test</span>
                <Segmented :options="testingOptions" :value="workTesting" wrap @pick="pickTesting" />
            </div>
        </template>
        <template v-if="tab === 'workers' && workTesting === TEST_BUDGET">
            <TestTurns :workers="rows" />
        </template>
    </AgentDropdown>
</template>

<style scoped>
.workers-tabs {
    flex: none;
    padding: 8px 8px 0;
}

.workers-testing {
    display: flex;
    flex: none;
    flex-direction: column;
    gap: 4px;
    padding: 8px 8px 8px;
    border-bottom: 1px solid var(--line);
}

.workers-testing-label {
    color: var(--text-3);
    font-size: 12px;
}
</style>
