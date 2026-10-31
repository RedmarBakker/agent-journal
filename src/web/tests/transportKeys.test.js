import {afterEach, expect, test, vi} from "vitest";

const {transport} = await import("../src/api/transport.js");

afterEach(() => vi.restoreAllMocks());

const answering = () => {
    const sent = [];
    let finish = () => {};
    vi.spyOn(transport, "send").mockImplementation((method, url) => {
        sent.push(url);
        return new Promise((resolve) => (finish = () => resolve({url})));
    });
    return {sent, finish: () => finish()};
};

test("a read of a key in flight is not sent again: its caller takes the answer of the one in flight, whatever its query", async () => {
    const {sent, finish} = answering();
    const first = transport.request("GET", "/journal/messages?limit=25", undefined, 0, {}, "main messages.page");
    const same = transport.request("GET", "/journal/messages?limit=25", undefined, 0, {}, "main messages.page");
    const later = transport.request("GET", "/journal/messages?limit=25&since=99", undefined, 0, {}, "main messages.page");
    expect(sent).toEqual(["/journal/messages?limit=25"]);
    finish();
    expect(await Promise.all([first, same, later])).toEqual([{url: "/journal/messages?limit=25"}, {url: "/journal/messages?limit=25"}, {url: "/journal/messages?limit=25"}]);
    transport.request("GET", "/journal/messages?limit=25", undefined, 0, {}, "main messages.page");
    expect(sent).toHaveLength(2);
});

test("reads of different keys go out side by side, and a read with no key is keyed by its endpoint", async () => {
    const {sent} = answering();
    transport.request("GET", "/journal/messages?limit=25", undefined, 0, {}, "side messages.page");
    transport.request("GET", "/journal/messages?limit=25&before=40", undefined, 0, {}, "side messages.older");
    transport.request("GET", "/journal/summary?a=1");
    transport.request("GET", "/journal/summary?a=2");
    expect(sent).toEqual(["/journal/messages?limit=25", "/journal/messages?limit=25&before=40", "/journal/summary?a=1"]);
});

test("two reads of a table's rows by different ids go out side by side, each answered with its own rows", async () => {
    const {sent} = answering();
    const {api} = await import("../src/api/client.js");
    vi.spyOn(api, "env").mockReturnValue("main");
    api.list("tasks", {ids: [4481, 4482]});
    api.list("tasks", {ids: [4491, 4492]});
    api.list("tasks", {ids: [4491, 4492]});
    expect(sent.map((url) => url.split("/journal")[1])).toEqual(["/tasks?ids=4481%2C4482", "/tasks?ids=4491%2C4492"]);
});

test("an answer the journal sent without readable JSON is refused, so a poll keeps what it had", async () => {
    const {answered} = await import("../src/api/transport.js");
    await expect(answered(new Response("<html>", {status: 200}), "200 OK")).rejects.toThrow("could not be read");
    await expect(answered(new Response(JSON.stringify({rows: []}), {status: 200}), "200 OK")).resolves.toEqual({rows: []});
});
