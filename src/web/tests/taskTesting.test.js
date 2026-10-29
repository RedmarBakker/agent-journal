import {expect, test} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {STATUS_ORDER, statusOf} = await import("../src/domain/taskBoard.js");
const {GROUPS} = await import("../src/domain/records.js");

test("a task waiting in testing is grouped as Testing, right after the tasks in progress", () => {
    expect(statusOf({table: "tasks", id: 3, state: "testing"})).toBe("testing");
    expect(GROUPS.testing).toBe("Testing");
    expect(STATUS_ORDER.slice(0, 2)).toEqual(["started", "testing"]);
});
