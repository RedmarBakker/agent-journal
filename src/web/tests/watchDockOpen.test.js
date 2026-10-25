import {readFileSync} from "node:fs";
import {createApp, h, ref} from "vue";
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

test("a docked output is titled in words, keeps its command in its tooltip, not beneath, and opens on a click to its whole output in a box that scrolls", async () => {
    const read = vi.spyOn(api, "readOutput").mockResolvedValue({command: "pytest -q", outcome: "running", lines: ["collecting", "FAILED test_b", "[ 40%] test_c"], start: 0, next: 3});
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(WatchDock, {message: watched})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-label").textContent.trim()).toBe("Running the tests");
    expect(host.querySelector(".watch-dock-command")).toBe(null);
    expect(host.querySelector(".watch-dock-output")).toBeNull();
    host.querySelector(".watch-dock-label").click();
    await flush();
    expect(read).toHaveBeenCalledWith(12);
    expect(host.querySelector(".watch-dock-more").classList.contains("open")).toBe(true);
    expect(host.querySelector(".watch-dock-output").textContent).toBe("collecting\nFAILED test_b\n[ 40%] test_c");
    host.querySelector(".watch-dock-label").click();
    await flush();
    expect(host.querySelector(".watch-dock-more").classList.contains("open")).toBe(false);
});

test("an open dock asks for the lines after the last it holds, and adds them to its output", async () => {
    const read = vi.spyOn(api, "readOutput").mockResolvedValueOnce({lines: ["collecting", "FAILED test_b"], start: 0, next: 2}).mockResolvedValueOnce({lines: ["[ 40%] test_c"], start: 2, next: 3});
    const host = document.createElement("div");
    document.body.append(host);
    const message = ref(watched);
    app = createApp({render: () => h(WatchDock, {message: message.value})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    host.querySelector(".watch-dock-label").click();
    await flush();
    expect(read).toHaveBeenLastCalledWith(12);
    message.value = {...watched, data: {...watched.data, lines: ["[ 40%] test_c"]}};
    await flush();
    expect(read).toHaveBeenLastCalledWith(12, {after: 2});
    expect(host.querySelector(".watch-dock-output").textContent).toBe("collecting\nFAILED test_b\n[ 40%] test_c");
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

test("a run shows no bar before it has progress, and its bar lies along the card's foot without adding height, so the card never grows when it comes", async () => {
    const host = document.createElement("div");
    document.body.append(host);
    const early = {...watched, data: {...watched.data, figure: "", count: "", fraction: 0, counting: true}};
    app = createApp({render: () => h(WatchDock, {message: early})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-bar")).toBeNull();
    app.unmount();
    const going = {...watched, data: {...watched.data, figure: "40%", fraction: 0.4, counting: true}};
    app = createApp({render: () => h(WatchDock, {message: going})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-fill").style.width).toBe("40%");
    const dock = readFileSync("src/chat/WatchDock.vue", "utf8");
    expect(dock).toMatch(/\.watch-dock-bar \{\s*position: absolute;/);
});

test("a chat mark of a counting run draws its empty bar before any progress", async () => {
    const {default: ChatMark} = await import("../src/kit/ChatMark.vue");
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(ChatMark, {mark: {label: "Running tests", counting: true, fraction: 0}})});
    app.mount(host);
    await flush();
    expect(host.querySelector(".progress")).not.toBeNull();
});

test("a docked card of a running command counts its run up each second from its start time without a request, and shows the total once it ends", async () => {
    vi.useFakeTimers({toFake: ["setInterval", "clearInterval", "Date"]});
    vi.setSystemTime(new Date(1000 * 1000));
    const read = vi.spyOn(api, "readOutput");
    const host = document.createElement("div");
    document.body.append(host);
    const message = ref({...watched, data: {...watched.data, began_at: 1000 - 84}});
    app = createApp({render: () => h(WatchDock, {message: message.value})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-timer").textContent).toBe("1m 24s");
    vi.advanceTimersByTime(3000);
    await flush();
    expect(host.querySelector(".watch-dock-timer").textContent).toBe("1m 27s");
    message.value = {...watched, data: {...watched.data, began_at: 1000 - 84, ended_at: 1000 + 10}};
    await flush();
    vi.advanceTimersByTime(5000);
    await flush();
    expect(host.querySelector(".watch-dock-timer").textContent).toBe("1m 34s");
    expect(read).not.toHaveBeenCalled();
    vi.useRealTimers();
});

test("a docked run that failed shows red by the outcome its card reports, never the green of a card with no tone", async () => {
    const failed = {...watched, data: {...watched.data, ending: "failed with code 1", outcome: "failed", tone: undefined}};
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(WatchDock, {message: failed})});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-state").dataset.state).toBe("bad");
});

test("the run's duration is the last detail of a docked card's head, after its figure and its ending", async () => {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(WatchDock, {message: {...watched, data: {...watched.data, count: "3 of 9", ending: "Passed", began_at: 1, ended_at: 5}}})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    const order = [...host.querySelectorAll(".watch-dock-figure, .watch-dock-ending")].map((el) => el.textContent.trim());
    expect(order).toEqual(["3 of 9", "Passed", "4s"]);
});
