import {afterEach, expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {api} = await import("../src/api/client.js");
const {choose} = await import("../src/state/environment.js");
const {store} = await import("../src/state/store.js");
const {earlier, keepRows, load, pageOf, refresh, releaseRows, rows} = await import("../src/sync/rows.js");
choose("main");

const message = (id) => ({table: "messages", id, author: "agent", text: `reply ${id}`, agent_role: "main", data: {}, created_at: new Date(id * 1000).toISOString(), updated_at: new Date(id * 1000).toISOString()});
const CHAT = Array.from({length: 200}, (_, index) => message(index + 1));

// the messages api over a chat of 200: the newest page, or the page before a message
const listed = async (table, {limit, before, since}) => {
    if (since) return {rows: CHAT.filter((m) => Date.parse(m.updated_at) / 1000 > since), is_last_page: true, counts: {}};
    const older = before ? CHAT.filter((m) => m.id < before) : CHAT;
    const page = older.slice(-limit);
    return {rows: page, is_last_page: page[0].id === 1, counts: {}};
};

afterEach(() => vi.restoreAllMocks());

test("the chat opens with its latest 25 messages and each scroll to the top loads one page of 25 more", async () => {
    const list = vi.spyOn(api, "list").mockImplementation(listed);
    store.rows.messages = [];
    store.paging.size.messages = 0;
    expect(pageOf("messages")).toBe(25);
    await load("messages");
    expect(list).toHaveBeenCalledTimes(1);
    expect(list).toHaveBeenLastCalledWith("messages", {limit: 25});
    expect(store.rows.messages.map((m) => m.id)).toEqual(CHAT.slice(-25).map((m) => m.id));
    await earlier("messages");
    expect(list).toHaveBeenCalledTimes(2);
    expect(list).toHaveBeenLastCalledWith("messages", {limit: 25, before: 176});
    expect(store.rows.messages).toHaveLength(50);
    expect(pageOf("tasks")).toBe(50);
});

test("scrolled back, the chat keeps every page it loaded while new messages arrive, and back at the foot it trims to the newest 25", async () => {
    vi.spyOn(api, "list").mockImplementation(listed);
    store.rows.messages = [];
    store.paging.size.messages = 0;
    rows("messages");
    await load("messages");
    keepRows("messages");
    await earlier("messages");
    await earlier("messages");
    expect(store.rows.messages).toHaveLength(75);
    const top = store.rows.messages[0].id;
    CHAT.push(message(201));
    await refresh(["messages"]);
    expect(store.rows.messages).toHaveLength(76);
    expect(store.rows.messages[0].id).toBe(top);
    expect(store.rows.messages.at(-1).id).toBe(201);
    releaseRows("messages");
    expect(store.rows.messages.map((m) => m.id)).toEqual(CHAT.slice(-25).map((m) => m.id));
    CHAT.pop();
});

test("a reconnect reads the chat again but redraws nothing: every message unchanged since is the very row the chat held, a changed one is new", async () => {
    // each read answers fresh rows, as the server's JSON does
    vi.spyOn(api, "list").mockImplementation(async (table, options) => {
        const got = await listed(table, options);
        return {...got, rows: got.rows.map((row) => structuredClone(row))};
    });
    vi.spyOn(api, "entries").mockImplementation(async () => []);
    vi.spyOn(api, "settings").mockImplementation(async () => ({}));
    const {reload} = await import("../src/sync/rows.js");
    store.rows.messages = [];
    store.paging.size.messages = 0;
    rows("messages");
    await load("messages");
    const before = [...store.rows.messages];
    const edited = CHAT.length - 3;
    CHAT[edited - 1] = {...CHAT[edited - 1], text: "edited", updated_at: new Date(10_000_000).toISOString()};
    await reload();
    await new Promise((settle) => setTimeout(settle, 80));
    const after = store.rows.messages;
    expect(after.map((m) => m.id)).toEqual(before.map((m) => m.id));
    for (const [index, row] of after.entries()) {
        if (row.id === edited) expect(row, "a changed message is read anew").not.toBe(before[index]);
        else expect(row, `message ${row.id} kept as held`).toBe(before[index]);
    }
});
