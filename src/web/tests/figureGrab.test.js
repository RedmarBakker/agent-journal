import {expect, test} from "vitest";

const {GRAB, headTiltFor, onHead, pointerSpeed, resumedClock, thrownFrame, thrownFrom} = await import("../src/figure/grab.js");
const {CLIPS} = await import("../src/figure/figure.js");
const {SKYWARD} = await import("../src/figure/skyward.js");
const {PICTURES, WHOA_SPOT, litPixels} = await import("../src/figure/visorPixels.js");
const {airborneFrame, chuteFrom} = await import("../src/domain/figureMotion.js");

const SIZE = 112;
// the feet may go anywhere across a chat from 56 to 944 pixels, whose top is at 100
const ROOM = {left: 56, right: 944, top: 100};
// the chat's floor, the compose box's top at 700 under the chat's whole width, and two bubbles above it, one overhanging the other
const HOME = {id: "home", kind: "compose", left: 56, right: 944, top: 700, element: "home"};
const UPPER = {id: "upper", kind: "bubble", left: 100, right: 500, top: 300, bottom: 360, element: "upper"};
const LOWER = {id: "lower", kind: "bubble", left: 300, right: 800, top: 500, bottom: 560, element: "lower"};
const FLOORS = [HOME, UPPER, LOWER];

// the throw flown at 60 frames a second from its first frame at 0 until it lands or is gone, with every frame it passed through
function flown(thrown) {
    const frames = [thrown];
    for (let frame = 1; frame < 60 * 30; frame++) {
        const next = thrownFrame(frames.at(-1), FLOORS, ROOM, (frame * 1000) / 60);
        if (!next.airborne || next.gone) return {frames, ...next};
        frames.push(next.airborne);
    }
    return {frames, landed: null, gone: false};
}

// the highest floor under `x` whose top is at or below `y`
const nearestBelow = (x, y) => FLOORS.filter((floor) => floor.left <= x && floor.right >= x && floor.top >= y).sort((a, b) => a.top - b.top)[0];

test("the head dragged across tilts with the pointer, never past the largest angle either way, and only a press above the neck takes the head", () => {
    expect(headTiltFor(0)).toBe(0);
    expect(headTiltFor(10)).toBeCloseTo(10 * GRAB.pull, 6);
    expect(headTiltFor(-10)).toBeCloseTo(-10 * GRAB.pull, 6);
    for (const across of [GRAB.tilt / GRAB.pull, 200, 5000]) {
        expect(headTiltFor(across)).toBe(GRAB.tilt);
        expect(headTiltFor(-across)).toBe(-GRAB.tilt);
    }
    const head = {x: 0.5, y: 0.3};
    expect(onHead({x: 0.5, y: 0.2}, head)).toBe(true);
    expect(onHead({x: 0.5, y: head.y + GRAB.neck}, head)).toBe(true);
    expect(onHead({x: 0.5, y: 0.6}, head)).toBe(false);
});

test("while the head is held the act stands still on its frame, startled with a 'whoa', and once let go goes on from that frame", () => {
    const clip = CLIPS.find((each) => each.name === "disco");
    const frameAt = (started, now) => Math.floor(((now - started) / 1000) * clip.fps);
    // the act started at 0, the head held at 1.3 seconds and let go 4 seconds later: the frame then is the frame it was held on
    const [started, began, released] = [0, 1300, 5300];
    const resumed = resumedClock(started, began, released);
    expect(frameAt(resumed, released)).toBe(frameAt(started, began));
    // and it plays on from there, a frame each frame's time
    expect(frameAt(resumed, released + 1000 / clip.fps)).toBe(frameAt(started, began) + 1);
    // held, the visor shows wide eyes and a round mouth under them
    const face = {eyed: true, eyes: 1.5, glance: [0, 0], tint: null, hearts: 0, stars: 0, squeezed: 0, dozing: 0, sign: null, ticker: null};
    const mouth = (lit) => lit.filter((pixel) => Math.abs(pixel.column - WHOA_SPOT.column) <= 2 && Math.abs(pixel.row - WHOA_SPOT.row) <= 2);
    expect(mouth(litPixels(face))).toEqual([]);
    expect(mouth(litPixels({...face, whoa: true})).length).toBe(PICTURES.whoa.join("").split("#").length - 1);
    expect(litPixels({...face, whoa: true}).length).toBeGreaterThan(litPixels(face).length);
});

test("let go, the figure flies off at the pointer's speed and way over its last moves, never faster than the fastest throw", () => {
    // the pointer swept 60 pixels right and 30 up over its last 50 ms, after a slow drag before
    const moves = [{x: 0, y: 0, at: 0}, {x: 10, y: 0, at: 0.5}, {x: 40, y: -15, at: 0.525}, {x: 70, y: -30, at: 0.55}];
    const speed = pointerSpeed(moves, 0.55);
    expect(speed.x).toBeCloseTo(60 / 0.05, 6);
    expect(speed.y).toBeCloseTo(-30 / 0.05, 6);
    // a pointer held still before letting go throws nothing; one flung hard is held to the fastest throw, its way kept
    expect(pointerSpeed(moves, 0.9)).toEqual({x: 0, y: 0});
    const hard = pointerSpeed([{x: 0, y: 0, at: 0}, {x: 300, y: -400, at: 0.01}], 0.01);
    expect(Math.hypot(hard.x, hard.y)).toBeCloseTo(GRAB.fastest, 6);
    expect(hard.x / hard.y).toBeCloseTo(-0.75, 6);
    // the throw carries that speed: its first frame moves the feet by it
    const thrown = thrownFrom({x: 400, y: 200}, speed, 0);
    expect(thrown).toMatchObject({x: 400, y: 200, vx: speed.x, speed: speed.y, thrown: true});
    const next = thrownFrame(thrown, FLOORS, ROOM, 16).airborne;
    expect(next.x - thrown.x).toBeCloseTo(speed.x * 0.016, 6);
    expect(next.y).toBeLessThan(thrown.y);
});

test("let go without a throw, it falls straight down from where it is let go to the nearest floor below: a bubble's top or the chat's floor", () => {
    // over the upper bubble, onto its top; let go in front of the upper bubble, below its top, onto the lower one; past both, onto the floor
    for (const [from, onto] of [[{x: 400, y: 200}, UPPER], [{x: 400, y: 350}, LOWER], [{x: 900, y: 200}, HOME], [{x: 200, y: 400}, HOME]]) {
        const {frames, landed, gone} = flown(thrownFrom(from, {x: 0, y: 0}, 0));
        const label = `${from.x},${from.y}`;
        expect(gone, label).toBe(false);
        expect(landed, label).toEqual({x: from.x, y: onto.top, posture: "stand", face: 0, view: null, on: onto.element});
        expect(onto, label).toBe(nearestBelow(from.x, from.y));
        for (const frame of frames) expect(frame.x, label).toBe(from.x);
    }
});

test("thrown hard, it flies tumbling, off the chat's sides, and falls to the nearest floor below where it comes down, not where it was let go", () => {
    for (const speed of [{x: 1200, y: -600}, {x: -900, y: -300}, {x: GRAB.fastest, y: 0}, {x: 400, y: 900}]) {
        const from = {x: 250, y: 250};
        const {frames, landed, gone} = flown(thrownFrom(from, speed, 0));
        const label = JSON.stringify(speed);
        expect(gone, label).toBe(false);
        const last = frames.at(-1);
        expect(landed.x, label).not.toBe(from.x);
        expect(landed.y, label).toBe(nearestBelow(landed.x, last.y).top);
        // it tumbles all the way, a good turn and more on a throw that flies up first
        const turned = Math.max(...frames.map((frame) => Math.abs(frame.spin)));
        expect(turned, label).toBeGreaterThan(speed.y < 0 ? 90 : 0);
        for (const frame of frames) {
            expect(frame.x, label).toBeGreaterThanOrEqual(ROOM.left);
            expect(frame.x, label).toBeLessThanOrEqual(ROOM.right);
        }
    }
});

test("thrown up hard, it flies past the chat's top and off the screen, and comes back down from above on its parachute to the floor", () => {
    const {frames, landed, gone} = flown(thrownFrom({x: 400, y: 250}, {x: 300, y: -GRAB.fastest}, 0));
    expect(gone).toBe(true);
    expect(landed).toBe(null);
    // nothing stopped it at the top: it rose on up to it and past
    const highest = frames.at(-1);
    expect(highest.y).toBeLessThanOrEqual(ROOM.top + 60);
    expect(highest.speed).toBeLessThan(0);
    // the way back is the parachute's from above the screen, as after the run up the bubbles (VoiceFigure goneOff, flyOn), onto the floor
    let back = chuteFrom(highest.x, ROOM.top - SIZE / 4, SKYWARD.chute * SIZE, 0);
    let came = null;
    for (let frame = 1; frame < 60 * 30 && !came; frame++) ({airborne: back, landed: came} = airborneFrame(back, FLOORS, (frame * 1000) / 60));
    expect(came.spot).toMatchObject({x: highest.x, y: HOME.top, posture: "stand"});
});
