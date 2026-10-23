import {computed, ref} from "vue";
import {usePoll} from "./poll.js";

// the rows a workers poller hands over, and whether it has answered yet
function workerRows() {
    const rows = ref([]);
    const loaded = ref(false);
    const take = (got) => {
        rows.value = got;
        loaded.value = true;
    };
    return {rows, loaded, take};
}

export function useWorkers() {
    const {rows, loaded, take} = workerRows();
    return {rows, loaded, refresh: usePoll("workers.index", {take})};
}

export function useEveryWorker(open) {
    const {rows, loaded, take} = workerRows();
    return {rows, loaded, refresh: usePoll("workers.every", {take, active: () => open.value})};
}

// The workers that hold any of these tasks.
export function useWorkersHolding(tasks) {
    const ids = computed(() => [...new Set(tasks.value.map((t) => t.worker_id).filter(Boolean))]);
    const {rows, loaded, take} = workerRows();
    return {rows, loaded, refresh: usePoll("workers.holding", {params: () => ({ids: ids.value}), take, active: () => ids.value.length > 0})};
}
