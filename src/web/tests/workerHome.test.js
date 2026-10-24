import {createApp, h, inject} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

globalThis.ResizeObserver = globalThis.ResizeObserver || class {
    observe() {}
    disconnect() {}
};
window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

vi.mock("../src/chat/Thread.vue", () => ({
    default: {
        setup() {
            const scope = inject("scope");
            return () => h("div", {class: "stub-thread"}, [h("button", {class: "stub-send", onClick: () => scope.chat.send("mind the tests")}), String(scope.chat.session)]);
        },
    },
}));
vi.mock("../src/chat/TerminalWindow.vue", () => ({default: {props: ["agent", "level"], setup: (props) => () => h("div", {class: "stub-terminal"}, `terminal of agent ${props.agent.id}`)}}));
vi.mock("../src/chat/FileFeed.vue", () => ({default: {props: ["agent", "flush", "options", "defaults"], setup: (props) => () => h("div", {class: "stub-feed"}, `edits of agent ${props.agent}`)}}));
vi.mock("../src/resource/TranscriptLog.vue", () => ({default: {props: ["transcript", "entries", "env"], setup: () => () => h("div", {class: "stub-transcript"})}}));

const {api} = await import("../src/api/client.js");
const {choose} = await import("../src/state/environment.js");
const {store} = await import("../src/state/store.js");
const {default: WorkerHome} = await import("../src/pages/WorkerHome.vue");
const {default: WorkerPage} = await import("../src/resource/WorkerPage.vue");
choose("main");

const worker = {id: 3, name: "Lady Lovelace", state: "clocked in", session: "w-3", agent: 9, brief: "Write the parser.", created_at: "2026-10-23T08:00:00Z", updated_at: "2026-10-23T08:30:00Z", task: {task_id: null, points: [], todos: [], proofs: []}};
const agent = {table: "agents", id: 9, session: "w-3", role: "worker", status: "working", data: {}, updated_at: "2026-10-23T08:30:00Z", created_at: "2026-10-23T08:00:00Z"};
let app = null;

beforeEach(() => {
    sessionStorage.clear();
    location.hash = "#/worker/3";
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    vi.spyOn(api, "list").mockImplementation(async (table) => ({rows: table === "workers" ? [{table: "workers", ...worker}] : table === "agents" ? [agent] : [], is_last_page: true, counts: {}}));
    vi.spyOn(api, "chat").mockResolvedValue({rows: [], is_last_page: true, counts: {}});
    vi.spyOn(api, "workerTranscript").mockResolvedValue({turns: [], total: 0, first: 0});
});

afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

function mount(component, props = {}) {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(component, props)});
    app.directive("tip", {});
    app.mount(host);
    return host;
}

const settled = async () => {
    for (let i = 0; i < 6; i++) await flush();
};

test("a worker's home view has its chat, whose write box sends to the worker, its terminal and its feed, and a way back to the inspector", async () => {
    const act = vi.spyOn(api, "act").mockResolvedValue({});
    store.settings = store.settings || {viewer: {}};
    const host = mount(WorkerHome);
    await settled();
    expect(host.textContent).toContain("Worker 3, ");
    expect(host.querySelector(".stub-thread").textContent).toContain("w-3");
    expect(host.querySelector(".stub-terminal").textContent).toBe("terminal of agent 9");
    host.querySelector(".stub-send").click();
    await settled();
    expect(act).toHaveBeenCalledWith("workers", 3, "message", {text: "mind the tests"});
    host.querySelector('[data-tab="feed"]').dispatchEvent(new PointerEvent("pointerdown", {bubbles: true, button: 0}));
    window.dispatchEvent(new PointerEvent("pointerup"));
    await settled();
    expect(host.querySelector(".stub-feed").textContent).toBe("edits of agent 9");
    const back = [...host.querySelectorAll("button")].find((b) => b.textContent.includes("Back to the inspector"));
    back.click();
    expect(location.hash).toBe("#/home?open=workers:3");
});

test("the layout is kept for each worker on its own and a preset changes it", async () => {
    store.settings = store.settings || {viewer: {}};
    const host = mount(WorkerHome);
    await settled();
    const layout = () => JSON.parse(sessionStorage.getItem("journal.worker-home-layout.3"));
    expect(sessionStorage.getItem("journal.worker-home-layout.3")).toBeNull();
    [...host.querySelectorAll("button")].find((b) => b.textContent.includes("Change layout")).click();
    await settled();
    [...document.body.querySelectorAll("button, li, [role]")].find((e) => e.textContent.trim().startsWith("Chat only")).click();
    await settled();
    expect(layout().tree.dir).toBeUndefined();
    expect(sessionStorage.getItem("journal.worker-home-layout.4")).toBeNull();
});

test("the worker's inspector offers its home view", async () => {
    const host = mount(WorkerPage, {resource: worker});
    await settled();
    const open = [...host.querySelectorAll("button")].find((b) => b.textContent.includes("Open its home view"));
    expect(open).toBeTruthy();
    open.click();
    expect(location.hash).toBe("#/worker/3");
});
