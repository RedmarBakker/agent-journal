import {createApp, h} from "vue";
import {expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {useFileFeed} = await import("../src/composables/fileFeed.js");
const {choose} = await import("../src/state/environment.js");
choose("main");

const edit = (id) => ({id, path: `f${id}.py`, edit_type: "edit", time: id, added: 1, removed: 0, first_line: 1, last_line: 1, rows: [{line_type: "add", line: 1, text: "x"}]});
const ALL = Array.from({length: 120}, (_, i) => edit(i + 1));

const client = {
    env: () => "main",
    edits: vi.fn(async (agent, since, fields = {}) => {
        if (since && !fields.before) return {cursor: since, edits: [], older: false};
        const below = fields.before ? ALL.filter((e) => e.id < fields.before) : ALL;
        const page = below.slice(-50);
        return {cursor: 1, edits: page, older: Boolean(page.length) && page[0].id > 1};
    }),
};

test("the file feed opens on the newest fifty edits and each older load prepends fifty more until none are left", async () => {
    let feed;
    const app = createApp({setup: () => ((feed = useFileFeed(1, {landed() {}, snap() {}}, client)), () => h("div"))});
    app.mount(document.createElement("div"));
    await vi.waitFor(() => expect(feed.ready.value).toBe(true));
    expect(feed.cards.value[0].id).toBe(71);
    expect(feed.older.value).toBe(true);
    expect(await feed.earlier()).toBe(50);
    expect(client.edits).toHaveBeenLastCalledWith(1, 0, {before: 71});
    expect(feed.cards.value[0].id).toBe(21);
    expect(await feed.earlier()).toBe(20);
    expect(feed.older.value).toBe(false);
    expect(feed.cards.value[0].id).toBe(1);
    expect(feed.cards.value).toHaveLength(120);
    expect(await feed.earlier()).toBe(0);
    app.unmount();
});
