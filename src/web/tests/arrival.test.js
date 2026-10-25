import {expect, test} from "vitest";
import {DEPART_MS, FADE_MS, OWN_MS, PUSH_MS, arrivalQueue, arrive, arriveAtOnce, depart} from "../src/chat/arrival.js";

function stage(follows = () => true, arrival = arrive) {
    const log = [];
    const style = new Proxy({}, {set: (target, key, value) => ((target[key] = value), log.push([key, value]), true)});
    const el = {style, offsetHeight: 60};
    const pane = {scrollTop: 0, scrollHeight: 1000};
    let now = 0;
    let queued = null;
    const frame = (callback) => (queued = callback);
    const step = (ms) => {
        now += ms;
        const run = queued;
        queued = null;
        run?.();
    };
    let finished = false;
    arrival(el, {pane, follows, frame, clock: () => now}, () => (finished = true));
    return {log, el, pane, step, finished: () => finished};
}

test("an arriving turn makes its room first and fades in only after, and the pane is held at the foot all the while", () => {
    const run = stage();
    expect(run.log.some(([key, value]) => key === "height" && value === "60px")).toBe(true);
    expect(run.el.style.opacity).toBe("0");
    run.step(PUSH_MS / 2);
    expect(run.el.style.opacity).toBe("0");
    expect(run.pane.scrollTop).toBe(1000);
    run.step(PUSH_MS);
    expect(run.el.style.opacity).toBe("1");
    const heightAt = run.log.findIndex(([key, value]) => key === "height" && value === "60px");
    const fadeAt = run.log.findIndex(([key, value]) => key === "opacity" && value === "1");
    expect(heightAt).toBeLessThan(fadeAt);
    run.step(FADE_MS + 10);
    expect(run.finished()).toBe(true);
    expect(run.el.style.height).toBe("");
});

test("a reader who is scrolled up sees nothing move: the turn is let in at once and no style is set", () => {
    const run = stage(() => false);
    expect(run.finished()).toBe(true);
    expect(run.log).toEqual([]);
});

test("the user's own message shows the moment it is sent: there at its full size, fading in, and done within a tenth of a second or so", () => {
    const run = stage(() => true, arriveAtOnce);
    expect(run.el.style.opacity).toBe("1");
    expect(run.log.some(([key]) => key === "height")).toBe(false);
    expect(run.el.style.transition).toContain("opacity");
    expect(run.pane.scrollTop).toBe(0);
    run.step(10);
    expect(run.pane.scrollTop).toBe(1000);
    run.step(OWN_MS + 5);
    expect(run.finished()).toBe(true);
    expect(OWN_MS).toBeLessThan(PUSH_MS);
});


test("turns that arrive together come in one after another with a gap, the waiting ones held off the page, and a reader who is away gets them at once", () => {
    const timers = [];
    const queue = arrivalQueue({gap: 100, later: (fn, ms) => timers.push([fn, ms])});
    const started = [];
    const turn = (name) => ({name, style: {}});
    const arrival = (el, options, done) => {
        started.push(el.name);
        el.finish = done;
    };
    const options = {pane: {}, follows: () => true};
    const [a, b, c] = ["a", "b", "c"].map(turn);
    const finished = [];
    [a, b, c].forEach((el) => queue(el, options, () => finished.push(el.name), arrival));
    expect(started).toEqual(["a"]);
    expect([b.style.display, c.style.display]).toEqual(["none", "none"]);
    a.finish();
    expect(finished).toEqual(["a"]);
    expect(started).toEqual(["a"]);
    expect(timers.map(([, ms]) => ms)).toEqual([100]);
    timers.shift()[0]();
    expect(started).toEqual(["a", "b"]);
    expect(b.style.display).toBe("");
    b.finish();
    timers.shift()[0]();
    expect(started).toEqual(["a", "b", "c"]);
    const away = turn("d");
    let arrived = false;
    queue(away, {pane: {}, follows: () => false}, () => (arrived = true), arrival);
    expect(arrived).toBe(true);
    expect(away.style.display).toBeUndefined();
});

test("a turn that goes closes its height while it fades, and is let go once the time has passed", () => {
    const el = {style: {}, offsetHeight: 48};
    let gone = false;
    const timers = [];
    depart(el, () => (gone = true), (fn, ms) => timers.push([fn, ms]));
    expect(el.style.height).toBe("0px");
    expect(el.style.opacity).toBe("0");
    expect(gone).toBe(false);
    expect(timers[0][1]).toBe(DEPART_MS);
    timers[0][0]();
    expect(gone).toBe(true);
});
