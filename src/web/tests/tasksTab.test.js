import {createApp} from "vue";
import {afterEach, beforeEach, describe, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};
window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {api} = await import("../src/api/client.js");
const {store} = await import("../src/state/store.js");
const {taskBoard} = await import("../src/state/taskBoard.js");
const {default: TasksTab} = await import("../src/tasks/TasksTab.vue");

const task = (id, title, state, more = {}) => ({table: "tasks", id, title, brief: "", state, plan_id: null, waits: [], block_reason: "", ...more});
let app = null;

beforeEach(() => {
    store.rows = {
        tasks: [task(1, "paused one", "paused"), task(2, "blocked one", "blocked", {block_reason: "the release"}), task(3, "open one", "open"), task(4, "done one", "done", {finished_at: "2026-10-21T10:00:00+00:00"})],
        plans: [],
        questions: [],
        checks: [],
    };
    Object.assign(taskBoard, {view: "list", selected: 0, inspecting: false, statuses: [], words: "", folded: {}, draft: null});
    Object.assign(taskBoard.display, {grouping: "plan", showDone: false, number: true, wait: true});
    vi.spyOn(api, "act").mockResolvedValue({});
});

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    location.hash = "";
    vi.restoreAllMocks();
});

async function shown() {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp(TasksTab);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    return host;
}

describe("the chat's Tasks tab", () => {
    test("draws the tasks dialog's own list and rows, grouped by status, with the done ones left out", async () => {
        const host = await shown();
        const heads = [...host.querySelectorAll(".tasks-tab .task-list .head .label")].map((h) => h.textContent.trim());
        expect(heads).toEqual(["Blocked", "Paused", "Open"]);
        expect([...host.querySelectorAll(".tasks-tab .task-row")].map((r) => r.dataset.task)).toEqual(["2", "1", "3"]);
        expect(host.querySelector('.task-row[data-task="2"] .wait').textContent).toBe("Blocked: the release");
    });

    test("a row clicked opens that task in the tasks dialog's inspector", async () => {
        const host = await shown();
        host.querySelector('.task-row[data-task="3"]').click();
        expect(location.hash).toBe("#/tasks/3");
    });

    test("open tasks are ordered critical, high, normal, low and then by number, each row marking its priority after the status icon", async () => {
        store.rows.tasks = [task(5, "low", "open", {priority: 50}), task(4, "normal", "open", {priority: 100}), task(3, "critical", "open", {priority: 200}), task(2, "high", "open", {priority: 150}), task(1, "also normal", "open")];
        const host = await shown();
        expect([...host.querySelectorAll(".tasks-tab .task-row")].map((r) => r.dataset.task)).toEqual(["3", "2", "1", "4", "5"]);
        const marks = (id) => host.querySelector(`.task-row[data-task="${id}"] .prio`).classList;
        expect(marks(3).contains("hot")).toBe(true);
        expect(marks(2).contains("high")).toBe(true);
        expect(marks(1).contains("hot") || marks(1).contains("high")).toBe(false);
        expect(marks(5).contains("hot") || marks(5).contains("high")).toBe(false);
        const row = host.querySelector('.task-row[data-task="3"]');
        expect(row.querySelector(".status").nextElementSibling).toBe(row.querySelector(".priority"));
    });
});
