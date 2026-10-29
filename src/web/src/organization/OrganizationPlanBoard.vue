<script setup>
import {computed} from "vue";
import {organizationLanes} from "../domain/organizationBoard.js";
import {organizationBoard} from "../state/organizationBoard.js";
import OrganizationPlanCard from "./OrganizationPlanCard.vue";
import Skeleton from "../kit/Skeleton.vue";
import PagedCards from "../kit/PagedCards.vue";
import {pageOf} from "../sync/paging.js";

const PHASES = ["planned", "in_progress", "in_review", "done"];
const PLAN_PAGE = pageOf("plans");
const props = defineProps({domains: {type: Array, default: () => []}, plans: {type: Array, default: null}, loading: Boolean});
const boards = computed(() => props.plans
    ? [{domain: {id: "all-plans", title: "All", board: {}}, allPlans: true, lanes: organizationLanes({plans: props.plans})}]
    : props.domains.map((domain) => ({domain, lanes: organizationLanes(domain, organizationBoard)})));
</script>

<template>
    <section class="organization-plan-board" :aria-label="plans ? 'All plans' : 'Domain boards'">
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
                                <OrganizationPlanCard v-for="plan in items" :key="plan.id" :plan="plan" />
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
</style>
