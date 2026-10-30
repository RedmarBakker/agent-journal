import {createApp} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

vi.mock("../src/api/client.js", async (original) => ({...(await original()), api: {...(await original()).api, list: vi.fn(async () => ({rows: [], is_last_page: true, counts: {}})), show: vi.fn(async () => ({}))}}));

const {default: PlansTab} = await import("../src/plans/PlansTab.vue");
const {store} = await import("../src/state/store.js");

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    host?.remove();
    store.rows = {};
});

const plan = (id, state, title, more = {}) => ({table: "plans", id, state, title, phases: [], task_ids: [], phase_count: 2, task_count: 4, held: false, delegated: false, ...more});
const text = (node) => node.textContent.replace(/\s+/g, " ").trim();

async function mounted(rows) {
    store.rows = rows;
    host = document.createElement("div");
    document.body.append(host);
    app = createApp(PlansTab);
    app.directive("tip", {});
    app.mount(host);
    await flush();
}

test("the Plans window shows a running plan as a card with its state, its reason, its task in hand and its tasks done, then the waiting plans as rows, and no closed plan", async () => {
    const running = plan(7, "blocked", "Teams in the sidebar", {block_reason: "Waiting for the release", task_ids: [70, 71], task_count: 2, current_phase: 1});
    await mounted({
        plans: [running, plan(3, "ready", "Phase-end testing"), plan(5, "done", "Skills as a map", {updated_at: "2026-10-30T10:00:00+00:00"})],
        tasks: [
            {table: "tasks", id: 70, plan_id: 7, state: "completed", title: "Team rows"},
            {table: "tasks", id: 71, plan_id: 7, state: "started", title: "Team page routes"},
        ],
    });
    expect([...host.querySelectorAll(".plans-head")].map(text)).toEqual(["Being worked on 1", "Waiting to start 1"]);
    const card = host.querySelector(".run");
    expect([text(card.querySelector(".state-name")), text(card.querySelector(".state-why"))]).toEqual(["Blocked", "Waiting for the release"]);
    expect([...card.querySelectorAll(".pair-label")].map(text)).toEqual(["Current phase", "Task being worked on"]);
    expect(text(card.querySelector(".worker"))).toBe("71Team page routes");
    expect(text(card.querySelector(".done"))).toBe("1 of 2 tasks done");
    expect(card.querySelector(".bar").classList.contains("stalled")).toBe(true);
    const row = host.querySelector(".wait");
    expect([text(row.querySelector(".wait-title")), text(row.querySelector(".state-name")), text(row.querySelector(".size"))]).toEqual(["Phase-end testing", "Ready, waiting for your approval", "2 phases · 4 tasks"]);
    expect(text(row.querySelector(".act"))).toBe("Approve");
});

test("a plan with workers names each worker holding one of its open tasks with the job it was given", async () => {
    const phases = [{id: 1, title: "Team page", task_ids: [80]}, {id: 2, title: "Several teams per project", task_ids: [81, 82]}];
    const delegated = plan(9, "delegated", "Teams in the sidebar", {delegated: true, current_phase: 2, phases, task_ids: [80, 81, 82], task_count: 3});
    await mounted({
        plans: [delegated],
        tasks: [
            {table: "tasks", id: 80, plan_id: 9, state: "completed", title: "Team page", worker_id: null},
            {table: "tasks", id: 81, plan_id: 9, state: "open", title: "Account list", worker_id: 4},
            {table: "tasks", id: 82, plan_id: 9, state: "open", title: "Connect a team", worker_id: null},
        ],
        workers: [{table: "workers", id: 4, name: "Mr. Brunel", brief: "Team stories for several teams"}],
    });
    const card = host.querySelector(".run");
    expect(text(card.querySelector(".state-name"))).toBe("With workers");
    expect([...card.querySelectorAll(".pair-label")].map(text)).toEqual(["Current phase", "Workers on this plan"]);
    expect(text(card.querySelector(".pair-value"))).toBe("Phase 2 of 2 · Several teams per project");
    expect(text(card.querySelector(".worker"))).toBe("Mr. Brunel81 Account list");
});

test("the Plans window with no open plan says so", async () => {
    await mounted({plans: [plan(5, "done", "Skills as a map", {updated_at: "2026-10-30T10:00:00+00:00"})], tasks: []});
    expect(text(host.querySelector(".plans-empty h4"))).toBe("No open plans");
    expect(host.querySelector(".run")).toBe(null);
});
