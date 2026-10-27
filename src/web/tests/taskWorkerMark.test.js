import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const {store} = await import("../src/state/store.js");
const {taskBoard} = await import("../src/state/taskBoard.js");
const {default: TasksTab} = await import("../src/tasks/TasksTab.vue");
const {default: TaskState} = await import("../src/tasks/TaskState.vue");

const task = (id, title, more = {}) => ({table: "tasks", id, title, brief: "", state: "open", plan_id: null, waits: [], block_reason: "", updated_at: new Date().toISOString(), ...more});
const working = task(4, "worker's", {state: "started", delegated: true, worker_id: 7});
const queued = task(2, "queued", {delegated: true, worker_id: 8});
const own = task(1, "the agent's own");
let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

async function mounted(component, props = {}) {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(component, props)});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    return host;
}

test("a task with a worker sits under its own state, in progress or open, with a worker icon naming the worker on hover", async () => {
    store.rows = {tasks: [working, queued, own], plans: [], questions: [], workers: [{table: "workers", id: 7, name: "Lady Lovelace"}, {table: "workers", id: 8, name: "Mr. Eames"}]};
    Object.assign(taskBoard, {statuses: [], words: "", folded: {}});
    Object.assign(taskBoard.display, {showDone: false, number: true, wait: true});
    const host = await mounted(TasksTab);
    const drawn = [...host.querySelectorAll(".head .label, .task-row")].map((el) => (el.classList.contains("task-row") ? Number(el.dataset.task) : el.textContent.trim()));
    expect(drawn).toEqual(["In progress", 4, "Open", 1, 2]);
    expect(host.querySelector('.task-row[data-task="4"] .task-worker').title).toBe("With Lady Lovelace");
    expect(host.querySelector('.task-row[data-task="2"] .task-worker').title).toBe("With Mr. Eames");
    expect(host.querySelector('.task-row[data-task="1"] .task-worker')).toBeNull();
    expect(host.textContent).not.toContain("With a worker");
    app.unmount();
    const inspector = await mounted(TaskState, {task: working, tasks: [working, queued, own]});
    expect(inspector.querySelector(".state").textContent.trim()).toBe("In progress");
    expect(inspector.querySelector(".state-line .task-worker").title).toBe("With Lady Lovelace");
});
