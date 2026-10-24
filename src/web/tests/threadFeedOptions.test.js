import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {ui} from "../src/state/ui.js";

test("the chat's file edits pane keeps the view options the user picks, so lines and collapse apply there too", () => {
    const thread = readFileSync(resolve(__dirname, "../src/chat/Thread.vue"), "utf8");
    expect(thread).toMatch(/<FileFeed[^>]*:options="ui\.threadFeed"[^>]*@options="ui\.threadFeed = \$event"/);
    expect("threadFeed" in ui).toBe(true);
});

test("the status line above the compose box never goes: when the agent is not working it reads idle or waiting in its place, and it fades while the reader has scrolled up", () => {
    const thread = readFileSync(resolve(__dirname, "../src/chat/Thread.vue"), "utf8");
    const line = `<div :class="\\['thread-turn', 'busy', \\{faded: offFoot\\}\\]"`;
    expect(thread).toMatch(new RegExp(`<template v-if="busy && !waitingNow">\\s*${line}`));
    expect(thread).toMatch(new RegExp(`<template v-else>\\s*${line}[^>]*>[\\s\\S]*?@click="toggleWaiting">waiting<\\/button>[\\s\\S]*?<span>idle<\\/span>`));
    expect(thread).toMatch(/\.thread-turn\.busy\.faded \{[^}]*opacity: 0;/);
    const edge = readFileSync(resolve(__dirname, "../src/kit/WaitEdge.vue"), "utf8");
    expect(edge).not.toMatch(/Waiting\s*<WorkingDots/);
    expect(thread).not.toMatch(/<Transition name="status">/);
});

test("a suggestion's description reaches its card whole, however long", async () => {
    const {threadTurns} = await import("../src/domain/thread.js");
    const long =
        "This project installs Code Commandments v4.324.1 as a package, and the package runs its own hooks beside the journal's, so the same sins are raised twice and the chat fills up.";
    const {
        turns: [turn],
    } = threadTurns(
        [
            {
                id: 1,
                author: "system",
                text: "Run it as a journal plugin instead?",
                created_at: "2026-10-22T19:00:00Z",
                data: {kind: "suggestion", row: "suggestions:3", description: long, detail: "", accept: "Switch"},
            },
        ],
        []
    );
    expect(turn.suggestion.detail).toBe(long);
});

test("the chat opens the output dialog on the output it was asked for", () => {
    const thread = readFileSync(resolve(__dirname, "../src/chat/Thread.vue"), "utf8");
    expect(thread).toMatch(/<OutputDialog :key="outputOpen" :n="outputOpen"/);
});
