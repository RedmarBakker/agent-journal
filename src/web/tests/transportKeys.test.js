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
