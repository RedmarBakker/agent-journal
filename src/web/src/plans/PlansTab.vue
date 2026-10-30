<script setup>
import {computed, ref} from "vue";
import {runPlan} from "../actions/work.js";
import {usePlanRows} from "../composables/planRows.js";
import {PLAN_STATES, planGroups, sizeOf, standingOf, statusOf} from "../domain/plans.js";
import EmptyState from "../kit/EmptyState.vue";
import PSection from "../layout/PSection.vue";
import {peek} from "../route.js";
import {rows} from "../sync/rows.js";

// The Home page's Plans window: the open plans, those being worked on as their bars, then those waiting to start, each with its progress.
const groups = computed(() => planGroups(rows("plans")));
const error = ref("");
usePlanRows(() => groups.value.flatMap((group) => group.plans));

const progress = (p) => standingOf(p, rows("tasks"));

async function runBar(p) {
    error.value = "";
    try {
        await runPlan(p);
    } catch (e) {
        error.value = e.message;
    }
}
</script>

<template>
    <div class="plans-tab">
        <template v-if="!groups.length">
            <EmptyState title="No plans yet">A plan the agent builds shows here with its progress.</EmptyState>
        </template>
        <template v-for="group in groups" :key="group.key">
            <section class="plans-group">
                <h4 class="plans-head">
                    {{ group.title }} <span class="plans-count">{{ group.plans.length }}</span>
                </h4>
                <template v-if="group.key === 'running'">
                    <template v-for="p in group.plans" :key="p.id">
                        <PSection :p="p" :error="error" @run-bar="runBar" @failed="error = $event" />
                    </template>
                </template>
                <template v-else>
                    <template v-for="p in group.plans" :key="p.id">
                        <button type="button" class="plan-row" @click="peek('plans', p.id)">
                            <span class="plan-number">{{ p.id }}</span>
                            <span class="plan-title">{{ p.title }}</span>
                            <span class="plan-state">{{ PLAN_STATES[statusOf(p)] }}</span>
                            <span class="plan-progress">{{ progress(p).title }} · {{ sizeOf(p) }}</span>
                            <span class="plan-bar"><span class="plan-bar-done" :style="{width: `${progress(p).donePart}%`}" /></span>
                        </button>
                    </template>
                </template>
            </section>
        </template>
    </div>
</template>

<style scoped>
.plans-tab {
    height: 100%;
    overflow: auto;
    padding: 6px 0 12px;
}

.plans-group {
    margin-bottom: 10px;
}

.plans-head {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 8px 14px 6px;
    color: var(--text-3);
    font-size: 12px;
    font-weight: 500;
}

.plans-count {
    color: var(--text-3);
    font-variant-numeric: tabular-nums;
}

.plan-row {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 2px 10px;
    width: 100%;
    padding: 8px 14px;
    border: 0;
    background: transparent;
    color: var(--text);
    font: inherit;
    text-align: left;
    cursor: pointer;
}

.plan-row:hover {
    background: var(--hover);
}

.plan-number {
    color: var(--text-3);
    font-size: 12.5px;
    font-variant-numeric: tabular-nums;
}

.plan-title {
    min-width: 0;
    overflow: hidden;
    font-size: 13px;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-state {
    color: var(--text-3);
    font-size: 12px;
}

.plan-progress {
    grid-column: 2 / 4;
    color: var(--text-3);
    font-size: 12px;
}

.plan-bar {
    grid-column: 2 / 4;
    height: 3px;
    border-radius: 2px;
    background: var(--border);
    overflow: hidden;
}

.plan-bar-done {
    display: block;
    height: 100%;
    background: var(--accent);
}
</style>
