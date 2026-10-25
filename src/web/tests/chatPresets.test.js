import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {
    allMarks,
    defaultHidden,
    groupSwitched,
    mainOnlyToggled,
    presetOf,
    presets,
    visibilityChoices,
    visibleIn,
} from "../src/domain/chatVisibility.js";
import {store} from "../src/state/store.js";

const marks = JSON.parse(readFileSync("tests/fixtures/markKinds.json", "utf8"));

test("Only chat hides every chat mark and keeps the messages, and Chat with context shows the marks as set by default", () => {
    store.spec = {...store.spec, marks};
    const only = presets().find((preset) => preset.key === "chat");
    const mark = {kind: "card", data: {shows: "commits"}};
    const message = {kind: "message", author: "agent", data: {}};
    expect(visibleIn(only.hidden)(mark)).toBe(false);
    expect(visibleIn(only.hidden)(message)).toBe(true);
    expect(presetOf(allMarks())).toBe("chat");
    expect(presetOf(defaultHidden())).toBe("context");
    expect(presetOf(["commits"]), "a hand-picked set is no preset").toBe("");
});

test("Show in chat offers the presets and opens the chat mark kinds as a submenu of their own", () => {
    const visible = readFileSync("src/panes/PaneMenuVisible.vue", "utf8");
    const markMenu = readFileSync("src/panes/PaneMenuMarks.vue", "utf8");
    const menu = readFileSync("src/panes/PaneMenu.vue", "utf8");
    expect(visible).toContain('v-for="choice in choices"');
    expect(visible).toContain('label="Chat marks"');
    expect(visible).not.toContain("group.kinds");
    expect(markMenu).toContain('v-for="kind in group.kinds"');
    expect(menu).toContain("<template #marks>");
    expect(menu).toContain(`@open="list = 'marks'"`);
});

test("the Chat marks menu lists every group and kind the registry serves, a switch per group, and a group's main marks alone on request", () => {
    store.spec = {...store.spec, marks};
    const choices = visibilityChoices(defaultHidden());
    expect(choices.map((group) => group.key)).toEqual(marks.groups.map((group) => group.key));
    expect(choices.flatMap((group) => group.kinds.map((kind) => kind.key)).sort()).toEqual(marks.kinds.map((kind) => kind.key).sort());
    expect(
        choices.flatMap((group) => group.kinds).find((kind) => kind.key === "reviewers").on,
        "a kind the registry adds is in the menu, shown"
    ).toBe(true);
    const journal = choices.find((group) => group.key === "journal");
    const off = groupSwitched([], {...journal, on: true});
    expect(
        marks.kinds.filter((kind) => kind.group === "journal").every((kind) => off.includes(kind.key)),
        "a group's switch hides all of it"
    ).toBe(true);
    expect(visibilityChoices(off).find((group) => group.key === "journal").on).toBe(false);
    const main = mainOnlyToggled(
        [],
        visibilityChoices([]).find((group) => group.key === "journal")
    );
    expect(main).toEqual(["sequence_steps"]);
    expect(visibilityChoices(main).find((group) => group.key === "journal").mainOnly).toBe(true);
});

test("a docked command card shows its title, progress and lines but no command line, which stays in its tooltip and in the card in the chat", () => {
    const dock = readFileSync("src/chat/WatchDock.vue", "utf8");
    const turn = readFileSync("src/chat/Turn.vue", "utf8");
    expect(dock).not.toContain('class="watch-dock-command"');
    expect(dock).toContain(':title="[card.line,');
    expect(turn).toContain('<p class="mark-command">{{ data.line }}</p>');
});

test("a bubble holds its React, Reply and Copy buttons, so they sit on its own corner however wide its turn is", () => {
    const message = readFileSync("src/chat/TurnMessage.vue", "utf8");
    const bubble = message.split('class="thread-bubble md"')[1].split("\n        </div>")[0];
    expect(bubble).toContain("<TurnActions");
    expect(message).toMatch(/\.thread-bubble \{\s*position: relative;/);
});
