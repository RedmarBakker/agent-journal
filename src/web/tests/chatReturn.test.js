import {readFileSync} from "node:fs";
import {expect, test, vi} from "vitest";
import {arrivalQueue} from "../src/chat/arrival.js";

vi.mock("../src/sync/rows.js", () => ({reload: () => Promise.resolve()}));

test("back on the page by the window's focus, the return is marked for the chat to catch up", async () => {
    const {ui} = await import("../src/state/ui.js");
    await import("../src/platform/visibility.js");
    const before = ui.away.returnedAt;
    window.dispatchEvent(new Event("focus"));
    expect(ui.away.returnedAt).toBeGreaterThan(before);
});

test("the turns still queued to come in one by one are shown at once when the queue is flushed", () => {
    const shown = [];
    const enqueue = arrivalQueue({later: () => {}});
    const options = {pane: {}, follows: () => true};
    const item = (id) => ({id, style: {display: ""}});
    const first = item(1);
    enqueue(first, options, () => shown.push(1), (el, given, done) => {});
    const waiting = [item(2), item(3)];
    waiting.forEach((el) => enqueue(el, options, () => shown.push(el.id)));
    expect(waiting.map((el) => el.style.display)).toEqual(["none", "none"]);
    enqueue.flush();
    expect(waiting.map((el) => el.style.display)).toEqual(["", ""]);
    expect(shown).toEqual([2, 3]);
});

test("the thread flushes its queue and goes to the foot at every return", () => {
    const thread = readFileSync("src/chat/Thread.vue", "utf8");
    expect(thread).toMatch(/\(\) => ui\.away\.returnedAt,\s*\(\) => \{\s*comeIn\.flush\(\);\s*if \(!away\.value\) toFoot\(\);/);
});
