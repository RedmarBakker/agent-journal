import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {api} = await import("../src/api/client.js");
const {default: DeveloperPanel} = await import("../src/pages/DeveloperPanel.vue");

afterEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("the Developer tab opens the timings of hooks and requests, the newest requests, the records read and the nudge counts from a button into a side inspector", async () => {
    const measured = {count: 2, average_ms: 12, slowest_ms: 20};
    const numbers = vi.spyOn(api, "developer").mockResolvedValue({hooks: measured, requests: measured, by_kind: {}, recent: [{time: 1, method: "GET", route: "/journal/tasks", ms: 12}], slowest: [], loads: [], models: []});
    const nudges = vi.spyOn(api, "developerNudges").mockResolvedValue({agents: []});
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(DeveloperPanel)});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(document.body.textContent).not.toContain("Time to answer, in milliseconds");
    expect(numbers).not.toHaveBeenCalled();
    [...host.querySelectorAll("button")].find((b) => b.textContent.trim() === "Open the developer numbers").click();
    await flush();
    const panel = document.querySelector("aside.panel");
    expect(panel.getAttribute("aria-label")).toBe("Developer numbers");
    expect(panel.textContent).toContain("Time to answer, in milliseconds");
    expect(panel.textContent).toContain("/journal/tasks");
    expect(panel.textContent).toContain("Records read per kind since the last reset");
    expect([numbers.mock.calls.length > 0, nudges.mock.calls.length > 0]).toEqual([true, true]);
    app.unmount();
});
