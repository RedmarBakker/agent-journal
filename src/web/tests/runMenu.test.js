import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const {api} = await import("../src/api/client.js");
const {choose} = await import("../src/state/environment.js");
const {default: RunMenu} = await import("../src/chat/RunMenu.vue");

const running = [
    {id: 4, title: "Testing the update", command: "journal update-matrix", began_at: 1, card: 30, docked: true},
    {id: 5, title: "Building the viewer", command: "journal build-viewer", began_at: 2, card: 31, docked: false},
];
let app = null;
choose("main");

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

async function mounted() {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(RunMenu)});
    app.directive("tip", {});
    app.mount(host);
    for (let i = 0; i < 20 && !host.querySelector(".run-menu-strip"); i++) await flush();
    return host;
}

test("a slim strip counts the processes running and lists each, docked or not, and a click docks one that is not", async () => {
    vi.spyOn(api, "runningOutputs").mockResolvedValue({outputs: running});
    const act = vi.spyOn(api, "act").mockResolvedValue({});
    const host = await mounted();
    expect(host.querySelector(".run-menu-strip").textContent.trim()).toBe("Running: 2");
    host.querySelector(".run-menu-strip").click();
    await flush();
    const items = [...document.querySelectorAll(".run-menu-item")];
    expect(items.map((item) => [...item.children].map((part) => part.textContent.trim()))).toEqual([["Testing the update", "Docked"], ["Building the viewer", "Dock it"]]);
    expect(items[0].disabled).toBe(true);
    items[1].click();
    await flush();
    expect(act).toHaveBeenCalledWith("messages", 31, "dock");
});

test("with no process running there is no strip", async () => {
    vi.spyOn(api, "runningOutputs").mockResolvedValue({outputs: []});
    const host = await mounted();
    expect(host.querySelector(".run-menu-strip")).toBeNull();
});
