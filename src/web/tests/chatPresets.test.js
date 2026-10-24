import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {ALL_MARKS, DEFAULT_HIDDEN, PRESETS, presetOf, visibleIn} from "../src/domain/chatVisibility.js";

test("Only chat hides every chat mark and keeps the messages, and Chat with context shows the marks as set by default", () => {
    const only = PRESETS.find((preset) => preset.key === "chat");
    const mark = {kind: "card", data: {shows: "commits"}};
    const message = {kind: "message", author: "agent", data: {}};
    expect(visibleIn(only.hidden)(mark)).toBe(false);
    expect(visibleIn(only.hidden)(message)).toBe(true);
    expect(presetOf(ALL_MARKS)).toBe("chat");
    expect(presetOf(DEFAULT_HIDDEN)).toBe("context");
    expect(presetOf(["commits"]), "a hand-picked set is no preset").toBe("");
});

test("Show in chat offers the presets and opens the chat mark kinds as a submenu of their own", () => {
    const visible = readFileSync("src/panes/PaneMenuVisible.vue", "utf8");
    const marks = readFileSync("src/panes/PaneMenuMarks.vue", "utf8");
    const menu = readFileSync("src/panes/PaneMenu.vue", "utf8");
    expect(visible).toContain('v-for="choice in PRESETS"');
    expect(visible).toContain('label="Chat marks"');
    expect(visible).not.toContain("group.kinds");
    expect(marks).toContain('v-for="kind in group.kinds"');
    expect(menu).toContain("<template #marks>");
    expect(menu).toContain(`@open="list = 'marks'"`);
});
