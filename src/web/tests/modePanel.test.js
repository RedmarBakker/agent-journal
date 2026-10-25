import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
const {default: StatusBar} = await import("../src/layout/StatusBar.vue");
const {default: Tooltip} = await import("../src/kit/Tooltip.vue");
const {tip} = await import("../src/kit/tip.js");
const {store} = await import("../src/state/store.js");
const {choose} = await import("../src/state/environment.js");
const {api} = await import("../src/api/client.js");

const switches = (host) => [...host.querySelectorAll(".statusbar-agentset .switch-inner")].map((word) => word.textContent.trim());

test("hovering the Orchestrator button shows its one-line description and its settings as toggles, which change their settings, and the plan bar keeps none of them", async () => {
    choose("main");
    store.agents = [];
    store.summary = {environments: [{environment: {id: 1, name: "main"}, agent: null, task: null, questions: 0, messages: 0, tasks: 0, silent: false}]};
    store.settings = {features: {}, tasks: {auto: true}, workers: {mode: "builder", orchestrator_approves_plans: false}, reviewing: {reviewer: false}};
    const save = vi.spyOn(api, "saveSettings").mockResolvedValue(null);
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h("div", [h(StatusBar), h(Tooltip)])});
    app.directive("tip", tip);
    app.mount(host);
    await nextTick();
    expect(switches(host)).toEqual(["auto"]);
    store.settings = {...store.settings, workers: {...store.settings.workers, mode: "orchestrator"}};
    await nextTick();
    expect(switches(host)).toEqual([]);
    const orchestrator = [...host.querySelectorAll(".statusbar-mode .segmented-option")].find((button) => button.textContent.trim() === "Orchestrator");
    orchestrator.dispatchEvent(new MouseEvent("pointerover", {bubbles: true}));
    await nextTick();
    await nextTick();
    const panel = host.querySelector(".tooltip");
    expect(panel.hidden).toBe(false);
    expect(panel.querySelector(".tip-line").textContent.trim()).toBe("The agent plans, hands tasks to workers and reviews their work.");
    const toggles = [...panel.querySelectorAll(".tip-toggle")];
    expect(toggles.map((toggle) => toggle.textContent.trim())).toEqual(["May write plans", "Approves plans", "Approves only plans it did not write", "May release", "Reviewer"]);
    expect(toggles.map((toggle) => toggle.getAttribute("aria-checked"))).toEqual(["true", "false", "false", "false", "false"]);
    toggles[1].click();
    await nextTick();
    expect(save).toHaveBeenCalledWith({workers: {orchestrator_approves_plans: true}});
    expect(panel.querySelectorAll(".tip-toggle")[1].getAttribute("aria-checked")).toBe("true");
    panel.querySelectorAll(".tip-toggle")[4].click();
    expect(save).toHaveBeenCalledWith({reviewing: {reviewer: true}});
    app.unmount();
    host.remove();
    save.mockRestore();
});
