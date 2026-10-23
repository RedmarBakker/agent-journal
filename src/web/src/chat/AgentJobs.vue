<script setup>
import {nextRun, scheduleWords} from "../domain/cron.js";
import {clock} from "../format/time.js";

defineProps({jobs: {type: Array, default: () => []}});

const firstLine = (prompt) => String(prompt || "").split("\n")[0];
const next = (job) => {
    const at = nextRun(job.cron);
    return at ? `next at ${clock(at.getTime() / 1000)}` : "not due again";
};
</script>

<template>
    <div class="agent-jobs">
        <div class="agent-jobs-head">Scheduled</div>
        <template v-if="!jobs.length">
            <p class="agent-jobs-none">The agent has scheduled nothing.</p>
        </template>
        <template v-for="job in jobs" :key="job.id">
            <div class="agent-job">
                <b>{{ firstLine(job.prompt) }}</b>
                <span>{{ scheduleWords(job.cron) }}{{ job.recurring ? "" : ", once" }} · {{ next(job) }}</span>
            </div>
        </template>
    </div>
</template>

<style scoped>
.agent-jobs {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 10px 12px;
}

.agent-jobs-head {
    color: var(--text-3);
    font-size: 11.5px;
}

.agent-jobs-none {
    margin: 0;
    color: var(--text-3);
    font-size: 12.5px;
}

.agent-job {
    display: flex;
    flex-direction: column;
    gap: 2px;
    font-size: 12.5px;
}

.agent-job b {
    overflow: hidden;
    color: var(--text);
    font-weight: 500;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.agent-job span {
    color: var(--text-3);
    font-size: 11.5px;
}
</style>
