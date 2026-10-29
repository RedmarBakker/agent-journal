import {expect, test} from "vitest";
import {threadTurns} from "../src/domain/thread.js";

const searched = (count) => ({
    table: "messages",
    id: 1,
    created_at: new Date(1e4).toISOString(),
    creator: "system",
    author: "system",
    text: `Searched for "base", ${count} results`,
    files: [],
    comments_on: [],
    idempotency: "",
    data: {kind: "search", shows: "searches", terms: "base", row: "", results: Array.from({length: count}, (_, i) => ({row: `tasks:${i + 1}`, label: `task ${i + 1}`, passage: "the base repository"}))},
});

test("a search mark is one group headed with its words and count, a child per result opening its row", () => {
    const [group] = threadTurns([searched(2)], []).turns;
    expect(group.kind).toBe("group");
    expect(group.title).toBe('Searched for "base", 2 results');
    expect(group.turns.map((t) => [t.data.label, t.data.row])).toEqual([
        ["task 1", "tasks:1"],
        ["task 2", "tasks:2"],
    ]);
});

test("past ten results the last child says how many more and opens the search page with the words", () => {
    const [group] = threadTurns([searched(14)], []).turns;
    expect(group.turns).toHaveLength(11);
    expect(group.turns[10].data).toMatchObject({label: "+ 4 more", go: "search", query: "base"});
});

test("a search that found nothing is a plain mark with no children", () => {
    const [mark] = threadTurns([searched(0)], []).turns;
    expect(mark.kind).toBe("card");
});
