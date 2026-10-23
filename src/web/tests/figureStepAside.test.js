// @vitest-environment node
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {SPANS, groundEdge, roomToStepAside} = await import("../src/figure/places.js");

// a chat whose compose box runs from 300 to 700 across the page, with bars docked over it from `left` to `right`, or none
function chat(docked) {
    const bars = docked && boxed({left: docked.left, right: docked.right, top: 540, bottom: 600});
    const thread = {...boxed({left: 200, top: 100, right: 900, bottom: 800}), querySelector: (selector) => (selector === "[data-figure-docked-bars]" ? bars : null)};
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
    return {bars, home};
}

// the figure resting on the bars docked over the compose box, as it rides up onto a card that docks under it
const onTheBars = (bars) => ({x: 500, y: 540, posture: "stand", on: bars});

test("a card docked over the compose box full width sets off no step-aside: the figure stands on it, with nowhere beside to step", () => {
    const {bars} = chat({left: 300, right: 700});
    expect(groundEdge().docked).toBe(true);
    expect(roomToStepAside(onTheBars(bars))).toBe(false);
    // as wide as the compose box to a pixel or two, as a card's border lays it out
    const {bars: near} = chat({left: 300 + SPANS.within / 2, right: 700 - SPANS.within / 2});
    expect(roomToStepAside(onTheBars(near))).toBe(false);
});

test("a narrower docked card, with room beside it, still sets off the step-aside, and away from the docks it is as ever", () => {
    const {bars} = chat({left: 300, right: 560});
    expect(roomToStepAside(onTheBars(bars)), "room on the right of it").toBe(true);
    const {bars: centred} = chat({left: 380, right: 620});
    expect(roomToStepAside(onTheBars(centred)), "room on both sides").toBe(true);
    const {home} = chat(null);
    expect(roomToStepAside({x: 500, y: 600, posture: "stand", on: home}), "no card docked").toBe(true);
    chat({left: 300, right: 700});
    expect(roomToStepAside({x: 500, y: 300, posture: "stand", on: {}}), "resting on a bubble, not the docked card").toBe(true);
});
