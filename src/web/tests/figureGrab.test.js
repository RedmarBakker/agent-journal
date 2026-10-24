import {expect, test} from "vitest";

const {GRAB, headTiltFor, onHead, pointerSpeed, resumedClock, thrownFrame, thrownFrom} = await import("../src/figure/grab.js");
const {CLIPS} = await import("../src/figure/figure.js");
const {SKYWARD} = await import("../src/figure/skyward.js");
const {PICTURES, WHOA_SPOT, litPixels} = await import("../src/figure/visorPixels.js");

const SIZE = 112;
// the feet may go anywhere across a chat 1000 pixels wide, from a line 100 pixels down to the compose box's top at 700
const ROOM = {left: 56, right: 944, top: 100, bottom: 700};
// the perch it was lifted from: the compose box's top
const PERCH = {x: 400, y: 700, posture: "stand", face: 0, view: null, on: null};

// the throw flown at 60 frames a second from its first frame at 0 until it lands or is lost, with every frame it passed through
function flown(thrown, perch = PERCH) {
    const frames = [thrown];
    for (let frame = 1; frame < 60 * 30; frame++) {
        const next = thrownFrame(frames.at(-1), perch, ROOM, SIZE, (frame * 1000) / 60);
        if (!next.airborne || next.lost) return {frames, ...next};
        frames.push(next.airborne);
    }
    return {frames, landed: null, lost: false};
}

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
    const face = {eyed: true, eyes: 1.5, shift: [0, 0], tint: null, hearts: 0, stars: 0, squeezed: 0, dozing: 0, sign: null, ticker: null};
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
    const thrown = thrownFrom({x: 400, y: 500}, speed, 0);
    expect(thrown).toMatchObject({x: 400, y: 500, vx: speed.x, speed: speed.y, chute: false, thrown: true});
    const next = thrownFrame(thrown, PERCH, ROOM, SIZE, 16).airborne;
    expect(next.x - thrown.x).toBeCloseTo(speed.x * 0.016, 6);
    expect(next.y).toBeLessThan(thrown.y);
});

test("thrown, it tumbles, then its parachute opens and floats it back down onto the perch it was lifted from, never out of its world", () => {
    for (const speed of [{x: 1200, y: -600}, {x: -900, y: -1500}, {x: 0, y: 0}, {x: GRAB.fastest, y: 0}]) {
        const {frames, landed, lost} = flown(thrownFrom({x: 400, y: 450}, speed, 0));
        const label = JSON.stringify(speed);
        expect(lost, label).toBe(false);
        expect(landed, label).toBe(PERCH);
        // it tumbles before the parachute opens, and is righted under it by the time it lands
        const opened = frames.findIndex((frame) => frame.chute);
        expect(opened, label).toBeGreaterThan(0);
        if (speed.x) expect(Math.max(...frames.slice(0, opened).map((frame) => Math.abs(frame.spin))), label).toBeGreaterThan(90);
        expect(Math.abs(frames.at(-1).spin), label).toBeLessThan(5);
        // under the canopy it sinks no faster than the parachute lets it and never rises
        for (const [index, frame] of frames.slice(opened).entries()) {
            expect(frame.speed, `${label} ${index}`).toBeLessThanOrEqual(SKYWARD.chute * SIZE + 1e-9);
            if (index) expect(frame.y, `${label} ${index}`).toBeGreaterThanOrEqual(frames[opened + index - 1].y);
        }
        for (const frame of frames) {
            expect(frame.x, label).toBeGreaterThanOrEqual(ROOM.left);
            expect(frame.x, label).toBeLessThanOrEqual(ROOM.right);
            expect(frame.y, label).toBeGreaterThanOrEqual(ROOM.top);
            expect(frame.y, label).toBeLessThanOrEqual(ROOM.bottom);
        }
        // the last frame in the air is over the perch, on its way down onto it
        expect(Math.abs(frames.at(-1).x - PERCH.x), label).toBeLessThan(SIZE);
    }
    // a perch up on a bubble is come back to just the same
    const bubble = {...PERCH, x: 700, y: 300};
    expect(flown(thrownFrom({x: 300, y: 200}, {x: 600, y: -300}, 0), bubble).landed).toBe(bubble);
    // thrown down from just above it the parachute catches it before it passes the perch; let go below it, thrown down, the parachute
    // opens below it: lost, to come down to whatever is under it
    expect(flown(thrownFrom({x: 300, y: 260}, {x: 0, y: 900}, 0), bubble).landed).toBe(bubble);
    expect(flown(thrownFrom({x: 300, y: 400}, {x: 0, y: 900}, 0), bubble).lost).toBe(true);
});
