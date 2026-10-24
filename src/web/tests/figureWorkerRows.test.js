import {expect, test} from "vitest";
import {facesAfter, readingsAfter, sayingsAfter, testResultsAfter, withSystemCards, writtenFacesAfter} from "../src/domain/figureState.js";

const at = (seconds) => new Date(seconds * 1000).toISOString();
const row = (id, role, fields = {}) => ({table: "messages", id, agent_role: role, session: role === "main" ? "s1" : `w${id}`, created_at: at(100 + id), read_at: null, text: "", data: {}, ...fields});
const run = (id, role, ending) =>
    row(id, role, {author: "system", text: "Running tests", data: {kind: "card", icon: "agents", tone: ending === "failed" ? "bad" : "good", is_test: true, output: 1, figure: "", ending}});

const lead = (messages) => withSystemCards({session: "s1", data: {}}, messages);

test("a worker's failed test run is not the main agent's: only the main agent's own run moves its avatar", () => {
    const messages = [run(1, "main", "failed"), run(2, "worker", "failed"), run(3, "subagent", "failed")];
    const beats = testResultsAfter(lead(messages), new Map(), 0);
    expect(beats.map((beat) => [beat.beat, beat.card])).toEqual([["tests_failed", "messages:1"]]);
});

test("a worker's or a subagent's report and written face leave the main agent's avatar still, and its own are heard", () => {
    const report = (id, role) => row(id, role, {author: "agent", data: {kind: "report"}});
    const said = (id, role) => row(id, role, {author: "agent", text: "that was a 😅"});
    const messages = [report(1, "main"), report(2, "worker"), report(3, "subagent"), said(4, "main"), said(5, "worker")];
    expect(sayingsAfter({session: "s1"}, messages, 0).map((beat) => beat.card)).toEqual(["messages:1"]);
    expect(writtenFacesAfter({session: "s1"}, messages, 0).map((beat) => beat.card)).toEqual(["messages:4"]);
});

test("a message a worker's user read and a face put on a worker's message do not move the main agent's avatar", () => {
    const read = (id, role) => row(id, role, {author: "user", read_at: at(500)});
    expect(readingsAfter([read(1, "main"), read(2, "worker")], 0).map((beat) => beat.card)).toEqual(["messages:1"]);
    const messages = [row(1, "main"), row(2, "worker")];
    const faces = [{message_id: 1, author: "user", emoji: "👍", created_at: at(500)}, {message_id: 2, author: "user", emoji: "👍", created_at: at(500)}];
    expect(facesAfter(faces, 0, messages).map((beat) => beat.card)).toEqual(["messages:1"]);
});
