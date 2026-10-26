import {expect, test} from "vitest";
import {leadOf} from "../src/domain/agents.js";

test("the lead agent is the environment's main agent, never a worker heard from later", () => {
    const main = {id: 39, role: "main", status: "idle", heard_at: "2026-10-22T20:00:00Z"};
    const worker = {id: 43, role: "worker", status: "working", heard_at: "2026-10-22T20:05:00Z"};
    expect(leadOf([main, worker]).id).toBe(39);
    expect(leadOf([worker])).toBe(null);
});

test("a subagent, a reviewer or a verifier heard from later never takes the lead, so the Home's edits stay on the main agent", () => {
    const main = {id: 39, role: "main", status: "working", heard_at: "2026-10-22T20:00:00Z"};
    const helpers = ["subagent", "reviewer", "verifier"].map((role, i) => ({id: 50 + i, role, status: "working", heard_at: `2026-10-22T20:0${i + 1}:00Z`}));
    expect(leadOf([main, ...helpers]).id).toBe(39);
    expect(leadOf([...helpers, main]).id).toBe(39);
});
