<script setup>
import {computed} from "vue";
import {boardColumns, driverLine} from "../domain/hub.js";
import {rowLabel} from "../domain/rowLabels.js";
import PagedCards from "../kit/PagedCards.vue";
import {pageOf} from "../sync/paging.js";

const props = defineProps({tasks: {type: Array, default: () => []}, environments: {type: Array, default: () => []}});
const emit = defineEmits(["open"]);
const TASK_PAGE = pageOf("tasks");
const columns = computed(() => boardColumns(props.tasks));
</script>

<template>
    <div class="board" data-hub-board role="region" aria-label="Home task board" tabindex="0">
        <template v-for="column in columns" :key="column.key">
            <section class="column" :data-column="column.key">
                <h3 class="head">{{ column.title }} <span class="count">{{ column.tasks.length }}</span></h3>
                <PagedCards :items="column.tasks" :page-size="TASK_PAGE" :label="`${column.title} tasks`" noun="tasks">
                    <template #default="{items}">
                        <button v-for="task in items" :key="task.id" type="button" class="card" @click="emit('open', task)">
                            {{ rowLabel("task", task, environments) }}: {{ task.title }}
                            <span v-if="task.driver" class="driver" data-driver>{{ driverLine(task) }}</span>
                        </button>
                    </template>
                </PagedCards>
            </section>
        </template>
    </div>
</template>

<style scoped>
.board {
    display: flex;
    gap: 12px;
    padding: 12px;
    overflow-x: auto;
}

.board:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

.column {
    flex: 1 0 200px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.head {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-2);
}

.count {
    color: var(--text-3);
}

.card {
    display: flex;
    flex-direction: column;
    gap: 2px;
    text-align: left;
    padding: 8px 10px;
    font-size: 12.5px;
    color: var(--text);
    background: var(--bg-2, var(--bg));
    border: 1px solid var(--border);
    border-radius: 6px;
}

.card:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
}

.driver {
    font-size: 11.5px;
    color: var(--text-3);
}
</style>
