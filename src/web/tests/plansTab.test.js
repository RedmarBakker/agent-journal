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

test("the Plans window shows the plans waiting to start with their state and progress, and no closed plan", async () => {
    const plan = (id, state, title, more = {}) => ({table: "plans", id, state, title, phases: [], task_ids: [], phase_count: 2, task_count: 4, held: false, delegated: false, ...more});
    store.rows = {plans: [plan(3, "ready", "Teams in the sidebar"), plan(5, "done", "Skills as a map", {updated_at: "2026-10-30T10:00:00+00:00"})], tasks: []};
    host = document.createElement("div");
    document.body.append(host);
    app = createApp(PlansTab);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect([...host.querySelectorAll(".plans-head")].map((h) => h.textContent.replace(/\s+/g, " ").trim())).toEqual(["Waiting to start 1"]);
    const rows = [...host.querySelectorAll(".plan-row")].map((r) => [r.querySelector(".plan-title").textContent, r.querySelector(".plan-state").textContent, r.querySelector(".plan-progress").textContent]);
    expect(rows).toEqual([
        ["Teams in the sidebar", "Ready", "0 of 4 tasks done · 2 phases · 4 tasks"],
    ]);
});
