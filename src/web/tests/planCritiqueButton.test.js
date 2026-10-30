import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

vi.mock("../src/route.js", async (original) => ({...(await original()), peek: vi.fn()}));
globalThis.ResizeObserver ??= class {
    observe() {}
    disconnect() {}
};

const ready = {table: "plans", id: 5, title: "Plan", state: "ready", task_ids: [], phases: [{title: "First", task_ids: []}]};

test("a ready plan's card asks for a critique with a button of its own beside Approve, never from the Approve menu", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: PlanCard} = await import("../src/chat/PlanCard.vue");
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(PlanCard, {plan: ready, folded: false})});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const buttons = [...host.querySelectorAll(".plan-card-acts button")].map((button) => button.textContent.trim());
    expect(buttons, "the critique is a button in the card's bar").toContain("Ask for a critique");
    host.querySelector(".plan-card-start button:last-child")?.click();
    await nextTick();
    const menu = [...document.querySelectorAll("[role='menuitem']")].map((item) => item.textContent.trim());
    expect(menu.some((item) => item.includes("critique")), "the Approve menu holds only ways to approve").toBe(false);
    app.unmount();
    host.remove();
});
