import {effectScope} from "vue";
import {expect, test, vi} from "vitest";

const api = {env: () => "main", list: vi.fn()};
vi.mock("../src/api/client.js", () => ({api, onWrite: vi.fn()}));
vi.mock("../src/chat/outbox.js", () => ({onOutboxChange: vi.fn()}));

const {usePlanRows} = await import("../src/composables/planRows.js");
const {barPlans, delegationOf, planProgress, standingOf} = await import("../src/domain/plans.js");
const {rows} = await import("../src/sync/rows.js");
const {store} = await import("../src/state/store.js");

const index = {table: "plans", id: 5, title: "Going", state: "started", phase_count: 2, task_count: 3};
const whole = {...index, phases: [{title: "One", task_ids: [1, 2]}, {title: "Two", task_ids: [3]}], task_ids: [1, 2, 3], current_phase: 2, held: false, delegated: true};
const task = (id, state) => ({table: "tasks", id, title: `t${id}`, state, plan_id: 5});

test("a started plan listed as a summary is read whole, then its tasks, so the bar counts its done tasks and draws its phase with no error", async () => {
    store.rows.plans = [index];
    store.rows.tasks = [];
    api.list.mockImplementation(async (table, query) => ({
        rows: table === "plans" ? [whole] : [task(1, "done"), task(2, "done"), task(3, "open")].filter((t) => query.ids.includes(t.id)),
        is_last_page: true,
        counts: {},
    }));
    const scope = effectScope();
    scope.run(() => usePlanRows(() => rows("plans")));
    await vi.waitFor(() => expect(rows("tasks")).toHaveLength(3));
    const [plan] = rows("plans");
    expect(api.list.mock.calls).toContainEqual(["plans", {ids: [5]}]);
    expect(standingOf(plan, rows("tasks")).title).toBe("2 of 3 tasks done");
    expect(planProgress(plan)).toMatchObject({total: 2, phase: 2, finished: 1});
    expect(barPlans(rows("plans"))).toEqual([plan]);
    expect(() => delegationOf(index, {tasks: [], workers: []})).not.toThrow();
    expect(delegationOf(plan, {tasks: rows("tasks"), workers: []}).line).toBe("Delegated");
    scope.stop();
});
