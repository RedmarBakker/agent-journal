import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";
import {store} from "../src/state/store.js";

vi.mock("../src/actions/settings.js", () => ({saveSettings: vi.fn(async () => ({}))}));

test("the fitness dropdown switches the fitness warnings to the agent off and on", async () => {
    const {saveSettings} = await import("../src/actions/settings.js");
    const {default: FitnessTimeline} = await import("../src/layout/FitnessTimeline.vue");
    store.settings = {workers: {}};
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(FitnessTimeline, {score: 40, hours: 6, low: 75})});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const toggle = host.querySelector(".fitness-timeline-warnings [role=switch]");
    expect(toggle.getAttribute("aria-checked")).toBe("true");
    toggle.click();
    expect(saveSettings).toHaveBeenCalledWith({workers: {fitness_warnings: false}});
    app.unmount();
    host.remove();
});
