import {effectScope} from "vue";
import {afterEach, expect, test} from "vitest";
import {useHomeViews} from "../src/composables/homeViews.js";
import {recordCount} from "../src/domain/records.js";
import {store} from "../src/state/store.js";

afterEach(() => {
    store.rows = {};
    store.counts = {};
});

test("the Tasks and Plans windows count what the sidebar counts, not the rows the page happens to hold", () => {
    const task = (id, more = {}) => ({table: "tasks", id, state: "open", title: `task ${id}`, ...more});
    store.rows = {tasks: [task(1), task(2), task(3, {plan_id: 9})], plans: []};
    store.counts = {tasks: {all: 40, open: 10, unread: 0}, plans: {all: 5, open: 2, unread: 0}};
    const scope = effectScope();
    const {views} = scope.run(() => useHomeViews());
    expect(views.value.tasks.count).toBe(recordCount("tasks"));
    expect(views.value.tasks.count).toBe(10);
    expect(views.value.plans.count).toBe(2);
    scope.stop();
});
