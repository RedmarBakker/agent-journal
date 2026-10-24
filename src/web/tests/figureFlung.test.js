// @vitest-environment node
import {expect, test} from "vitest";
import {page} from "./support/figurePage.js";

const {FLUNG, floorOf, footingOn, groundUnder, readFloors} = await import("../src/figure/floors.js");
const {stayingAt} = await import("../src/figure/perches.js");
const {airborneFrame, goneUp, launchFrom} = await import("../src/domain/figureMotion.js");
const {skywardAt} = await import("../src/figure/skyward.js");

const FIGURE = {size: 112, below: 0.05};
// a frame of the page, in milliseconds
const FRAME = 16;

// the figure perched on a bubble of the chat, as `kind` says, a hang from its side or a stand on its top, and the bubble's top it moves
function perched(kind) {
    const bubble = {top: 400, getBoundingClientRect: () => ({left: 260, right: 600, top: bubble.top, bottom: bubble.top + 60, width: 340, height: 60})};
    page(bubble);
    const stay = {where: "bubble", perch: {floor: floorOf(bubble), kind, side: "right", grip: kind === "hang" ? "r" : "", face: 0}, until: 1e9};
    const spot = stayingAt(stay, FIGURE, {x: 600, y: 600});
    return {bubble, spot, footing: footingOn(spot)};
}

// the ground under the perched figure once its bubble rose `pixels` in one frame of a scroll
function scrolled(kind, pixels) {
    const {bubble, spot, footing} = perched(kind);
    const before = readFloors(undefined, 1000);
    bubble.top -= pixels;
    return groundUnder(footing, spot, FIGURE, readFloors(before, 1000 + FRAME).floors);
}

// a launch from feet at `y` at the bubble's `speed`, stepped frame by frame until it lands or goes off the top of the world at `top`
function flight(y, speed, top) {
    const floors = readFloors().floors;
    let airborne = launchFrom({x: 400, y, face: 0}, speed, 0);
    const heights = [y];
    for (let now = FRAME; now < 10000; now += FRAME) {
        const frame = airborneFrame(airborne, floors, now);
        if (frame.landed) return {heights, landed: frame.landed};
        airborne = frame.airborne;
        heights.push(airborne.y);
        if (goneUp(airborne, top)) return {heights, gone: true};
    }
    return {heights};
}

test("a fast scroll flings the bubble the figure hangs from, or stands on, and throws it off; a slow one leaves it hanging", () => {
    const fast = (FLUNG.speed * 1.5 * FRAME) / 1000;
    const slow = (FLUNG.speed * 0.3 * FRAME) / 1000;
    for (const kind of ["hang", "stand"]) {
        const thrown = scrolled(kind, fast);
        expect(thrown.motion, `${kind}: launched`).toBe("flung");
        expect(thrown.speed, `${kind}: thrown up`).toBeLessThanOrEqual(-FLUNG.speed * FLUNG.carry);
        const kept = scrolled(kind, slow);
        expect(kept.motion, `${kind}: still on it`).toBe("carried");
        expect(kept.spot.posture, kind).toBe(kind);
        expect(kept.spot.y, `${kind}: carried up with it`).toBeCloseTo(perched(kind).spot.y - slow, 5);
    }
    expect(scrolled("hang", -fast).motion, "a fast scroll up carries it down").toBe("carried");
});

test("thrown off, its momentum carries it up and it falls back home on its feet, or, thrown hard, goes off the top to come back on its parachute", () => {
    perched("hang");
    const home = readFloors().floors.find((floor) => floor.id === "home");
    const top = readFloors().world.top;
    const back = flight(500, -FLUNG.speed * FLUNG.carry, top);
    expect(Math.min(...back.heights), "carried up").toBeLessThan(500 - 100);
    expect(back.gone, "short of the top").toBeUndefined();
    expect(back.landed.spot).toMatchObject({y: home.top, posture: "stand"});
    const off = flight(500, -3 * FLUNG.speed * FLUNG.carry, top);
    expect(off.gone, "off the top").toBe(true);
    expect(skywardAt([], 0).gone, "out of sight at once, for the parachute to bring back").toBe(true);
});

test("a figure coming down on its parachute from above the top of the screen is never taken for one thrown off it again", async () => {
    const {chuteFrom} = await import("../src/domain/figureMotion.js");
    const top = 100;
    const chute = chuteFrom(400, top - 30, 200, 0, () => 0.5);
    expect(goneUp(chute, top), "starting above the top, falling").toBe(false);
    const rising = launchFrom({x: 400, y: top - 5, face: 0}, -900, 0);
    expect(goneUp(rising, top), "still rising past the top").toBe(true);
});
