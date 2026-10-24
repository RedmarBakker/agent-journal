import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";
import {saidTurns} from "../src/domain/transcript.js";
import {workerActions, workerMoves, workerReusesLine, workerState} from "../src/domain/workers.js";
import {checkedCount, doneCount, pointRows} from "../src/domain/workerShift.js";

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
    expect([workerReusesLine({reuse_count: 1, earlier_task: 1402}), workerReusesLine({reuse_count: 2}), workerReusesLine({reuse_count: 0})]).toEqual(["1, on task 1402", "2", ""]);
    const resumed = {reuse_count: 2, earlier_task: 1402, moves: {steps: [["dispatched", 1], ["merged", 2], ["sent a job", 3], ["sent back", 4]]}};
    expect(workerReusesLine(resumed)).toBe("1, on task 1402");
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
    expect([...list.querySelectorAll(".todo")].map((item) => [item.textContent.trim(), item.classList.contains("done")])).toEqual([
        ["write the grammar", true],
        ["run it", false],
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
    expect(host.querySelector(".tx").textContent).toContain("pytest -k parser");
    expect(host.textContent).toContain("Not written yet.");
    app.unmount();
    const branched = mount(WorkerPage, {resource: {...worker("clocked in"), branch: "worker/3-Lady-Lovelace", reuse_count: 1, earlier_task: 1402}}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    const facts = Object.fromEntries([...branched.querySelectorAll(".fact")].map((fact) => [fact.querySelector(".label").textContent, fact.querySelector(".value").textContent.trim()]));
    expect([facts.Branch, facts.Reuses]).toEqual(["worker/3-Lady-Lovelace", "1, on task 1402"]);
    app.unmount();
    const pooled = mount(WorkerPage, {resource: {...worker("clocked in"), pool_request: 7, device: "2"}}, {scope: {env: "", api, rows: () => [], holding: async () => {}}});
    await flush();
    const pool = [...pooled.querySelectorAll(".fact")].find((fact) => fact.querySelector(".label").textContent === "Team's pool");
    expect(pool.querySelector(".value").textContent.trim()).toBe("Runs on machine 2, from request 7");
});

test("the worker page names the task it works on and the tasks queued for it, in order, so what was delegated shows", async () => {
    const api = {env: () => "", act: vi.fn(), workerTranscript: vi.fn(async () => ({total: 0, first: 1, turns: []}))};
    const queue = [{id: 8, title: "the docs"}, {id: 9, title: "the help page"}];
    const host = mount(WorkerPage, {resource: {...worker("clocked in"), queue}}, {scope: {env: "", api, rows: () => [{id: 7, title: "the parser"}], holding: async () => {}}});
    await flush();
    const tasks = host.querySelector("[data-worker-tasks]");
    expect(tasks.textContent).toContain("Working on");
    expect(tasks.textContent).toContain("Task 7: the parser");
    expect([...tasks.querySelectorAll(".delegated-queue .task-link")].map((link) => link.textContent.trim())).toEqual(["Task 8: the docs", "Task 9: the help page"]);
});
