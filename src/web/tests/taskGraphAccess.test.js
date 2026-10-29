import {createApp, h} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const {narrow} = vi.hoisted(() => ({narrow: {value: true}}));
vi.mock("../src/platform/view.js", () => ({narrow}));

const {default: TaskGraph} = await import("../src/tasks/TaskGraph.vue");
const {store} = await import("../src/state/store.js");
const {taskBoard} = await import("../src/state/taskBoard.js");

const tasks = [
    {table: "tasks", id: 1, title: "The task that waits", state: "blocked", waits: ["tasks:2"], block_reason: "", plan_id: null},
    {table: "tasks", id: 2, title: "The task it waits on", state: "open", waits: [], block_reason: "", plan_id: null},
];

let app = null;
let host = null;

beforeEach(() => {
    narrow.value = true;
    store.rows = {tasks, plans: [], questions: [], comments: [], checks: []};
    taskBoard.unfolded = {};
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("the task graph can be focused and its nodes remain keyboard buttons in a narrow layout", () => {
    const select = vi.fn();
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(TaskGraph, {tasks, onSelect: select})});
    app.mount(host);

    const graph = host.querySelector(".task-graph");
    expect(graph.getAttribute("role")).toBe("region");
    expect(graph.getAttribute("aria-label")).toBe("Task graph");
    expect(graph.tabIndex).toBe(0);
    expect(host.querySelector(".plane").style.width).toBe("350px");
    const nodes = [...host.querySelectorAll(".task-graph-node .box")];
    expect(nodes).toHaveLength(2);
    expect(nodes.every((node) => node.tagName === "BUTTON" && node.type === "button")).toBe(true);
    nodes[0].focus();
    expect(document.activeElement).toBe(nodes[0]);
    nodes[0].click();
    expect(select).toHaveBeenCalledWith(1);
});
