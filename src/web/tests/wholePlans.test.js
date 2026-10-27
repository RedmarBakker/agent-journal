import {effectScope, nextTick} from "vue";
import {expect, test, vi} from "vitest";

const api = {env: () => "main", list: vi.fn(), show: vi.fn()};
vi.mock("../src/api/client.js", () => ({api, onWrite: vi.fn()}));
vi.mock("../src/chat/outbox.js", () => ({onOutboxChange: vi.fn()}));

const {boardLines} = await import("../src/domain/taskBoard.js");
const {delegationOf, standingOf} = await import("../src/domain/plans.js");
const {wholePlans} = await import("../src/composables/wholePlans.js");
const {rows} = await import("../src/sync/rows.js");
const {store} = await import("../src/state/store.js");

const index = {table: "plans", id: 5, title: "The rest of the list", state: "started", current_phase: 1, delegated: true, phase_count: 2, task_count: 3};
const whole = {...index, phases: [{title: "First", task_ids: [1, 2]}, {title: "Second", task_ids: [3]}], task_ids: [1, 2, 3]};
const task = (id, state) => ({table: "tasks", id, title: `task ${id}`, state: state === "done" ? "completed" : state, plan_id: 5, priority: 0});
const tasks = [task(1, "done"), task(2, "open"), task(3, "open")];

test("a plan list row, which carries the plan alone, draws the task board without a throw and its tasks as loose ones", () => {
    const lines = boardLines("plan", {shown: tasks, all: tasks, plans: [index], folded: {}});
    expect(lines.filter((line) => line.type === "row").map((line) => line.task.id)).toEqual([1, 2, 3]);
    expect(delegationOf(index, {tasks, workers: []})).toBe(null);
});

test("a plan read whole draws its phases on the task board and counts its done tasks", () => {
    const lines = boardLines("plan", {shown: tasks, all: tasks, plans: [whole], folded: {}});
    expect(lines.filter((line) => line.type === "head").map((line) => line.label)).toEqual(["The rest of the list", "Phase 1 of 2: First", "Phase 2 of 2: Second"]);
    expect(standingOf(whole, tasks).title).toBe("1 of 3 tasks done");
});

test("a view that shows a plan asks for it whole by its id, once, and reads its phases from it", async () => {
    store.rows.plans = [index];
    api.show.mockResolvedValue(whole);
    const scope = effectScope();
    scope.run(() => wholePlans(() => [5]));
    await vi.waitFor(() => expect(rows("plans")[0].task_ids).toEqual([1, 2, 3]));
    await nextTick();
    expect(api.show.mock.calls).toEqual([["plans", 5]]);
    expect(api.list).not.toHaveBeenCalled();
    scope.stop();
});
