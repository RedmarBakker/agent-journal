<script setup>
import {isActivePlan, phaseCount, phaseOf, standingOf} from "../domain/plans.js";
import {onUnmounted, ref} from "vue";
import Icon from "../kit/Icon.vue";
import MenuPanel from "../kit/MenuPanel.vue";
import {usePlanRows} from "../composables/planRows.js";
import {peek} from "../route.js";
import {rows} from "../sync/rows.js";

const CLOSE_AFTER_MS = 200;
const props = defineProps({plans: Array});
const shown = ref(0);
const anchor = ref(null);
let closing = 0;
usePlanRows(() => props.plans);
onUnmounted(() => clearTimeout(closing));

const standing = (p) => standingOf(p, rows("tasks"));
const plan = () => props.plans.find((p) => p.id === shown.value);

function show(p, event) {
    clearTimeout(closing);
    anchor.value = event.currentTarget;
    shown.value = p.id;
}

function leave() {
    closing = setTimeout(() => (shown.value = 0), CLOSE_AFTER_MS);
}

function keep() {
    clearTimeout(closing);
}

function open(p) {
    shown.value = 0;
    peek("plans", p.id);
}
</script>

<template>
    <div class="planstrip">
        <template v-for="p in plans" :key="p.id">
            <button type="button" :class="['planstrip-plan', {'planstrip-plan-active': isActivePlan(p)}]" :title="`Plan ${p.id}: ${p.title}${isActivePlan(p) ? ' (active)' : ''}`" @mouseenter="show(p, $event)" @mouseleave="leave" @click.stop="open(p)">
                <Icon name="plan" class="planstrip-icon" />
                <span class="planstrip-number">{{ p.id }}</span>
                <span class="planstrip-track" role="progressbar">
                    <span :style="{width: `${standing(p).donePart}%`}" />
                </span>
            </button>
        </template>
        <span class="planstrip-more"><slot /></span>
        <template v-if="shown && plan()">
            <MenuPanel :anchor="anchor" @click.stop @close="shown = 0">
                <div class="planstrip-card" @mouseenter="keep" @mouseleave="leave">
                    <p class="planstrip-card-title">{{ plan().title }}</p>
                    <template v-if="isActivePlan(plan())">
                        <p class="planstrip-card-line">The plan being worked on</p>
                    </template>
                    <template v-if="phaseOf(plan())">
                        <p class="planstrip-card-line">Phase {{ plan().current_phase || 1 }} of {{ phaseCount(plan()) }} · {{ phaseOf(plan()) }}</p>
                    </template>
                    <p class="planstrip-card-line">{{ standing(plan()).title }}</p>
                    <button type="button" class="planstrip-card-open" @click="open(plan())">Open plan {{ plan().id }}</button>
                </div>
            </MenuPanel>
        </template>
    </div>
</template>

<style scoped>
.planstrip-more {
    margin-left: auto;
}

.planstrip-more :deep(.planmore) {
    width: auto;
    height: auto;
    padding: 0;
    border: 0;
    background: none;
}

.planstrip {
    display: flex;
    align-items: center;
    gap: 6px;
    height: 24px;
    padding: 0 14px;
    border-bottom: 1px solid var(--line);
    background: var(--bg-2);
}

.planstrip-plan {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    height: 20px;
    padding: 0 7px;
    border: 0;
    border-radius: 6px;
    background: none;
    color: var(--text-3);
    font: inherit;
    font-size: 11px;
    font-variant-numeric: tabular-nums;
    cursor: pointer;
}

.planstrip-plan:first-child {
    margin-left: -7px;
}

.planstrip-plan:hover {
    background: var(--hover);
    color: var(--text);
}

.planstrip-plan-active {
    color: var(--accent-text);
}

.planstrip-plan-active .planstrip-track > span {
    background: var(--accent);
}

.planstrip-track {
    display: flex;
    width: 36px;
    height: 3px;
    border-radius: 3px;
    overflow: hidden;
    background: var(--line);
}

.planstrip-track > span {
    display: block;
    height: 100%;
    background: var(--text-2);
}

.planstrip-card {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 220px;
    padding: 10px 12px;
}

.planstrip-card-title {
    margin: 0;
    font-weight: 500;
}

.planstrip-card-line {
    margin: 0;
    color: var(--text-3);
    font-size: 12px;
}

.planstrip-card-open {
    align-self: flex-start;
    padding: 0;
    border: 0;
    background: none;
    color: var(--accent-text);
    font: inherit;
    font-size: 12px;
    cursor: pointer;
}
</style>
