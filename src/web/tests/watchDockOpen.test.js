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
const {default: WatchDock} = await import("../src/chat/WatchDock.vue");

const watched = {table: "messages", id: 7, author: "system", text: "Running the tests", data: {kind: "card", output: 12, line: "pytest -q", lines: ["FAILED test_b"], figure: "Tests 40%", fraction: 0.4, docked: true}};
let app = null;
choose("main");

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("a docked output is titled in words, names its command beneath, and opens on a click to its whole output in a box that scrolls", async () => {
    const read = vi.spyOn(api, "readOutput").mockResolvedValue({command: "pytest -q", outcome: "running", lines: ["collecting", "FAILED test_b", "[ 40%] test_c"]});
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(WatchDock, {message: watched})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-label").textContent.trim()).toBe("Running the tests");
    expect(host.querySelector(".watch-dock-command").textContent).toBe("pytest -q");
    expect(host.querySelector(".watch-dock-output")).toBeNull();
    host.querySelector(".watch-dock-label").click();
    await flush();
    expect(read).toHaveBeenCalledWith(12);
    expect(host.querySelector(".watch-dock-output").textContent).toBe("collecting\nFAILED test_b\n[ 40%] test_c");
    host.querySelector(".watch-dock-label").click();
    await flush();
    expect(host.querySelector(".watch-dock-output")).toBeNull();
});

test("a docked run shows its state as a dot in place of its icon, pulsing while it runs, blue while running, green once passed, red once failed, and no outline", async () => {
    const states = [];
    for (const data of [{tone: "", ending: ""}, {tone: "good", ending: "finished"}, {tone: "bad", ending: "failed with code 1"}]) {
        const host = document.createElement("div");
        document.body.append(host);
        app = createApp({render: () => h(WatchDock, {message: {...watched, data: {...watched.data, ...data}}})});
        app.directive("tip", {});
        app.mount(host);
        await flush();
        const card = host.querySelector(".chat-dock-card");
        const dot = card.querySelector(".chat-dock-head .watch-dock-state");
        states.push([dot.dataset.state, dot.style.getPropertyValue("--tone"), [...card.classList].filter((name) => name.startsWith("tone-"))]);
        app.unmount();
        app = null;
    }
    expect(states).toEqual([
        ["running", "var(--tone-work)", []],
        ["good", "var(--tone-good)", []],
        ["bad", "var(--tone-bad)", []],
    ]);
});

test("a docked test run shows how many passed and failed while it runs and keeps them at its end", async () => {
    const host = document.createElement("div");
    document.body.append(host);
    const running = {...watched, data: {...watched.data, count: "7 passed, 1 failed"}};
    app = createApp({render: () => h(WatchDock, {message: running})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-figure").textContent).toBe("7 passed, 1 failed");
    app.unmount();
    const ended = {...watched, data: {...watched.data, count: "15 passed, 1 failed", ending: "failed with code 1", tone: "bad"}};
    app = createApp({render: () => h(WatchDock, {message: ended})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-figure").textContent).toBe("15 passed, 1 failed");
    expect(host.querySelector(".watch-dock-ending").textContent).toBe("failed with code 1");
});
