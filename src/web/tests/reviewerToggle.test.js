import {createApp, nextTick} from "vue";
import {expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
const {default: StatusBar} = await import("../src/layout/StatusBar.vue");
const {store} = await import("../src/state/store.js");
const {choose} = await import("../src/state/environment.js");
const {api} = await import("../src/api/client.js");

const words = (host) => [...host.querySelectorAll(".statusbar-agentset .switch-inner")].map((word) => word.textContent.trim());

test("in orchestrator mode the plan bar shows the Reviewer switch in place of Auto, beside Approves plans, and the switch saves the reviewer setting", async () => {
    choose("main");
    store.agents = [];
    store.summary = {environments: [{environment: {id: 1, name: "main"}, agent: null, task: null, questions: 0, messages: 0, tasks: 0, silent: false}]};
    store.settings = {features: {}, tasks: {auto: true}, workers: {mode: "builder"}, reviewing: {reviewer: false}};
    const save = vi.spyOn(api, "saveSettings").mockResolvedValue(null);
    const host = window.document.createElement("div");
    window.document.body.append(host);
    const app = createApp(StatusBar);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(words(host)).toEqual(["auto"]);
    store.settings = {...store.settings, workers: {mode: "orchestrator"}};
    await nextTick();
    expect(words(host)).toEqual(["reviewer", "approves plans"]);
    host.querySelector(".statusbar-agentset .switch-button").click();
    await nextTick();
    expect(save).toHaveBeenCalledWith({reviewing: {reviewer: true}});
    expect(store.settings.reviewing.reviewer).toBe(true);
    app.unmount();
    host.remove();
    save.mockRestore();
});
