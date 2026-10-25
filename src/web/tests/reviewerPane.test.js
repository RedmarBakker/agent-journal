import {createApp, h} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

globalThis.ResizeObserver = globalThis.ResizeObserver || class {
    observe() {}
    disconnect() {}
};
window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

vi.mock("../src/chat/Thread.vue", () => ({default: {setup: () => () => h("div", {class: "stub-thread"}, [h("textarea", {class: "stub-input"})])}}));
vi.mock("../src/chat/TerminalWindow.vue", () => ({default: {setup: () => () => h("div", {class: "stub-terminal"})}}));
vi.mock("../src/chat/FileFeed.vue", () => ({default: {setup: () => () => h("div", {class: "stub-feed"})}}));
vi.mock("../src/chat/AgentBar.vue", () => ({default: {setup: () => () => h("div", {class: "stub-bar"})}}));
vi.mock("../src/rail/RailWaiting.vue", () => ({default: {setup: () => () => h("div", {class: "stub-waiting"})}}));
vi.mock("../src/tasks/TasksTab.vue", () => ({default: {setup: () => () => h("div", {class: "stub-tasks"})}}));

const {api} = await import("../src/api/client.js");
const {choose} = await import("../src/state/environment.js");
const {store} = await import("../src/state/store.js");
const {default: Home} = await import("../src/pages/Home.vue");
choose("main");

const at = (minute) => `2026-10-25T09:${String(minute).padStart(2, "0")}:00Z`;
const step = (id, text, tone, minute) => ({table: "messages", id, author: "system", session: "r-1", agent_role: "reviewer", text, data: {kind: "review_step", tone}, created_at: at(minute), updated_at: at(minute)});
const STEPS = [
    step(14, "Handed its report on worker 2, Mr. Babbage, to the agent: 1 passed. 2 short: the alias names are missing", "", 9),
    step(11, "Started reviewing worker 2, Mr. Babbage", "", 2),
    step(13, "Point 1 passed", "good", 8),
    step(12, "Ran python3 -m pytest tests/test_parser.py: passed", "good", 5),
];
let app = null;

beforeEach(() => {
    sessionStorage.clear();
    location.hash = "#/";
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    store.summary = {environments: [{environment: {id: 1, name: "main"}, agent: null, task: null, questions: 0, messages: 0, tasks: 0, silent: false}]};
    vi.spyOn(api, "list").mockImplementation(async (table) => ({rows: table === "reviewers" ? [{table: "reviewers", id: 7, name: "Mr. Juran, keeper of the quality ledger", session: "r-1", state: "reviewed"}] : [], is_last_page: true, counts: {}}));
    vi.spyOn(api, "chat").mockImplementation(async (session) => ({rows: session === "r-1" ? STEPS : [], is_last_page: true, counts: {}}));
});

afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

function mount() {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(Home)});
    app.directive("tip", {});
    app.mount(host);
    return host;
}

const settled = async () => {
    await new Promise((done) => setTimeout(done, 80));
    for (let i = 0; i < 6; i++) await flush();
};

test("with the reviewer on, Home shows the reviewer pane beside the chat, with no input box and the review's steps oldest first", async () => {
    store.settings = {features: {}, viewer: {}, tasks: {auto: true}, workers: {mode: "orchestrator"}, reviewing: {reviewer: true}};
    const host = mount();
    await settled();
    const chat = host.querySelector(".home-view.chat");
    const reviewer = host.querySelector(".home-view.reviewer");
    expect(chat).not.toBe(null);
    expect(reviewer).not.toBe(null);
    expect(chat.closest(".pane-body")).not.toBe(reviewer.closest(".pane-body"));
    expect(reviewer.querySelector("textarea, input, [contenteditable]")).toBe(null);
    expect([...reviewer.querySelectorAll(".reviewer-step-text")].map((text) => text.textContent)).toEqual([
        "Started reviewing worker 2, Mr. Babbage",
        "Ran python3 -m pytest tests/test_parser.py: passed",
        "Point 1 passed",
        "Handed its report on worker 2, Mr. Babbage, to the agent: 1 passed. 2 short: the alias names are missing",
    ]);
    expect(api.chat).toHaveBeenCalledWith("r-1", {limit: 100});
});

test("with the reviewer off, Home shows no reviewer pane, and turning it off takes the pane away", async () => {
    store.settings = {features: {}, viewer: {}, tasks: {auto: true}, workers: {mode: "orchestrator"}, reviewing: {reviewer: true}};
    const host = mount();
    await settled();
    expect(host.querySelector(".home-view.reviewer")).not.toBe(null);
    store.settings = {...store.settings, reviewing: {reviewer: false}};
    await settled();
    expect(host.querySelector(".home-view.reviewer")).toBe(null);
    expect(host.querySelector(".home-view.chat")).not.toBe(null);
    app.unmount();
    app = null;
    document.body.innerHTML = "";
    store.settings = {features: {}, viewer: {}, tasks: {auto: true}, workers: {mode: "builder"}, reviewing: {reviewer: true}};
    const builder = mount();
    await settled();
    expect(builder.querySelector(".home-view.reviewer")).toBe(null);
});
