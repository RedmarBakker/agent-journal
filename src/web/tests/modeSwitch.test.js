import {describe, expect, it} from "vitest";
import {switchQuestion} from "../src/domain/modes.js";

describe("a mode switch", () => {
    it("switches at once while the agent is idle", () => {
        expect(switchQuestion("orchestrator", {task: null, workersOut: 0, state: "idle"})).toBe("");
    });

    it("asks first while the agent works", () => {
        expect(switchQuestion("orchestrator", {task: {id: 12}, workersOut: 0, state: "working"})).toBe("Switch to Orchestrator? The agent is working on task 12.");
        expect(switchQuestion("solo", {task: null, workersOut: 2, state: "idle"})).toBe("Switch to Solo? The agent has 2 workers out.");
        expect(switchQuestion("builder", {task: null, workersOut: 0, state: "working"})).toBe("Switch to Builder? The agent is in the middle of a turn.");
    });
});
