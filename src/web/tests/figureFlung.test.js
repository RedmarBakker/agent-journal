// @vitest-environment node
import {expect, test} from "vitest";
import {page} from "./support/figurePage.js";

const {FLUNG, floorOf, footingOn, groundUnder, readFloors, throwSpeed} = await import("../src/figure/floors.js");
const {GRAVITY} = await import("../src/domain/falls.js");
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

// the ground under the perched figure frame by frame as its bubble rises each frame's pixels of `rises`, a scroll, and then stands still,
// each frame's answer in turn until it is thrown off
function scrolled(kind, rises) {
    let {bubble, spot, footing} = perched(kind);
    let floors = readFloors(undefined, 1000);
    const frames = [];
    for (const [index, pixels] of [...rises, 0].entries()) {
        bubble.top -= pixels;
        floors = readFloors(floors, 1000 + (index + 1) * FRAME);
        const ground = groundUnder(footing, spot, FIGURE, floors.floors);
        frames.push(ground);
        if (ground.motion === "flung") break;
        ({spot, footing} = ground);
    }
    return frames;
}
// how high a figure thrown up at `speed` goes before it falls back, in pixels
const apex = (speed) => (speed * speed) / (2 * GRAVITY);

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

test("a fast scroll flings the bubble the figure hangs from, or stands on: carried up through the burst, it is thrown off as the burst slows; a slow one leaves it hanging", () => {
    const fast = (FLUNG.speed * 1.5 * FRAME) / 1000;
    const slow = (FLUNG.speed * 0.3 * FRAME) / 1000;
    for (const kind of ["hang", "stand"]) {
        const thrown = scrolled(kind, [fast, fast, fast]);
        expect(thrown.slice(0, 3).map((frame) => frame.motion), `${kind}: carried through the burst`).toEqual(["carried", "carried", "carried"]);
        expect(thrown[2].spot.y, `${kind}: carried up with it`).toBeCloseTo(perched(kind).spot.y - 3 * fast, 5);
        expect(thrown[3].motion, `${kind}: thrown as it slows`).toBe("flung");
        expect(thrown[3].speed, `${kind}: thrown up`).toBeCloseTo(throwSpeed(3 * fast), 6);
        const kept = scrolled(kind, [slow, slow, slow]);
        expect(kept.map((frame) => frame.motion), `${kind}: still on it`).toEqual(["carried", "carried", "carried", "carried"]);
        expect(kept[3].spot.posture, kind).toBe(kind);
    }
    expect(scrolled("hang", [-fast, -fast]).map((frame) => frame.motion), "a fast scroll up carries it down").toEqual(["carried", "carried", "carried"]);
});

test("thrown off a bubble, the figure goes up as far as the chat moved: a small quick nudge throws it a little way, a long fast scroll high", () => {
    const fast = (FLUNG.speed * 1.5 * FRAME) / 1000;
    const thrownBy = (frames) => scrolled("hang", Array.from({length: frames}, () => fast)).find((frame) => frame.motion === "flung").speed;
    const nudge = apex(thrownBy(1));
    const scroll = apex(thrownBy(6));
    expect(nudge, "a nudge: a little way up").toBeLessThan(30);
    expect(scroll, "a long scroll: high").toBeGreaterThan(100);
    // as high as its share of how far the bubble rose, whatever the speed past the throw's own
    expect(nudge).toBeCloseTo(FLUNG.share * fast, 6);
    expect(scroll).toBeCloseTo(FLUNG.share * 6 * fast, 6);
    // a scroll that carries it out of sight throws it as it goes, as high as the bubble had risen by then
    expect(apex(thrownBy(30))).toBeGreaterThan(scroll);
});

test("thrown off, its momentum carries it up and it falls back home on its feet, or, thrown hard, goes off the top to come back on its parachute", () => {
    perched("hang");
    const home = readFloors().floors.find((floor) => floor.id === "home");
    const top = readFloors().world.top;
    const back = flight(500, throwSpeed(250), top);
    expect(Math.min(...back.heights), "carried up").toBeLessThan(500 - 100);
    expect(back.gone, "short of the top").toBeUndefined();
    expect(back.landed.spot).toMatchObject({y: home.top, posture: "stand"});
    const off = flight(500, throwSpeed(2000), top);
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
