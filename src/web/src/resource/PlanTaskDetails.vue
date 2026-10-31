<script setup>
import {computed} from "vue";

const props = defineProps({task: {type: Object, required: true}});
const subtasks = computed(() => props.task.subtasks || []);
const roles = computed(() => new Set(subtasks.value.map((task) => task.role?.id).filter(Boolean)).size);
const merged = computed(() => subtasks.value.filter((task) => task.state === "completed").length);
const summary = computed(() => `${subtasks.value.length} ${subtasks.value.length === 1 ? "subtask" : "subtasks"} for ${roles.value} ${roles.value === 1 ? "Role" : "Roles"}, ${merged.value} merged`);
</script>

<template>
    <section class="plan-task-details" :data-route-state="task.route_state" :aria-label="`Details for task ${task.id}`">
        <div class="plan-task-route">
            <span class="plan-task-domain">
                <span v-if="task.domain?.icon" aria-hidden="true">{{ task.domain.icon }}</span>
                Domain: {{ task.domain?.title || "No Domain assigned" }}
            </span>
            <span>Route: {{ task.route_state }}</span>
        </div>
        <template v-if="subtasks.length">
            <p class="plan-subtask-summary">{{ summary }}</p>
            <ol class="plan-subtasks">
                <li v-for="part in subtasks" :key="part.id" :data-subtask-id="part.id">
                    <strong>Subtask {{ part.order }}: {{ part.title }}</strong>
                    <span>Role: {{ part.role?.title || "Not assigned" }}</span>
                    <span>Worker: {{ part.worker?.name || "Not assigned" }}</span>
                    <span>State: {{ part.state }}</span>
                    <span v-if="part.after">After task {{ part.after.id }}: {{ part.after.title }}</span>
                    <span v-else>First subtask</span>
                </li>
            </ol>
        </template>
    </section>
</template>

<style scoped>
.plan-task-details {
    margin: 2px 0 6px 48px;
    color: var(--text-2);
    font-size: 12px;
}

.plan-task-route {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 14px;
}

.plan-task-domain {
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.plan-subtask-summary {
    margin: 6px 0 3px;
    color: var(--text-3);
}

.plan-subtasks {
    display: grid;
    gap: 4px;
    margin: 0;
    padding-left: 18px;
}

.plan-subtasks li {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
}

.plan-subtasks strong {
    color: var(--text);
}
</style>
