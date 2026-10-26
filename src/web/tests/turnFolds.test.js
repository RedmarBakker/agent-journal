import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {TURN_FOLDS, turnFold} from "../src/domain/turnFolds.js";

test("a worker's report folds after its first two lines, while the user's and the agent's messages keep their room", () => {
    const report = {who: "agent", text: "Hedy reports: done\nline\nline\nline", data: {kind: "report", worker: "Hedy"}};
    const said = {who: "agent", text: "a long answer", data: {}};
    const asked = {who: "user", text: "a long question", data: {}};
    expect(turnFold(report)).toBe(TURN_FOLDS.report);
    expect(TURN_FOLDS.report.keep).toBeLessThan(50);
    expect([turnFold(said), turnFold(asked)]).toEqual([TURN_FOLDS.message, TURN_FOLDS.message]);
    const message = readFileSync(resolve(__dirname, "../src/chat/TurnMessage.vue"), "utf8");
    expect(message).toMatch(/:fold-at="fold\.at" :keep="fold\.keep"/);
});

test("a process card that ends keeps its index in the thread, between the messages that were written around it", async () => {
    const {threadTurns} = await import("../src/domain/thread.js");
    const at = (n) => new Date(n * 1000).toISOString();
    const say = (id, n) => ({table: "messages", id, created_at: at(n), creator: "user", author: "user", agent_role: "main", text: `message ${id}`, files: [], comments_on: [], idempotency: "", data: {}});
    const card = (active, updated) => ({table: "messages", id: 2, created_at: at(20), updated_at: at(updated), creator: "system", author: "system", agent_role: "main", text: "Building the viewer", files: [], comments_on: [], idempotency: "", data: {kind: "card", key: "watch:7", output: 7, active, docked: false}});
    const index = (turns) => turns.findIndex((turn) => turn.text === "Building the viewer");
    const running = threadTurns([say(1, 10), card(true, 20), say(3, 30)], []).turns;
    const ended = threadTurns([say(1, 10), card(false, 99), say(3, 30)], []).turns;
    expect(index(running)).toBe(1);
    expect(index(ended)).toBe(1);
});
