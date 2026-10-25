import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const {api} = await import("../src/api/client.js");
const {choose} = await import("../src/state/environment.js");
const {store} = await import("../src/state/store.js");
const {default: StatusBar} = await import("../src/layout/StatusBar.vue");

let app = null;
const lead = (fitness) => ({id: 1, role: "main", session: "s", status: "working", state: "following_plan", heard_at: "2026-10-25T10:00:00+00:00", fitness});

beforeEach(() => {
    choose("main");
    vi.spyOn(api, "get").mockResolvedValue([]);
    store.agents = [];
    store.rows = {};
});

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

async function bar() {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(StatusBar)});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    return host;
}

test("the top bar shows the lead agent's fitness score left of the mode buttons, and a dash while it is not measured yet", async () => {
    store.agents = [lead({mode: "builder", score: 88, is_measured: true, lines: [], timeline: [], timeline_hours: 6})];
    const host = await bar();
    expect(host.querySelector(".statusbar-fitness").textContent.trim()).toBe("88");
    store.agents = [lead({mode: "builder", score: 100, is_measured: false, lines: [], timeline: [], timeline_hours: 6})];
    await nextTick();
    expect(host.querySelector(".statusbar-fitness").textContent.trim()).toBe("–");
});

test("the Fold the plans button is the last button before the full screen button", async () => {
    store.agents = [lead(null)];
    store.rows = {plans: [{table: "plans", id: 1, title: "A plan", state: "started", task_ids: [], phases: []}]};
    const host = await bar();
    const strip = host.querySelector(".statusbar-strip");
    const wide = host.querySelector('[data-step="fullscreen"]');
    expect(strip).not.toBeNull();
    expect(strip.nextElementSibling).toBe(wide);
});

test("the load shows for the builder and the orchestrator and is hidden in solo, and the builder's warns at its own ceiling", async () => {
    const withLoad = (rho) => ({...lead(null), load: {rho, arrivals: 10, clearings: 20, waiting: 1, wait_minutes: 1, waiting_refs: []}});
    store.settings = {features: {}, tasks: {}, workers: {mode: "builder", builder_load_ceiling: 0.5}, reviewing: {}};
    store.agents = [withLoad(0.6)];
    const host = await bar();
    expect(host.querySelector(".statusbar-load").classList.contains("warn")).toBe(true);
    store.settings = {...store.settings, workers: {mode: "solo"}};
    await nextTick();
    expect(host.querySelector(".statusbar-load")).toBeNull();
    store.settings = {...store.settings, workers: {mode: "orchestrator"}};
    await nextTick();
    expect(host.querySelector(".statusbar-load").classList.contains("warn")).toBe(false);
});
