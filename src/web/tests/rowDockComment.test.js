import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

test("a docked row that takes comments is commented on from its card, the composer naming the row and sending under it unquoted", () => {
    const dock = readFileSync("src/chat/RowDock.vue", "utf8");
    const thread = readFileSync("src/chat/Thread.vue", "utf8");
    expect(dock).toContain('const comment = () => (store.quoting = {text: card.value.heading, ref: "", on: `${row.value.table}:${row.value.id}`, label: "Commenting on"});');
    expect(dock).toContain('<template v-if="commentable">');
    expect(thread).toContain("const body = replying.on ? text : withQuote(replying.text, text);");
    expect(thread).toContain("refers: replying.refers, on: replying.on}");
});

test("a docked row's own acts show only while the row as it is now offers them, so an approved plan's card shows no Approve", () => {
    const dock = readFileSync("src/chat/RowDock.vue", "utf8");
    expect(dock).toContain("(b) => b.act !== \"close\" && (!rowAct(b) || !offered.value || offered.value.has(b.act))");
});
