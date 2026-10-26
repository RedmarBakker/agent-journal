import {describe, expect, test} from "vitest";
import {workerActivity} from "../src/domain/workers.js";

const worker = (more = {}) => ({id: 3, state: "clocked in", queue: [], runs: [], merging: false, ...more});

describe("what a worker is doing now, in plain words", () => {
    test("says the step its agent is on, or that its tests run", () => {
        expect(workerActivity(worker(), {tool_running: true, doing: "editing src/cart.py"})).toBe("Working: editing src/cart.py");
        expect(workerActivity(worker(), null)).toBe("Working on its task");
        expect(workerActivity(worker({runs: ["testing"]}), {tool_running: false})).toBe("Running its tests");
    });

    test("says it is clocked out for the check, being merged, idle with its queue, or waiting", () => {
        expect(workerActivity(worker({state: "clocked out"}))).toBe("Clocked out, waiting for its work to be checked");
        expect(workerActivity(worker({state: "clocked out", merging: true}))).toBe("Its work is being merged");
        expect(workerActivity(worker({state: "reported", queue: [{id: 7, title: "the parser"}, {id: 8, title: "the docs"}]}))).toBe("Idle, 2 tasks queued");
        expect(workerActivity(worker({state: "reported"}))).toBe("Idle, waiting for a job");
        expect(workerActivity(worker({state: "waiting for the usage limit"}))).toBe("Waiting for the usage limit");
        expect(workerActivity(worker({state: "dispatched", pool_request: 12, device: ""}))).toBe("Waiting for a machine to take it");
    });

    test("says how a closed one ended", () => {
        expect(workerActivity(worker({state: "stopped"}))).toBe("Stopped");
        expect(workerActivity(worker({state: "merged"}))).toBe("Merged");
    });
});
