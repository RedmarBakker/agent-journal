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
const lead = () => ({id: 1, role: "main", session: "s", status: "working", state: "following_plan", heard_at: "2026-10-25T10:00:00+00:00"});

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

test("the top bar has no agent mode or fitness controls", async () => {
    store.agents = [lead()];
    const host = await bar();
    expect(host.querySelector(".statusbar-mode")).toBeNull();
    expect(host.querySelector(".statusbar-fitness")).toBeNull();
});

test("the top bar shows the generic load and uses the configured warning levels", async () => {
    const withLoad = (rho) => ({...lead(), load: {rho, work: {rho, arrivals: 10, clearings: 20, waiting: 1, wait_minutes: 1, waiting_refs: []}, messages: null}});
    store.settings = {features: {}, tasks: {}, workers: {load_warn: 0.5, load_critical: 0.9}, reviewing: {}};
    store.agents = [withLoad(0.6)];
    const host = await bar();
    expect(host.querySelector(".statusbar-load").classList.contains("warn")).toBe(true);
    expect(host.querySelector(".statusbar-load").textContent.trim()).toBe("0.60");
    store.settings = {...store.settings, workers: {load_warn: 0.7, load_critical: 0.9}};
    await nextTick();
    expect(host.querySelector(".statusbar-load").classList.contains("warn")).toBe(false);
    store.settings = {...store.settings, workers: {load_warn: 0.7, load_critical: 0.55}};
    await nextTick();
    expect(host.querySelector(".statusbar-load").classList.contains("critical")).toBe(true);
});
