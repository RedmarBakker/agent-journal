import {createApp, h, nextTick, ref} from "vue";
import {expect, test, vi} from "vitest";

const api = {env: () => "main", list: vi.fn(), onWrite: vi.fn()};
vi.mock("../src/api/client.js", () => ({api, onWrite: vi.fn()}));

const {default: PlanPhase} = await import("../src/resource/PlanPhase.vue");
const {useWorkersHolding} = await import("../src/composables/workers.js");

test("a plan that opens reads the workers holding its tasks by the task numbers and shows each one's worker beside its task", async () => {
    vi.useFakeTimers();
    vi.spyOn(document, "hasFocus").mockReturnValue(true);
    api.list.mockResolvedValue({rows: [{id: 3, name: "Lady Lovelace", state: "dispatched", holds: [7]}]});
    const tasks = ref([{table: "tasks", id: 7, title: "Task 7", state: "open", completed_at: null}]);
    const into = document.createElement("div");
    document.body.append(into);
    createApp({
        setup() {
            const {rows, loaded} = useWorkersHolding(tasks);
            return () => h(PlanPhase, {phase: {i: 1, title: "Members", task_ids: [7], rows: tasks.value, waiting: 0}, workers: rows.value, workersLoaded: loaded.value});
        },
    }).mount(into);
    await vi.advanceTimersByTimeAsync(0);
    await nextTick();
    expect(api.list.mock.calls).toEqual([["workers", {tasks: [7]}]]);
    expect(into.textContent).toContain("Lady Lovelace");
    vi.useRealTimers();
});
