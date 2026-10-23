import {describe, expect, test} from "vitest";
import {conditionText, momentText} from "../src/domain/memoryTriggers.js";

describe("a fact, rule or reminder repeated on an event", () => {
    test("names its event and reads its condition in words", () => {
        expect(momentText("task_completed")).toBe("A task is completed");
        expect(conditionText({count: "tasks", where: {state: ["open", "started"]}, is: 0})).toBe("The number of tasks with state open or started is 0");
        expect(conditionText({any: [{count: "tasks", at_least: 3}, {count: "plans", where: {state: "started"}, at_most: 1}]})).toBe("The number of tasks is at least 3, or the number of plans with state started is at most 1");
        expect(conditionText({})).toBe("");
    });
});
