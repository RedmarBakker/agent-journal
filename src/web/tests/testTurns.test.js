import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

const {api} = await import("../src/api/client.js");
const {store} = await import("../src/state/store.js");
const {choose} = await import("../src/state/environment.js");
const {default: WorkerList} = await import("../src/chat/WorkerList.vue");
choose("main");

const now = Date.now() / 1000;
const at = (secondsAgo) => new Date((now - secondsAgo) * 1000).toISOString();
const workers = [
    {table: "workers", id: 3, name: "Lady Lovelace", state: "clocked in", created_at: at(3600), updated_at: at(60)},
    {table: "workers", id: 4, name: "Mr. Babbage", state: "clocked in", created_at: at(3600), updated_at: at(60)},
    {table: "workers", id: 5, name: "Miss Hopper", state: "clocked in", created_at: at(3600), updated_at: at(60)},
];
const turns = [
    {table: "test_turns", id: 9, worker: 5, ids: "tests/test_c.py::test_three", state: "waiting", started_at: 0, created_at: at(120), updated_at: at(120)},
    {table: "test_turns", id: 7, worker: 3, ids: "tests/test_a.py::test_one", state: "running", started_at: now - 300, created_at: at(400), updated_at: at(300)},
    {table: "test_turns", id: 8, worker: 4, ids: "tests/test_b.py::test_two tests/test_b.py::test_more", state: "running", started_at: now - 90, created_at: at(200), updated_at: at(90)},
];
let app = null;

afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("with the test budget on, the workers panel lists the turns going, then those waiting, each with its worker, its test ids and how long it has run or waited, and the budget's numbers", async () => {
    store.settings = {features: {}, workers: {testing: "Test budget", test_runs: 2, test_waiting: "4", tests_per_run: 20, test_run_minutes: 10}};
    vi.spyOn(api, "list").mockImplementation(async (table) => ({rows: table === "test_turns" ? turns : [], is_last_page: true, counts: {}}));
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(WorkerList, {rows: workers})});
    app.directive("tip", {});
    app.mount(host);
    for (let i = 0; i < 4; i++) await flush();
    expect(api.list).toHaveBeenCalledWith("test_turns", expect.objectContaining({limit: expect.any(Number)}));
    const rows = [...host.querySelectorAll(".test-turn")].map((row) => [row.querySelector(".test-turn-worker").textContent, row.querySelector(".test-turn-ids").textContent, row.querySelector(".test-turn-time").textContent]);
    expect(rows).toEqual([
        ["Lady Lovelace", "tests/test_a.py::test_one", "running 5m"],
        ["Mr. Babbage", "tests/test_b.py::test_two tests/test_b.py::test_more", "running 1m"],
        ["Miss Hopper", "tests/test_c.py::test_three", "waiting 2m"],
    ]);
    expect([...host.querySelectorAll(".test-turn")].map((row) => row.classList.contains("running"))).toEqual([true, true, false]);
    expect(host.querySelector(".test-turns-budget").textContent).toBe("2 runs at once · 4 may wait · 20 test ids a run · 10 minutes a run");
});

test("with another way of testing, the workers panel shows no test turns", async () => {
    store.settings = {features: {}, workers: {testing: "Hand the tests over"}};
    vi.spyOn(api, "list").mockImplementation(async () => ({rows: [], is_last_page: true, counts: {}}));
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(WorkerList, {rows: workers})});
    app.directive("tip", {});
    app.mount(host);
    for (let i = 0; i < 4; i++) await flush();
    expect(host.querySelector(".test-turns")).toBe(null);
});
