import {expect, test, vi} from "vitest";

const reads = [];
let finishRead = () => {};
vi.mock("../src/sync/rows.js", () => ({
    reload: () => {
        reads.push(Date.now());
        return new Promise((resolve) => (finishRead = resolve));
    },
}));

function showTab(hidden) {
    Object.defineProperty(document, "hidden", {configurable: true, get: () => hidden});
    Object.defineProperty(document, "visibilityState", {configurable: true, get: () => (hidden ? "hidden" : "visible")});
    document.dispatchEvent(new Event("visibilitychange"));
}

test("turns that come while the tab is hidden show at once, and the return reads the latest page once before turns come in one by one again", async () => {
    const {ui} = await import("../src/state/ui.js");
    const {arrivalQueue} = await import("../src/chat/arrival.js");
    await import("../src/platform/visibility.js");
    const queue = arrivalQueue({later: () => {}});
    const started = [];
    const finished = [];
    const follows = () => !ui.away.tabHidden && !ui.away.readingLatest;
    const arrival = (el) => started.push(el.name);
    const turn = (name) => ({name, style: {}});
    const options = {pane: {}, follows};
    ["a", "b", "c"].forEach((name) => queue(turn(name), options, () => finished.push(name), arrival));
    expect(started).toEqual(["a"]);

    showTab(true);
    expect(ui.away.tabHidden).toBe(true);
    queue.flush();
    expect(finished).toEqual(["b", "c"]);
    queue(turn("d"), options, () => finished.push("d"), arrival);
    expect(finished).toEqual(["b", "c", "d"]);

    showTab(false);
    window.dispatchEvent(new Event("focus"));
    expect(ui.away.tabHidden).toBe(false);
    expect(ui.away.readingLatest).toBe(true);
    expect(reads).toHaveLength(1);
    queue(turn("e"), options, () => finished.push("e"), arrival);
    expect(finished).toEqual(["b", "c", "d", "e"]);

    finishRead();
    await vi.waitFor(() => expect(ui.away.readingLatest).toBe(false));
    expect(reads).toHaveLength(1);
    expect(started).toEqual(["a"]);
});
