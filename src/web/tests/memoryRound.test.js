import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const {choose} = await import("../src/state/environment.js");
const {default: Turn} = await import("../src/chat/Turn.vue");
const {threadTurns} = await import("../src/domain/thread.js");

choose("main");
let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

const scope = {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}};

// a memories mark as the journal writes it at a compaction, with the round it faded or without one
const faded = (round) => ({
    table: "messages",
    id: 9,
    created_at: new Date(1e4).toISOString(),
    author: "system",
    text: "Memories faded by one: 1 of 2 still shown",
    files: [],
    comments_on: [],
    data: {kind: "card", detail: "", row: "", shows: "memories", ...(round ? {round} : {})},
});

async function opened(message) {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(Turn, {turn: threadTurns([message], []).turns[0]})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    host.querySelector(".mark").click();
    await flush();
    return host;
}

test("a memories mark opens to two groups shut until clicked: the memories still shown with their weights, and those removed", async () => {
    const round = {
        shown: [{id: 4, text: "the suite runs in shards", weight_before: 4, weight_after: 3}],
        faded: [{id: 5, text: "the port is fixed", weight_before: 1, weight_after: 0}],
        removed: [{id: 6, text: "the old updater", weight: 6}],
    };
    const host = await opened(faded(round));
    expect([...host.querySelectorAll(".memory-round .fold-label")].map((label) => label.textContent)).toEqual(["Still shown", "Removed"]);
    expect(host.querySelectorAll(".memory-round-ref").length).toBe(0);
    for (const head of host.querySelectorAll(".memory-round .fold-head")) head.click();
    await flush();
    expect([...host.querySelectorAll(".memory-round-ref")].map((ref) => ref.textContent)).toEqual(["Memory 4", "Memory 5", "Memory 6"]);
    expect([...host.querySelectorAll(".memory-round-weight")].map((weight) => weight.textContent)).toEqual(["weight 4 to 3", "faded out at weight 0", "taken out at weight 6"]);
});

test("a memories mark written before rounds were kept opens and says the round was not recorded", async () => {
    const host = await opened(faded(null));
    expect(host.querySelector(".memory-round-missing").textContent).toContain("This round was not recorded");
});
