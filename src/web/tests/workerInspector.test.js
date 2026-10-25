import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";
import {saidTurns} from "../src/domain/transcript.js";
import {workerActions, workerMoves, workerReusesLine, workerState} from "../src/domain/workers.js";
import {checkedCount, doneCount, pointRows} from "../src/domain/workerTurn.js";

globalThis.ResizeObserver = globalThis.ResizeObserver || class {
    observe() {}
    disconnect() {}
};
window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {default: WorkerPoints} = await import("../src/agents/WorkerPoints.vue");
const {default: WorkerTodos} = await import("../src/agents/WorkerTodos.vue");
const {default: WorkerPage} = await import("../src/resource/WorkerPage.vue");

let app = null;

afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
});

const task = {
    task_id: 7,
    points: ["reads the grammar", "names each rule", "passes its test", "has a page"],
    todos: [{text: "write the grammar", complete: true}, {text: "run it", complete: false}],
    proofs: [
        {point: 1, text: "parser.py:12", state: "checked", shortfall: ""},
        {point: 2, text: "parser.py:30", state: "shown", shortfall: ""},
        {point: 3, text: "tried by hand", state: "short", shortfall: "Prove it with a test."},
    ],
};
const worker = (state) => ({id: 3, name: "Lady Lovelace", state, brief: "Write the parser.", created_at: "2026-10-23T08:00:00Z", updated_at: "2026-10-23T08:30:00Z", task});

function mount(component, props, provides = {}) {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(component, props)});
    Object.entries(provides).forEach(([key, value]) => app.provide(key, value));
    app.mount(host);
    return host;
}

test("a worker's task reads as its points, each with its latest proof or none, and counts what is checked and done", () => {
    expect(pointRows(task).map((row) => [row.point, row.proof?.state || null])).toEqual([
        [1, "checked"],
        [2, "shown"],
        [3, "short"],
        [4, null],
    ]);
    expect([checkedCount(task), doneCount(task)]).toEqual([1, 1]);
});

test("the worker's states read as the page draws them, a clocked-out worker offering its merge", () => {
    expect(["clocked in", "clocked out", "ended without clocking out", "merged", "released"].map((state) => workerState({state}))).toEqual(["running", "ready", "unfinished", "finished", "finished"]);
    expect(workerActions({state: "clocked out"}).map((action) => action.key)).toEqual(["merge"]);
    expect(workerActions({state: "ended without clocking out"}).map((action) => action.key)).toEqual(["send", "release"]);
});

test("a worker's moves are the ones it made, the one it is at, and the ones still to come", () => {
    expect(workerMoves(worker("clocked in")).map((move) => [move.word, move.at])).toEqual([
        ["Dispatched", ""],
        ["Clocked in", "now"],
        ["Clocked out", "later"],
        ["Merged", "later"],
    ]);
    expect(workerMoves(worker("reported")).map((move) => move.word)).toEqual(["Dispatched", "Reported"]);
});

test("a worker sent back once shows every move of its current job with its time, the one it is at, and the merge still to come", () => {
    const at = (hour, minute) => new Date(2026, 9, 23, hour, minute).getTime() / 1000;
    const steps = [["dispatched", at(14, 2)], ["clocked in", at(14, 3)], ["clocked out", at(14, 51)], ["sent back", at(14, 58)], ["clocked in", at(14, 59)], ["clocked out", at(15, 24)]];
    const moves = workerMoves({...worker("clocked out"), moves: {steps}});
    expect(moves.map((move) => [move.word, move.at])).toEqual([
        ["Dispatched", ""],
        ["Clocked in", ""],
        ["Clocked out", ""],
        ["Sent back", ""],
        ["Clocked in", ""],
        ["Clocked out", "now"],
        ["Merged", "later"],
    ]);
    expect(moves.every((move) => move.at === "later" || /\d\d:\d\d/.test(move.time))).toBe(true);
    const reused = workerMoves({...worker("clocked in"), moves: {steps: [["dispatched", at(9, 0)], ["merged", at(10, 0)], ["sent a job", at(14, 2)], ["clocked in", at(14, 3)]]}});
    expect(reused.map((move) => move.word)).toEqual(["Sent a job", "Clocked in", "Clocked out", "Merged"]);
});

test("a worker's reuses count the new jobs it took, never a point sent back, and name the task it worked on before", () => {
    expect([workerReusesLine({reuse_count: 1, earlier_task: 1402}), workerReusesLine({reuse_count: 2}), workerReusesLine({reuse_count: 0})]).toEqual(["Reused once, on task 1402", "Reused twice", ""]);
    const resumed = {reuse_count: 2, earlier_task: 1402, moves: {steps: [["dispatched", 1], ["merged", 2], ["sent a job", 3], ["sent back", 4]]}};
    expect(workerReusesLine(resumed)).toBe("Reused once, on task 1402");
});

test("each point is a row with its proof, a sent-back point shows its reason, and a clocked-out worker's proved point offers check and send back", async () => {
    const api = {act: vi.fn(async () => ({}))};
    const host = mount(WorkerPoints, {task, worker: 3, api, checking: true});
    await flush();
    expect([...host.querySelectorAll(".word")].map((word) => word.textContent)).toEqual(["Checked", "Proved", "Sent back", "Unproved"]);
    expect(host.querySelector(".reason").textContent).toContain("Prove it with a test.");
    expect([...host.querySelectorAll("button")].map((button) => button.textContent.trim())).toEqual(["Check", "Send back"]);
    host.querySelector("button").click();
    await flush();
    expect(api.act).toHaveBeenCalledWith("workers", 3, "check", {point: 2});
});

test("a worker still at work has no check to offer, and its tasks mark what is done", async () => {
    const host = mount(WorkerPoints, {task, worker: 3, api: {act: vi.fn()}});
    await flush();
    expect(host.querySelectorAll("button").length).toBe(0);
    app.unmount();
    const list = mount(WorkerTodos, {todos: task.todos});
    expect([...list.querySelectorAll(".todo")].map((item) => [item.textContent.trim(), item.classList.contains("done")])).toEqual([["run it", false]]);
    list.querySelector(".more").click();
    await flush();
    expect([...list.querySelectorAll(".todo")].map((item) => [item.textContent.trim(), item.classList.contains("done")])).toEqual([
        ["run it", false],
        ["write the grammar", true],
    ]);
});

const turns = [
    {line: 1, kind: "human", time: 1, text: "Write the parser.", tools: []},
    {line: 2, kind: "agent", time: 2, text: "Reading the grammar first.", tools: ["Read", "Bash"], steps: [{kind: "file read", path: "grammar.txt", partial: false}, {kind: "shell line", command: "pytest -k parser"}]},
    {line: 3, kind: "tool", time: 3, text: "", tools: [], has_text: true},
    {line: 4, kind: "tool", time: 4, text: "", tools: [], has_text: true},
    {line: 5, kind: "agent", time: 5, text: "", tools: ["WebFetch"], steps: []},
];

test("a transcript reads as who said what, each with the steps it took in words and the line of each step's output", () => {
    const said = saidTurns(turns, {agent: "Lady Lovelace", human: "The agent"});
    expect(said.map((turn) => [turn.who, turn.text])).toEqual([
        ["The agent", "Write the parser."],
        ["Lady Lovelace", "Reading the grammar first."],
    ]);
    expect(said[1].steps.map((step) => [step.words, step.code, step.output])).toEqual([
        ["Read", "grammar.txt", 3],
        ["Ran", "pytest -k parser", 4],
        ["Used", "WebFetch", 0],
    ]);
});

test("the worker page shows its points, its readable transcript and its to-dos side by side, with no empty pane", async () => {
    const api = {env: () => "", act: vi.fn(), workerTranscript: vi.fn(async () => ({total: turns.length, first: 1, turns}))};
    const host = mount(WorkerPage, {resource: worker("clocked in")}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await new Promise((resolve) => setTimeout(resolve, 20));
    await flush();
    expect([...host.querySelectorAll(".head")].map((head) => head.firstChild.textContent.trim())).toEqual(["Points", "Transcript", "To-dos"]);
    expect(host.textContent).toContain("1 of 4 checked");
    expect(host.textContent).toContain("1 of 2 done");
    expect(host.querySelector(".tx").textContent).toContain("Show 3 steps");
    expect(host.querySelector(".quiet").textContent).toContain("Report not written yet");
    app.unmount();
    const branched = mount(WorkerPage, {resource: {...worker("clocked in"), worktree: true, branch: "worker/3-Lady-Lovelace", reuse_count: 1, earlier_task: 1402}}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    const facts = [...branched.querySelectorAll(".quiet > span")].map((fact) => fact.textContent.trim());
    expect(facts).toContain("Own worktree, branch worker/3-Lady-Lovelace");
    expect(facts).toContain("Reused once, on task 1402");
    app.unmount();
    const pooled = mount(WorkerPage, {resource: {...worker("clocked in"), pool_request: 7, device: "2"}}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    expect(pooled.querySelector(".quiet").textContent).toContain("Runs on machine 2, from request 7");
});

test("the facts are one plain line ending in Brief and Report, each opening its panel that Esc closes, and History lists the moves", async () => {
    const api = {env: () => "", act: vi.fn(), workerTranscript: vi.fn(async () => ({total: turns.length, first: 1, turns}))};
    const host = mount(WorkerPage, {resource: {...worker("clocked out"), report: "The parser is written."}}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    const words = [...host.querySelectorAll(".quiet > span")].map((fact) => fact.textContent.trim());
    expect(words.slice(-2)).toEqual(["Brief", "Report"]);
    host.querySelector('[data-open="brief"]').click();
    await flush();
    expect(document.body.querySelector(".inspector-pop").textContent).toContain("Write the parser.");
    window.dispatchEvent(new KeyboardEvent("keydown", {key: "Escape"}));
    await flush();
    expect(document.body.querySelector(".inspector-pop")).toBe(null);
    host.querySelector('[data-open="history"]').click();
    await flush();
    expect([...document.body.querySelectorAll(".inspector-pop .move")].map((move) => move.textContent.trim()).some((line) => line.includes("Dispatched"))).toBe(true);
});

test("each message folds its steps under a Show N steps link, and the to-do list shows what is left with the done behind a link", async () => {
    const api = {env: () => "", act: vi.fn(), workerTranscript: vi.fn(async () => ({total: turns.length, first: 1, turns}))};
    const host = mount(WorkerPage, {resource: worker("clocked in")}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await new Promise((resolve) => setTimeout(resolve, 20));
    await flush();
    const fold = [...host.querySelectorAll(".tx .fold")].find((button) => button.textContent.includes("Show 3 steps"));
    expect(host.querySelector(".tx .steps")).toBe(null);
    fold.click();
    await flush();
    expect(host.querySelector(".tx .steps").textContent).toContain("pytest -k parser");
    const todos = [...host.querySelectorAll(".todo")].map((todo) => todo.textContent.trim());
    expect(todos).toEqual(["run it"]);
    expect(host.textContent).toContain("Show the 1 done");
});

test("the worker inspector's columns are a pane grid whose dividers resize them, the sizes kept for the viewer", async () => {
    const {useWorkerLayout} = await import("../src/composables/paneLayout.js");
    const layout = useWorkerLayout();
    expect(layout.measured.value.splits.length).toBe(2);
    layout.resize("", 0.3);
    expect(layout.measured.value.splits[0].r).toBe(0.3);
    expect(JSON.parse(sessionStorage.getItem("journal.worker-layout")).tree.r).toBe(0.3);
});

test("the worker page names the task it works on above its name and the tasks queued for it at the top of its to-do list, in order", async () => {
    const api = {env: () => "", act: vi.fn(), workerTranscript: vi.fn(async () => ({total: 0, first: 1, turns: []}))};
    const queue = [{id: 8, title: "the docs"}, {id: 9, title: "the help page"}];
    const host = mount(WorkerPage, {resource: {...worker("clocked in"), queue}}, {scope: {env: "", api, rows: () => [{id: 7, title: "the parser"}], holding: async () => {}}});
    await flush();
    expect(host.querySelector(".stamp").textContent).toContain("Task 7: the parser");
    expect(host.querySelector("[data-worker-tasks]")).toBe(null);
    const queued = host.querySelector(".todos [data-worker-queue]");
    expect([...queued.querySelectorAll(".queued-task")].map((link) => link.textContent.trim())).toEqual(["Task 8: the docs", "Task 9: the help page"]);
});

test("a worker's queued tasks count as to-dos not yet done in the To-dos count, and stay listed under Queued next", async () => {
    const api = {env: () => "", act: vi.fn(), workerTranscript: vi.fn(async () => ({total: 0, first: 1, turns: []}))};
    const todos = [true, true, false, false].map((complete, n) => ({text: `item ${n}`, complete}));
    const queue = Array.from({length: 11}, (_, n) => ({id: 20 + n, title: `queued ${n}`}));
    const host = mount(WorkerPage, {resource: {...worker("clocked in"), task: {...task, todos}, queue}}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    expect(host.textContent).toContain("2 of 15 done");
    expect(host.querySelectorAll(".todos [data-worker-queue] .queued-task").length).toBe(11);
});

test("a worker with three queued tasks shows its report choice and its place in the queue in the worker list and the inspector", async () => {
    const {workerEntry} = await import("../src/domain/agentEntries.js");
    const api = {env: () => "", act: vi.fn(), workerTranscript: vi.fn(async () => ({total: 0, first: 1, turns: []}))};
    const queued = {...worker("clocked in"), report_choice: {tasks: 0}, holds: [8, 9], finished: [7], queue: [{id: 9, title: "c"}]};
    expect(workerEntry(queued).work).toBe("Task 2 of 3, reports when its queue is empty · Write the parser.");
    expect(workerEntry({...queued, report_choice: {tasks: 2}}).work).toContain("reports after every 2 tasks");
    const host = mount(WorkerPage, {resource: queued}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    expect([...host.querySelectorAll(".quiet > span")].map((fact) => fact.textContent.trim())).toContain("Task 2 of 3, reports when its queue is empty");
    app.unmount();
    const single = mount(WorkerPage, {resource: {...worker("clocked in"), report_choice: {tasks: 1}, holds: [7]}}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    expect([...single.querySelectorAll(".quiet > span")].map((fact) => fact.textContent.trim())).toContain("Reports after each task");
});
