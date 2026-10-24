import {expect, test} from "vitest";
import {FADE_MS, PUSH_MS, arrive} from "../src/chat/arrival.js";

function stage(follows = () => true) {
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
    arrive(el, {pane, follows, frame, clock: () => now}, () => (finished = true));
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
