import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

vi.mock("../src/route.js", async (original) => ({...(await original()), peek: vi.fn()}));

const {default: Turn} = await import("../src/chat/Turn.vue");
const {threadTurns} = await import("../src/domain/thread.js");
const {peek} = await import("../src/route.js");

let app = null;
afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

const REASON = "the journal says worker 1142 holds no task";
const stopped = {
    table: "messages",
    id: 9,
    created_at: new Date(1e4).toISOString(),
    author: "system",
    text: "Worker 1142, Mr Gutenberg: stopped before it finished",
    files: [],
    comments_on: [],
    data: {kind: "card", outcome: "failed", row: "workers:1142", detail: REASON, reason: REASON},
};

test("a worker that stopped early opens in place to why it stopped, and its act still opens the worker", async () => {
    const scope = {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}};
    const turn = threadTurns([stopped], []).turns[0];
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(Turn, {turn})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".mark-label")).toBeNull();
    host.querySelector(".top").click();
    await flush();
    expect(host.querySelector(".mark").classList.contains("open")).toBe(true);
    expect(host.querySelector(".mark-label").textContent).toBe("Why it stopped");
    expect(host.querySelector(".mark-summary").textContent).toBe(REASON);
    expect(host.querySelector(".mact").getAttribute("aria-label")).toBe("Open the worker");
    host.querySelector(".mact").click();
    await flush();
    expect(host.querySelector(".mark").classList.contains("open")).toBe(true);
    expect(peek).toHaveBeenCalledWith("workers", 1142, 0);
});
