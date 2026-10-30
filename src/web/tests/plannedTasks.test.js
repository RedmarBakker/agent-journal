import {afterEach, expect, test} from "vitest";
import {groupOf} from "../src/domain/records.js";
import {store} from "../src/state/store.js";

afterEach(() => {
    store.rows = {};
});

const task = (fields) => ({table: "tasks", id: 1, state: "open", plan_id: null, ...fields});

test("an open task of a plan waits under Planned, also with its plan's row not loaded and its plan started", () => {
    store.rows = {};
    expect(groupOf(task({plan_id: 1057})), "the plan's row is not in the store").toBe("planned");
    store.rows = {plans: [{table: "plans", id: 1057, state: "started"}]};
    expect(groupOf(task({plan_id: 1057})), "the plan is started").toBe("planned");
    expect(groupOf(task({plan_id: null})), "a task of no plan stays open").toBe("open");
    expect(groupOf(task({plan_id: 1057, state: "started"})), "a plan's task in hand is in progress").toBe("started");
});
