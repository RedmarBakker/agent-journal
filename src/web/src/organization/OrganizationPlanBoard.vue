<script setup>
import {computed} from "vue";
import {organizationLanes} from "../domain/organizationBoard.js";
import {organizationBoard} from "../state/organizationBoard.js";
import OrganizationPlanCard from "./OrganizationPlanCard.vue";
import Skeleton from "../kit/Skeleton.vue";
import PagedCards from "../kit/PagedCards.vue";
import {pageOf} from "../sync/paging.js";
import {forecastForPlan, sprintGroups, sprintRange, sprintStatusLabel} from "../domain/deliveryForecast.js";
import {sprintPointLabel} from "../domain/taskSizing.js";

const PHASES = ["planned", "in_progress", "in_review", "done"];
const PLAN_PAGE = pageOf("plans");
const props = defineProps({domains: {type: Array, default: () => []}, plans: {type: Array, default: null}, sprintForecasts: {type: Array, default: () => []}, view: {type: String, default: "plans"}, loading: Boolean});
const boards = computed(() => props.plans
    ? [{domain: {id: "all-plans", title: "All", board: {}}, allPlans: true, lanes: organizationLanes({plans: props.plans})}]
    : props.domains.map((domain) => ({domain, lanes: organizationLanes(domain, organizationBoard)})));
const groups = computed(() => sprintGroups(props.plans || [], props.sprintForecasts));
const planGroups = computed(() => groups.value.map((group) => ({...group, plans: group.plans.map(({plan}) => plan)})));
const phasesFor = (plans) => organizationLanes({plans});
const forecastFor = (plan) => forecastForPlan(plan.id, props.sprintForecasts);
const sprintName = (group) => group.sprint ? `Sprint ${group.sprint.id}` : "No sprint yet";
const sprintDates = (group) => group.sprint ? sprintRange(group.sprint) : "";
const sprintStatus = (group) => sprintStatusLabel(group);
const pointSummary = (group) => sprintPointLabel(group.plans);
</script>

<template>
    <section class="organization-plan-board" :aria-label="plans ? (view === 'board' ? 'Board plans' : 'All plans') : 'Domain boards'">
        <div v-if="!loading && !plans" class="organization-board-tools">
            <label class="organization-board-filter">
                Filter plans
                <input v-model="organizationBoard.words" type="search" placeholder="Plan title, mode, or waiting reason" />
            </label>
            <label class="organization-board-hide-done"><input v-model="organizationBoard.hideDone" type="checkbox" /> Hide completed plans</label>
        </div>

        <div v-if="loading" class="organization-board-columns organization-board-loading" aria-busy="true" aria-label="Loading plans">
            <section v-for="phase in PHASES" :key="phase" class="organization-board-lane">
                <Skeleton shape="cards" :count="2" label="Loading plans" />
            </section>
        </div>
        <div v-else-if="plans && view === 'plans'" class="organization-sprint-list" aria-label="Plans grouped by sprint">
            <section v-for="group in planGroups" :key="group.key" class="organization-sprint-group" data-sprint-group :data-sprint-id="group.key">
                <header class="organization-sprint-head">
                    <div class="organization-sprint-title">
                        <h2>{{ sprintName(group) }}</h2>
                        <span v-if="sprintDates(group)" class="organization-sprint-dates">{{ sprintDates(group) }}</span>
                        <span class="organization-sprint-status" :data-sprint-status="group.status">{{ sprintStatus(group) }}</span>
                    </div>
                    <span class="organization-sprint-summary">{{ group.plans.length }} {{ group.plans.length === 1 ? "plan" : "plans" }} · {{ pointSummary(group) }}</span>
                </header>
                <PagedCards :items="group.plans" :page-size="PLAN_PAGE" :label="`${sprintName(group)} plans`" noun="plans">
                    <template #default="{items}">
                        <OrganizationPlanCard v-for="plan in items" :key="plan.id" :plan="plan" compact :forecast="forecastFor(plan)" />
                    </template>
                </PagedCards>
            </section>
        </div>
        <div v-else-if="plans && view === 'board'" class="organization-sprint-board" aria-label="Board grouped by sprint">
            <section v-for="group in groups" :key="group.key" class="organization-sprint-group" data-sprint-group :data-sprint-id="group.key">
                <header class="organization-sprint-head">
                    <div class="organization-sprint-title">
                        <h2>{{ sprintName(group) }}</h2>
                        <span v-if="sprintDates(group)" class="organization-sprint-dates">{{ sprintDates(group) }}</span>
                        <span class="organization-sprint-status" :data-sprint-status="group.status">{{ sprintStatus(group) }}</span>
                    </div>
                    <span class="organization-sprint-summary">{{ group.plans.length }} {{ group.plans.length === 1 ? "plan" : "plans" }} · {{ pointSummary(group) }}</span>
                </header>
                <div class="organization-board-columns" role="region" tabindex="0" :aria-label="`${sprintName(group)} plan phases`">
                    <section v-for="lane in phasesFor(group.plans.map(({plan}) => plan))" :key="lane.key" class="organization-board-lane" :data-phase="lane.key">
                        <h3>{{ lane.title }} <span class="organization-board-count">{{ lane.plans.length }}</span></h3>
                        <PagedCards :items="lane.plans" :page-size="PLAN_PAGE" :label="`${sprintName(group)} ${lane.title} plans`" noun="plans">
                            <template #default="{items}">
                                <OrganizationPlanCard v-for="plan in items" :key="plan.id" :plan="plan" :forecast="forecastFor(plan)" />
                                <p v-if="!lane.plans.length" class="organization-board-empty">No plans.</p>
                            </template>
                        </PagedCards>
                    </section>
                </div>
            </section>
        </div>
        <div v-else class="organization-boards">
            <section v-for="board in boards" :key="board.domain.id" class="organization-domain-board" :data-domain="board.allPlans ? null : board.domain.id">
                <header v-if="!board.allPlans" class="organization-domain-board-head">
                    <span v-if="board.domain.icon" aria-hidden="true">{{ board.domain.icon }}</span>
                    <h2>{{ board.domain.title }}</h2>
                </header>
                <div class="organization-board-columns" role="region" tabindex="0" :aria-label="`${board.domain.title} plan phases`">
                    <section v-for="lane in board.lanes" :key="lane.key" class="organization-board-lane" :data-phase="lane.key">
                        <h3>{{ lane.title }} <span class="organization-board-count">{{ lane.plans.length }}</span></h3>
                        <PagedCards :items="lane.plans" :page-size="PLAN_PAGE" :label="`${board.domain.title} ${lane.title} plans`" noun="plans">
                            <template #default="{items}">
                                <OrganizationPlanCard v-for="plan in items" :key="plan.id" :plan="plan" :forecast="forecastFor(plan)" />
                                <p v-if="!lane.plans.length" class="organization-board-empty">
                                    {{ lane.key === "done" && organizationBoard.hideDone ? "Completed plans are hidden." : "No plans in this phase." }}
                                </p>
                            </template>
                        </PagedCards>
                    </section>
                </div>
            </section>
        </div>
    </section>
</template>

<style scoped>
.organization-plan-board {
    display: flex;
    flex-direction: column;
    gap: 14px;
    min-width: 0;
}

.organization-board-tools {
    display: flex;
    flex-wrap: wrap;
    align-items: end;
    gap: 12px 20px;
}

.organization-board-filter {
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: min(300px, 100%);
    color: var(--text-2);
    font-size: 12px;
}

.organization-board-filter input {
    min-height: 34px;
    padding: 6px 9px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text);
    font: inherit;
}

.organization-board-hide-done {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    min-height: 34px;
    color: var(--text-2);
    font-size: 12px;
}

.organization-boards {
    display: flex;
    flex-direction: column;
    gap: 22px;
}

.organization-sprint-list,
.organization-sprint-board {
    display: flex;
    flex-direction: column;
    gap: 14px;
    min-width: 0;
}

.organization-sprint-group {
    min-width: 0;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: var(--bg);
}

.organization-sprint-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 9px 12px;
    border-bottom: 1px solid var(--border);
}

.organization-sprint-title {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 7px 10px;
    min-width: 0;
}

.organization-sprint-title h2 {
    margin: 0;
    font-size: 13px;
    font-weight: 650;
}

.organization-sprint-dates,
.organization-sprint-summary {
    color: var(--text-2);
    font-size: 11px;
}

.organization-sprint-status {
    padding: 2px 7px;
    border: 1px solid var(--border);
    border-radius: 999px;
    color: var(--text-2);
    font-size: 10px;
    white-space: nowrap;
}

.organization-sprint-status[data-sprint-status="ended"] {
    border-color: color-mix(in srgb, var(--warning, #d99325) 45%, var(--border));
    color: var(--warning, #d99325);
}

.organization-sprint-summary {
    flex: none;
    text-align: right;
}

.organization-sprint-list :deep(.paged-cards) {
    gap: 0;
}

.organization-sprint-board .organization-board-columns {
    padding: 10px;
}

.organization-domain-board {
    min-width: 0;
}

.organization-domain-board-head {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 10px;
}

.organization-domain-board-head h2 {
    margin: 0;
    font-size: 18px;
}

.organization-board-columns {
    display: grid;
    grid-template-columns: repeat(4, minmax(190px, 1fr));
    gap: 12px;
    min-width: 0;
    overflow-x: auto;
    padding-bottom: 5px;
}

.organization-board-columns:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

.organization-board-lane {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    min-width: 190px;
    min-height: 130px;
    padding: 10px;
    border: 1px solid var(--line);
    border-radius: 9px;
    background: var(--bg-2, var(--bg));
}

.organization-board-lane h3 {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin: 0 0 2px;
    color: var(--text-2);
    font-size: 12px;
    font-weight: 600;
}

.organization-board-count {
    color: var(--text-3);
    font-variant-numeric: tabular-nums;
}

.organization-board-empty {
    margin: 0;
    padding: 10px 2px;
    color: var(--text-3);
    font-size: 12px;
}

.organization-board-loading {
    margin-top: 8px;
}

.organization-board-loading :deep(.skeleton-cards) {
    width: 100%;
}

@media (max-width: 900px) {
    .organization-board-columns {
        grid-template-columns: repeat(4, minmax(220px, 1fr));
    }
}

@media (max-width: 700px) {
    .organization-sprint-head {
        align-items: flex-start;
        flex-direction: column;
    }

    .organization-sprint-summary {
        text-align: left;
    }
}
</style>
