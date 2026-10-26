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

test("an agent that awaits something shows waiting again once its command has ended for the timeout", async () => {
    const {WAITING_AGAIN_AFTER} = await import("../src/domain/agentState.js");
    const heard = 1000;
    const idle = {status: "idle", awaiting: "worker 3", heard_at: heard};
    expect(stateOf(idle, heard + 100)).toBe("waiting");
    const running = {...idle, status: "working", tool_running: true};
    expect(stateOf(running, heard + 100)).toBe("working");
    const ended = {...idle, status: "working", tool_running: false};
    expect(stateOf(ended, heard + WAITING_AGAIN_AFTER - 1)).toBe("working");
    expect(stateOf(ended, heard + WAITING_AGAIN_AFTER)).toBe("waiting");
    expect(stateOf({...ended, awaiting: ""}, heard + 100)).toBe("working");
});
