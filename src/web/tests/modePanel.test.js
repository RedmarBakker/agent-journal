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

test("hovering the Orchestrator button shows its one-line description and its toggles each with a line under it, plan approval's choices only while it is on, no fitness, and the plan bar keeps none of them", async () => {
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
    expect(toggles.map((toggle) => toggle.textContent.trim())).toEqual(["May write plans", "Approves plans", "May release", "Reviewer"]);
    expect(toggles.map((toggle) => toggle.getAttribute("aria-checked"))).toEqual(["true", "false", "false", "false"]);
    expect([...panel.querySelectorAll(".tip-toggle-note")].map((note) => note.textContent.trim())).toEqual([
        "Drafts plans itself with journal plan create. Off, only you write a plan.",
        "Approves plans itself with journal plan approve. Off, only you approve a plan.",
        "Tags a version and publishes a release. Off, a git tag or gh release waits for you.",
        "A reviewer reads each worker's proofs and runs their tests before you merge.",
    ]);
    expect(panel.textContent).not.toContain("Fitness");
    expect(panel.querySelectorAll(".tip-toggle-choices").length).toBe(0);
    toggles[1].click();
    await nextTick();
    expect(save).toHaveBeenCalledWith({workers: {orchestrator_approves_plans: true}});
    expect(panel.querySelectorAll(".tip-toggle")[1].getAttribute("aria-checked")).toBe("true");
    const choices = [...panel.querySelectorAll(".tip-toggle-choices .choice")];
    expect(choices.map((choice) => choice.textContent.trim())).toEqual(["Only its own", "Plans you made", "All plans"]);
    expect(choices.map((choice) => choice.getAttribute("aria-selected"))).toEqual(["false", "false", "true"]);
    choices[1].click();
    expect(save).toHaveBeenCalledWith({workers: {orchestrator_plan_approval: "can approve plans the user made"}});
    panel.querySelectorAll(".tip-toggle")[3].click();
    expect(save).toHaveBeenCalledWith({reviewing: {reviewer: true}});
    app.unmount();
    host.remove();
    save.mockRestore();
});
