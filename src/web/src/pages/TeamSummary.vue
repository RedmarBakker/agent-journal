<script setup>
import {onlineCount} from "../domain/team.js";
import StateDot from "../kit/StateDot.vue";
import "./team.css";

defineProps({standing: {type: Object, required: true}, people: {type: Array, required: true}});
</script>

<template>
    <div class="team-summary">
        <div class="team-summary-cell">
            <span class="team-label">Team server</span>
            <span class="team-summary-big"><StateDot state="done" />Running</span>
            <span class="team-fine">{{ standing.address }}</span>
        </div>
        <div class="team-summary-cell">
            <span class="team-label">Team version</span>
            <span class="team-summary-big">{{ standing.version || "Not known yet" }}</span>
            <span class="team-fine">Which machines are behind is not known yet</span>
        </div>
        <div class="team-summary-cell">
            <span class="team-label">People</span>
            <span class="team-summary-big">{{ people.length }}</span>
            <span class="team-fine">{{ onlineCount(people) }} online now</span>
        </div>
        <div class="team-summary-cell">
            <span class="team-label">Worker pool</span>
            <span class="team-summary-big">None offered</span>
            <span class="team-fine">No pool worker is running</span>
        </div>
    </div>
</template>

<style scoped>
.team-summary {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 10px;
}

.team-summary-cell {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
    padding: 12px 16px;
}

.team-summary-cell + .team-summary-cell {
    border-left: 1px solid var(--border);
}

.team-summary-cell .team-fine {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.team-summary-big {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 500;
}

@media (max-width: 700px) {
    .team-summary {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .team-summary-cell + .team-summary-cell {
        border-left: 0;
    }

    .team-summary-cell:nth-child(even) {
        border-left: 1px solid var(--border);
    }

    .team-summary-cell:nth-child(n + 3) {
        border-top: 1px solid var(--border);
    }
}
</style>
