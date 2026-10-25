import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};
window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {api} = await import("../src/api/client.js");
const {store} = await import("../src/state/store.js");
const {choose} = await import("../src/state/environment.js");
const {default: TaskPanel} = await import("../src/tasks/TaskPanel.vue");

let app = null;
choose("main");
afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

const task = {table: "tasks", id: 3, title: "open one", brief: "", state: "open", plan_id: null, waits: [], priority: 100};

test("a task opened on its own renders the tasks dialog's own inspector, whose priority control saves through the tasks route", async () => {
    store.rows = {tasks: [task], plans: [], questions: [], checks: []};
    vi.spyOn(api, "get").mockResolvedValue({rows: []});
    const change = vi.spyOn(api, "change").mockResolvedValue({});
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(TaskPanel, {task})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".task-inspector")).not.toBeNull();
    const options = [...host.querySelectorAll(".task-inspector .segmented-option")];
    expect(options.map((o) => o.textContent.trim())).toEqual(["Low", "Normal", "High", "Critical"]);
    options[3].click();
    await flush();
    expect(change).toHaveBeenCalledWith("tasks", 3, {priority: 200});
});
