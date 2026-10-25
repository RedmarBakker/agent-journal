<script setup>
import {workerCounts, workersBySection} from "../domain/workers.js";
import {workerEntry} from "../domain/agentEntries.js";
import {computed} from "vue";
import AgentDropdown from "./AgentDropdown.vue";
import TestTurns from "./TestTurns.vue";
import {TEST_BUDGET} from "../domain/testTurns.js";
import Segmented from "../kit/Segmented.vue";
import {TESTINGS} from "../domain/modes.js";
import {workTesting} from "../composables/settings.js";
import {saveSettings} from "../actions/settings.js";

const props = defineProps({rows: {type: Array, default: () => []}, loading: Boolean});
const emit = defineEmits(["close"]);
const entries = computed(() => Object.values(workersBySection(props.rows)).flat().map(workerEntry));
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
    <AgentDropdown title="Workers" table="workers" :entries="entries" :counts="countsLine" none="No workers have been sent from here." :loading="loading" @close="emit('close')">
        <div class="workers-testing">
            <span class="workers-testing-label">How workers test</span>
            <Segmented :options="testingOptions" :value="workTesting" wrap @pick="pickTesting" />
        </div>
        <template v-if="workTesting === TEST_BUDGET">
            <TestTurns :workers="rows" />
        </template>
    </AgentDropdown>
</template>

<style scoped>
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
