import {expect, test} from "vitest";
import {actsOf} from "../src/domain/acts.js";

const approves = (state) => actsOf({table: "plans", id: 1, state}).some((act) => act.name === "approve");

test("a plan is offered Approve only once it is ready, never while it is still being planned or reviewed", () => {
    expect(approves("ready")).toBe(true);
    expect(approves("draft")).toBe(false);
    expect(approves("reviewing")).toBe(false);
    expect(approves("approved")).toBe(false);
});
