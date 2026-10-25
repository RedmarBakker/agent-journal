<script setup>
import {computed} from "vue";
import {boardColumns} from "../domain/hub.js";

const props = defineProps({tasks: {type: Array, default: () => []}});
const emit = defineEmits(["open"]);
const columns = computed(() => boardColumns(props.tasks));
</script>

<template>
    <div class="board" data-hub-board>
        <template v-for="column in columns" :key="column.key">
            <section class="column" :data-column="column.key">
                <h3 class="head">{{ column.title }} <span class="count">{{ column.tasks.length }}</span></h3>
                <template v-for="task in column.tasks" :key="task.id">
                    <button type="button" class="card" @click="emit('open', task)">Task {{ task.id }}: {{ task.title }}</button>
                </template>
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
    text-align: left;
    padding: 8px 10px;
    font-size: 12.5px;
    color: var(--text);
    background: var(--bg-2, var(--bg));
    border: 1px solid var(--border);
    border-radius: 6px;
}
</style>
