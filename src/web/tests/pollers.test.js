import {beforeEach, describe, expect, test, vi} from "vitest";

const api = {env: () => "main", entries: vi.fn(), bar: vi.fn()};
const takeEntries = vi.fn();
vi.mock("../src/api/client.js", () => ({api}));
vi.mock("../src/sync/rows.js", () => ({takeEntries: (...a) => takeEntries(...a), PAGE: 50}));

const {POLLERS} = await import("../src/sync/pollers.js");
const {store} = await import("../src/state/store.js");

beforeEach(() => {
    api.entries.mockReset().mockResolvedValue([]);
    takeEntries.mockReset();
    store.entries = [];
    store.bar = null;
    store.streamOpen = false;
    store.agents = [];
});

describe("the poller table", () => {
    test("every key has two dot-separated segments or more, area first, and every poller reads something and says how often or on demand", () => {
        for (const [key, poller] of Object.entries(POLLERS)) {
            expect(key, key).toMatch(/^[a-z]+(\.[a-z]+)+$/);
            expect(typeof poller.read, key).toBe("function");
            expect(poller.demand ? !poller.pauses || poller.pauses in POLLERS : poller.every !== undefined, key).toBe(true);
        }
        expect(Object.isFrozen(POLLERS)).toBe(true);
    });

    test("the bar is asked twice a second while work queues, and every three seconds when calm", () => {
        expect(POLLERS["status.bar"].every()).toBe(3000);
        store.bar = [{id: 1}];
        expect(POLLERS["status.bar"].every()).toBe(500);
    });

    test("an answer that is not a list is not taken for the bar", () => {
        POLLERS["status.bar"].take({nothing: true});
        expect(store.bar).toBeNull();
        POLLERS["status.bar"].take([]);
        expect(store.bar).toEqual([]);
    });

    test("entries are polled every second, also while the stream is open", () => {
        store.streamOpen = true;
        expect(POLLERS["entries.recent"].active).toBeUndefined();
        expect(POLLERS["entries.recent"].every).toBe(1000);
    });

    test("entries are asked for after the newest one held, and each answer moves the mark on", async () => {
        store.entries = [{id: 7}];
        await POLLERS["entries.recent"].read();
        expect(api.entries).toHaveBeenLastCalledWith(7);
        POLLERS["entries.recent"].take([{id: 8}, {id: 9}]);
        expect(takeEntries).toHaveBeenCalledWith([{id: 8}, {id: 9}]);
        await POLLERS["entries.recent"].read();
        expect(api.entries).toHaveBeenLastCalledWith(9);
    });

    test("an empty answer changes nothing", () => {
        POLLERS["entries.recent"].take([]);
        expect(takeEntries).not.toHaveBeenCalled();
    });
});
