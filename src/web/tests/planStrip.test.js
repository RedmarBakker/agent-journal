import {createApp, nextTick} from "vue";
import {expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};
const peeked = vi.hoisted(() => []);
vi.mock("../src/route.js", async (original) => ({...(await original()), peek: (table, id) => peeked.push(`${table}/${id}`)}));
const {default: StatusBar} = await import("../src/layout/StatusBar.vue");
const {store} = await import("../src/state/store.js");
const {choose} = await import("../src/state/environment.js");

const plan = (id, title) => ({table: "plans", id, title, state: "started", held: false, delegated: false, current_phase: 1, phase_count: 2, task_count: 4, task_ids: [10 * id, 10 * id + 1, 10 * id + 2, 10 * id + 3], phases: [{title: `Phase one of ${title}`, task_ids: [10 * id]}, {title: "Second", task_ids: []}], created_at: "2026-10-25T10:00:00Z"});

test("the toggle folds three started plans into one strip of icon, number and progress, a hover opens the plan's panel, and the toggle opens the bar again", async () => {
    choose("main");
    store.agents = [];
    store.summary = {environments: [{environment: {id: 1, name: "main"}, agent: null, task: null, questions: 0, messages: 0, tasks: 0, silent: false}]};
    store.settings = {features: {}, tasks: {auto: true}, workers: {mode: "builder"}};
    store.rows.plans = [plan(1, "Floors"), plan(2, "Walls"), plan(3, "Roof")];
    store.rows.tasks = [1, 2, 3].flatMap((id) => [10 * id, 10 * id + 1, 10 * id + 2, 10 * id + 3].map((n) => ({table: "tasks", id: n, state: n === 10 * id ? "completed" : "open", completed_at: null})));
    const host = window.document.createElement("div");
    window.document.body.append(host);
    const app = createApp(StatusBar);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelectorAll(".planbar").length).toBe(3);
    expect(host.querySelector(".planstrip")).toBe(null);
    host.querySelector(".statusbar-strip").click();
    await nextTick();
    expect(host.querySelectorAll(".planbar").length).toBe(0);
    expect(host.querySelectorAll(".planstrip").length).toBe(1);
    const groups = [...host.querySelectorAll(".planstrip-plan")];
    expect(groups.map((group) => [group.querySelector("svg, .planstrip-icon") !== null, group.querySelector(".planstrip-number").textContent, group.querySelector(".planstrip-track") !== null])).toEqual([
        [true, "1", true],
        [true, "2", true],
        [true, "3", true],
    ]);
    expect(JSON.parse(localStorage.getItem("journal.plan_strip"))).toBe(true);
    groups[1].dispatchEvent(new window.MouseEvent("mouseenter"));
    await nextTick();
    const card = window.document.querySelector(".planstrip-card");
    expect(card.textContent).toContain("Walls");
    expect(card.textContent).toContain("Phase 1 of 2 · Phase one of Walls");
    expect(card.textContent).toContain("1 of 4 tasks done");
    card.querySelector(".planstrip-card-open").click();
    expect(peeked.at(-1)).toBe("plans/2");
    host.querySelector(".statusbar-strip").click();
    await nextTick();
    expect(host.querySelectorAll(".planbar").length).toBe(3);
    expect(host.querySelector(".planstrip")).toBe(null);
    app.unmount();
    host.remove();
});
