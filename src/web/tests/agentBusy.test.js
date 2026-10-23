import {expect, test} from "vitest";
import {isBusy, stateOf} from "../src/domain/agentState.js";

test("the chat's activity line and the top bar read busy from one place, a state of the agent's own included", () => {
    const orienting = {status: "getting oriented", state: "working"};
    expect(stateOf(orienting)).toBe("busy");
    expect(isBusy(orienting)).toBe(true);
    expect(isBusy({status: "working"})).toBe(true);
    expect(isBusy({status: "compacting"})).toBe(true);
    expect(isBusy({status: "idle"})).toBe(false);
    expect(isBusy({status: "stopped"})).toBe(false);
    expect(isBusy(null)).toBe(false);
});
