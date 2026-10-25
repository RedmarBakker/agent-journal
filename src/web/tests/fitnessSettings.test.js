import {createApp, h} from "vue";
import {expect, test, vi} from "vitest";

const went = vi.hoisted(() => []);
vi.mock("../src/route.js", async (original) => ({...(await original()), go: (...args) => went.push(args)}));
const {default: FitnessTimeline} = await import("../src/layout/FitnessTimeline.vue");

test("the fitness panel's cogwheel opens the settings page on the Fitness settings, and closes the panel", async () => {
    const host = document.body.appendChild(document.createElement("div"));
    const closed = vi.fn();
    const app = createApp({render: () => h(FitnessTimeline, {score: 80, lines: [], points: [], hours: 4, low: 70, onClose: closed})});
    app.directive("tip", {});
    app.mount(host);
    host.querySelector('[aria-label="Open the fitness settings"]').click();
    expect(went.at(-1)).toEqual(["settings", 0, "Fitness:"]);
    expect(closed).toHaveBeenCalled();
    app.unmount();
});

test("the settings page opens on the search the address names", async () => {
    const {readFileSync} = await import("node:fs");
    expect(readFileSync("src/pages/SettingsPage.vue", "utf8")).toContain("const query = ref(route.value.q);");
});
