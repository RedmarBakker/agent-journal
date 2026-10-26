import {createApp, h, nextTick, reactive} from "vue";
import {expect, test, vi} from "vitest";

vi.mock("../src/route.js", async (original) => ({...(await original()), peek: vi.fn()}));
globalThis.ResizeObserver ??= class {
    observe() {}
    disconnect() {}
};

const whole = (phases) => ({table: "plans", id: 5, title: "Plan", state: "draft", task_ids: [], phases: phases.map((title) => ({title, task_ids: []}))});
const summary = {table: "plans", id: 5, title: "Plan", state: "draft"};

test("the docked plan card keeps its rows mounted when a refresh brings the plan as a summary and when phases are added", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: PlanCard} = await import("../src/chat/PlanCard.vue");
    const held = reactive({plan: whole(["First", "Second"])});
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(PlanCard, {plan: held.plan, folded: false})});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const card = host.querySelector(".chat-dock-card");
    const first = [...host.querySelectorAll(".plan-card-phase:not(.quiet)")];
    expect(first.length).toBe(2);
    held.plan = summary;
    await nextTick();
    expect([...host.querySelectorAll(".plan-card-phase:not(.quiet)")], "a summary refresh draws no row away").toEqual(first);
    held.plan = whole(["First", "Second", "Third"]);
    await nextTick();
    const grown = [...host.querySelectorAll(".plan-card-phase:not(.quiet)")];
    expect(grown.length).toBe(3);
    expect(grown.slice(0, 2), "an added phase leaves the rows before it mounted").toEqual(first);
    expect(host.querySelector(".chat-dock-card"), "the card itself stays").toBe(card);
    app.unmount();
    host.remove();
});
