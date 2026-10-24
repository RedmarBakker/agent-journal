import {afterEach, beforeEach, describe, expect, test, vi} from "vitest";

// the poller table these tests declare their own pollers in, as the app declares its own in sync/pollers.js
const table = {};
vi.mock("../src/sync/pollers.js", () => ({POLLERS: table}));

const {demand, pausePoller, resumePoller, startPoll, usePoll, wakePolls} = await import("../src/composables/poll.js");

let keys = 0;
const stops = [];
const declared = (read, every, extra = {}) => {
    const key = `test.poller${++keys}`;
    table[key] = {read, every, ...extra};
    return key;
};
const begin = (read, every, take = () => {}, active = () => true) => {
    const stop = startPoll(declared(read, every), {take, active});
    stops.push(stop);
    return stop;
};

beforeEach(() => {
    vi.useFakeTimers();
    vi.spyOn(Math, "random").mockReturnValue(1);
    vi.spyOn(document, "hasFocus").mockReturnValue(true);
});

afterEach(() => {
    stops.splice(0).forEach((stop) => stop());
    vi.useRealTimers();
    vi.restoreAllMocks();
});

const passed = (ms) => vi.advanceTimersByTimeAsync(ms);

describe("a poll", () => {
    test("asks at once, then again after its interval, handing each answer to its user", async () => {
        const ask = vi.fn().mockResolvedValue("row");
        const take = vi.fn();
        begin(ask, 1000, take);
        await passed(0);
        expect(take).toHaveBeenCalledWith("row");
        await passed(1000);
        expect(ask).toHaveBeenCalledTimes(2);
    });

    test("failures back off to a cap of a minute and a good answer returns to the interval", async () => {
        const ask = vi.fn().mockRejectedValue(new Error("down"));
        begin(ask, 1000);
        await passed(0);
        await passed(10000);
        await passed(10000);
        const spaced = ask.mock.calls.length;
        expect(spaced).toBeLessThan(10);
        await passed(3600000);
        const hour = ask.mock.calls.length - spaced;
        expect(hour).toBeLessThanOrEqual(61);
        expect(hour).toBeGreaterThanOrEqual(55);
        ask.mockResolvedValue("ok");
        await passed(60000);
        const before = ask.mock.calls.length;
        await passed(5000);
        expect(ask.mock.calls.length - before).toBeGreaterThanOrEqual(4);
    });

    test("a throw in every() or active() still schedules the next round", async () => {
        const ask = vi.fn().mockResolvedValue("row");
        let broken = true;
        begin(ask, () => {
            if (broken) throw new Error("bad interval");
            return 1000;
        }, undefined, () => {
            if (broken) throw new Error("bad active");
            return true;
        });
        await passed(0);
        expect(ask).not.toHaveBeenCalled();
        broken = false;
        await passed(10000);
        expect(ask).toHaveBeenCalled();
    });

    test("a failed round never reaches the user", async () => {
        const take = vi.fn();
        begin(vi.fn().mockRejectedValue(new Error("down")), 1000, take);
        await passed(5000);
        expect(take).not.toHaveBeenCalled();
    });

    test("waking the polls asks a failing one again soon, and leaves a healthy one alone", async () => {
        const failing = vi.fn().mockRejectedValue(new Error("down"));
        const healthy = vi.fn().mockResolvedValue("ok");
        begin(failing, 1000);
        begin(healthy, 60000);
        await passed(0);
        await passed(30000);
        const [f, h] = [failing.mock.calls.length, healthy.mock.calls.length];
        wakePolls();
        await passed(500);
        expect(failing.mock.calls.length).toBe(f + 1);
        expect(healthy.mock.calls.length).toBe(h);
    });

    test("a page out of view or out of focus asks ten times less often and a shown one asks at its pace again", async () => {
        const ask = vi.fn().mockResolvedValue("ok");
        begin(ask, 1000);
        await passed(0);
        Object.defineProperty(document, "hidden", {configurable: true, value: true});
        document.dispatchEvent(new Event("visibilitychange"));
        await passed(5000);
        expect(ask).toHaveBeenCalledTimes(1);
        await passed(5000);
        expect(ask).toHaveBeenCalledTimes(2);
        Object.defineProperty(document, "hidden", {configurable: true, value: false});
        document.dispatchEvent(new Event("visibilitychange"));
        await passed(500);
        expect(ask).toHaveBeenCalledTimes(3);
        document.hasFocus.mockReturnValue(false);
        window.dispatchEvent(new Event("blur"));
        await passed(5000);
        expect(ask).toHaveBeenCalledTimes(3);
        document.hasFocus.mockReturnValue(true);
        window.dispatchEvent(new Event("focus"));
        await passed(500);
        expect(ask).toHaveBeenCalledTimes(4);
    });

    test("an inactive poll asks nothing and a stopped one stays stopped", async () => {
        const ask = vi.fn().mockResolvedValue("ok");
        const stop = begin(ask, 1000, () => {}, () => false);
        await passed(5000);
        expect(ask).not.toHaveBeenCalled();
        const live = vi.fn().mockResolvedValue("ok");
        const stopLive = begin(live, 1000);
        await passed(0);
        stopLive();
        await passed(5000);
        expect(live).toHaveBeenCalledTimes(1);
        stop();
    });

    test("a page that joins a poll another page runs is handed its last answer at once, before the next round", async () => {
        const ask = vi.fn().mockResolvedValue(["helper 1"]);
        const key = declared(ask, 5000);
        stops.push(startPoll(key));
        await passed(0);
        const joined = vi.fn();
        stops.push(startPoll(key, {take: joined}));
        expect(joined).toHaveBeenCalledWith(["helper 1"]);
        expect(ask).toHaveBeenCalledTimes(1);
    });

    test("when the first user of a shared poll leaves, the next round reads with the params of the user that stayed", async () => {
        const read = vi.fn(async ({who}) => who);
        const key = declared(read, 1000);
        const taken = vi.fn();
        const stopFirst = startPoll(key, {params: () => ({who: "first"}), active: () => false});
        const stopSecond = startPoll(key, {params: () => ({who: "second"}), take: taken});
        stops.push(stopFirst, stopSecond);
        stopFirst();
        await passed(1000);
        expect(read).toHaveBeenLastCalledWith({who: "second"});
        expect(taken).toHaveBeenCalledWith("second");
    });

    test("a key the table does not declare is refused", () => {
        expect(() => startPoll("test.undeclared")).toThrow(/no poller test.undeclared/);
    });

    test("a poller declared by agent runs once for each agent its users name, and a round is never sent while the last is in flight", async () => {
        let answer = () => {};
        const read = vi.fn(({agent}) => new Promise((resolve) => (answer = () => resolve(agent))));
        const key = declared(read, 1000, {by: ({agent}) => agent});
        stops.push(startPoll(key, {params: () => ({agent: 1})}), startPoll(key, {params: () => ({agent: 1})}), startPoll(key, {params: () => ({agent: 2})}));
        await passed(0);
        expect(read.mock.calls.map(([params]) => params.agent)).toEqual([1, 2]);
        await passed(5000);
        expect(read).toHaveBeenCalledTimes(2);
        answer();
    });
});

describe("pausing a poller and an on-demand one", () => {
    test("a pause settles only once nothing of the poller is in flight, and the poller asks nothing until resumed", async () => {
        let answer = () => {};
        const read = vi.fn(() => new Promise((resolve) => (answer = () => resolve("rows"))));
        const key = declared(read, 1000);
        stops.push(startPoll(key));
        await passed(0);
        let settled = false;
        const pausing = pausePoller(key).then((paused) => ((settled = true), paused));
        await passed(0);
        expect(settled).toBe(false);
        answer();
        const paused = await pausing;
        await passed(5000);
        expect(read).toHaveBeenCalledTimes(1);
        resumePoller(paused);
        await passed(0);
        expect(read).toHaveBeenCalledTimes(2);
    });

    test("an on-demand poller reads once when asked, with the poller it pauses quiet for the whole of its read", async () => {
        const order = [];
        const latest = vi.fn(async () => order.push("latest"));
        const key = declared(latest, 1000);
        const older = declared(
            async ({before}) => {
                order.push(`older before ${before}`);
                await new Promise((resolve) => setTimeout(resolve, 3000));
                order.push("older answered");
                return "page";
            },
            undefined,
            {demand: true, pauses: key}
        );
        stops.push(startPoll(key));
        await passed(0);
        const page = demand(older, {before: 40});
        await passed(3000);
        expect(await page).toBe("page");
        await passed(0);
        await passed(10);
        expect(order).toEqual(["latest", "older before 40", "older answered", "latest"]);
    });
});

describe("the least time between reads of an on-demand poller", () => {
    test("a run reads at most once a second unless it declares its own least, and each place has its own", async () => {
        const read = vi.fn(async ({page}) => page);
        const key = declared(read, undefined, {demand: true, by: ({place}) => place});
        const quick = declared(read, undefined, {demand: true, least: 100});
        const first = demand(key, {place: "a", page: 1});
        const second = demand(key, {place: "a", page: 2});
        const other = demand(key, {place: "b", page: 3});
        await passed(0);
        expect(read.mock.calls.map(([params]) => params.page)).toEqual([1, 3]);
        await passed(999);
        expect(read).toHaveBeenCalledTimes(2);
        await passed(1);
        expect(read).toHaveBeenCalledTimes(3);
        expect(await Promise.all([first, second, other])).toEqual([1, 2, 3]);
        demand(quick, {page: 4});
        demand(quick, {page: 5});
        await passed(100);
        expect(read.mock.calls.map(([params]) => params.page).slice(3)).toEqual([4, 5]);
    });
});

describe("the key a poller is used by", () => {
    test("a user that comes to name another agent moves to that agent's run", async () => {
        const read = vi.fn(async ({agent}) => agent);
        const key = declared(read, 60000, {by: ({agent}) => agent});
        expect(typeof usePoll).toBe("function");
        stops.push(startPoll(key, {params: () => ({agent: 3})}));
        await passed(0);
        expect(read).toHaveBeenLastCalledWith({agent: 3});
    });
});

describe("while the update cover is up", () => {
    test("every poll but the update's own status holds its question, and asks again once the cover is gone", async () => {
        const {begin: startUpdate, clear} = await import("../src/state/updating.js");
        const other = vi.fn().mockResolvedValue("row");
        const status = vi.fn().mockResolvedValue("status");
        startUpdate("2.0.0");
        table["status.summary"] = {read: status, every: 1000};
        stops.push(startPoll("status.summary"));
        begin(other, 1000);
        await passed(0);
        expect([status.mock.calls.length, other.mock.calls.length]).toEqual([1, 0]);
        clear();
        await passed(1000);
        expect(other).toHaveBeenCalled();
    });
});

describe("a fetch while the update cover is up", () => {
    test("is turned away before it is sent, except the update's status", async () => {
        const {transport} = await import("../src/api/transport.js");
        const {begin: startUpdate, clear} = await import("../src/state/updating.js");
        const sent = vi.fn().mockResolvedValue(new Response("{}", {status: 200}));
        vi.stubGlobal("fetch", sent);
        startUpdate("2.0.0");
        await expect(transport.request("GET", "/journal/tasks")).rejects.toMatchObject({updating: true});
        await transport.request("GET", "/journal/summary");
        expect(sent.mock.calls.map((call) => call[0])).toEqual(["/journal/summary"]);
        clear();
        vi.unstubAllGlobals();
    });
});
