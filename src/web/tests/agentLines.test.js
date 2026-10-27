import {expect, test} from "vitest";
import {agentLines} from "../src/domain/agentLines.js";

test("the lines sent to an agent are its own, newest first, each with its time and words", () => {
    const entries = [
        {id: 3, data: {session: "s1", time: 30, line: "output 4: 40%"}},
        {id: 7, data: {session: "s2", time: 70, line: "a worker's line"}},
        {id: 9, data: {session: "s1", time: 90, line: "reply with [!reply:12]"}},
        {id: 5, data: {session: "s1", time: 50}},
    ];
    expect(agentLines(entries, "s1")).toEqual([
        {id: 9, time: 90, line: "reply with [!reply:12]"},
        {id: 3, time: 30, line: "output 4: 40%"},
    ]);
});
