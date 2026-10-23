import {afterEach, expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {api} = await import("../src/api/client.js");
const {choose} = await import("../src/state/environment.js");
const {store} = await import("../src/state/store.js");
const {earlier, load, pageOf} = await import("../src/sync/rows.js");
choose("main");

const message = (id) => ({table: "messages", id, author: "agent", text: `reply ${id}`, agent_role: "main", data: {}, created_at: new Date(id * 1000).toISOString(), updated_at: new Date(id * 1000).toISOString()});
const CHAT = Array.from({length: 200}, (_, index) => message(index + 1));

// the messages api over a chat of 200: the newest page, or the page before a message
const listed = async (table, {limit, before}) => {
    const older = before ? CHAT.filter((m) => m.id < before) : CHAT;
    const rows = older.slice(-limit);
    return {rows, is_last_page: rows[0].id === 1, counts: {}};
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
