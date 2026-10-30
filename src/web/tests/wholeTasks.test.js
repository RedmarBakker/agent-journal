import {effectScope} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

const listed = vi.fn(async (table, {ids}) => ({rows: ids.map((id) => ({table, id, state: "open", title: `task ${id}`, updated_at: "2026-10-30T15:00:00+00:00", plan_id: 1057}))}));
vi.mock("../src/api/client.js", async (original) => ({...(await original()), api: {...(await original()).api, list: listed}}));

const {wholeTasks} = await import("../src/composables/wholeTasks.js");
const {groupOf} = await import("../src/domain/records.js");
const {store} = await import("../src/state/store.js");

afterEach(() => {
    store.rows = {};
    listed.mockClear();
});

test("the open tasks the Home page lists as list rows are read whole once, so a plan's task waits under Planned", async () => {
    const row = (id, fields = {}) => ({table: "tasks", id, state: "open", title: `task ${id}`, updated_at: "2026-10-30T15:00:00+00:00", ...fields});
    store.rows = {tasks: [row(4481), row(4489), row(12, {state: "completed", completed_at: "2026-10-30T14:00:00+00:00"})]};
    const scope = effectScope();
    scope.run(() => wholeTasks(() => store.rows.tasks || []));
    await flush();
    expect(listed).toHaveBeenCalledTimes(1);
    expect(listed.mock.calls[0][1].ids, "the open list rows alone, in one request").toEqual([4481, 4489]);
    expect(store.rows.tasks.filter((t) => t.id !== 12).map(groupOf)).toEqual(["planned", "planned"]);
    scope.stop();
});
