// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {BAR, PROGRESS, WATCH, watchLook, watchSpot} = await import("../src/figure/places.js");
const {eagerSpot, targetFor} = await import("../src/figure/perches.js");
const {CLIPS, HEAD_TIP, HEAD_TURN, LOOK_REACH, Posing, eyesAboveOf, headPivotOf, lookToward} = await import("../src/figure/figure.js");
const {LOOK_TURN_SPEED, eagerFor, gazeAfter} = await import("../src/figure/reactions.js");
const {boxAt} = await import("../src/figure/places.js");
const {clipFor} = await import("../src/domain/figureState.js");

const FIGURE = {size: 112, below: 0.05};
const HANDS = ["l", "r"];
const {rig} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};

// a chat with a card docked over its compose box, its progress bar running to its end at the right, 680 across the page
function chat(running = true) {
    const fill = boxed({left: 320, right: 500, top: 560, bottom: 566});
    const track = {...boxed({left: 320, right: 680, top: 560, bottom: 566}), querySelector: (selector) => (selector === PROGRESS && running ? fill : null)};
    const bars = {...boxed({left: 300, right: 700, top: 540, bottom: 600}), querySelector: (selector) => (selector === BAR ? track : null)};
    const scroll = {...boxed({left: 200, top: 100, right: 900, bottom: 540}), querySelectorAll: () => []};
    const thread = {...boxed({left: 200, top: 100, right: 900, bottom: 800}), querySelector: (selector) => (selector === ".thread-scroll" ? scroll : selector === "[data-figure-docked-bars]" ? bars : null)};
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
    return {bars, home};
}

test("watching a docked bar run, and anticipating its end, the figure stands on the bars a little left of the bar's end, never over it", () => {
    const {bars, home} = chat();
    const spot = watchSpot(FIGURE);
    // on top of the bars, left of the bar's end at 680 by the margin, so the bar runs on past it
    expect(spot).toMatchObject({y: 540, on: bars, posture: "stand"});
    expect(680 - spot.x, "stood back from the bar's end").toBeCloseTo(WATCH.back, 5);
    expect(WATCH.back, "enough space to look down without reaching the neck limit").toBeGreaterThan(FIGURE.size * 1.25);
    // anticipating the end it goes to that same spot, from the compose box under the bars, and stays once there
    expect(eagerSpot({x: 420, y: 600, on: home}, FIGURE)).toEqual(spot);
    expect(eagerSpot(spot, FIGURE)).toBe(null);
    // resting at home while the bar runs, it rests at that spot too
    const resting = {state: "idle", counts: {question: 0, waiting: 0, suggestion: 0}, now: 100, near: {x: 650, y: 540, posture: "stand", on: bars}, figure: FIGURE, hands: HANDS, stay: {where: "rest", until: 500}};
    expect(targetFor(resting).spot).toMatchObject({x: spot.x, y: 540, on: bars});
    // with no bar running there is no such spot
    chat(false);
    expect(watchSpot(FIGURE)).toBe(null);
});

test("it looks along the bar at its leading edge, never straight down, its head turned back to the screen from both in front of the mark and on top", () => {
    const mark = {left: 300, right: 700, top: 540, bottom: 600};
    const feet = {x: 618, y: 540};
    // wherever the leading edge is, the look is at least WATCH along of the picture off to one side of where it stands
    for (const x of [330, 480, 600, 618, 630, 670]) {
        const look = watchLook({x, y: 563}, feet, mark, FIGURE);
        expect(Math.abs(look.x - feet.x), `${x}`).toBeGreaterThanOrEqual(WATCH.along * FIGURE.size - 1e-9);
        expect(look.y).toBe(563);
    }
    // an edge well to one side is looked at where it is
    expect(watchLook({x: 400, y: 563}, feet, mark, FIGURE).x).toBe(400);
    // the bar stays on the screen behind it whether its feet are on top of the mark or below it
    expect(watchLook({x: 400, y: 563}, feet, mark, FIGURE).behind).toBe(true);
    expect(watchLook({x: 400, y: 563}, {x: 618, y: 640}, mark, FIGURE).behind).toBe(true);
    // the head: a look in front turns the head alone, a look behind turns the body round after it, its back to the viewer
    const turn = (behind) => {
        const pose = new Posing(RIG, "stand", 0);
        return lookToward(pose, {x: 0.62, y: 0.25, behind}, 0);
    };
    expect(Math.abs(turn(false))).toBeLessThan(5);
    // the head goes round as far as it turns and the body the rest, well past a quarter turn from the viewer, its back to them
    expect(Math.abs(turn(true)) + HEAD_TURN).toBeGreaterThan(135);
});

test("once eager for a run's end nothing calls it off but that end: the roll, a beat, the UFO and the crane all wait, and it goes nowhere else", () => {
    const eager = {run: 100, on: true};
    const near = (share) => ({bar: {}, share, ended: "", began: 100});
    // kept through every roll until the run ends
    for (const roll of [0, 0.5, 0.999]) expect(eagerFor(near(0.98), eager, () => roll, 150).eager, `${roll}`).toEqual(eager);
    // and over the moment the run ends
    expect(eagerFor({...near(1), ended: "good"}, eager, () => 0, 151).eager.on).toBe(false);
    // the eager wait is drawn over a beat waiting to play and over the UFO or the crane it would watch
    const scene = {place: {posture: "stand"}, eager: true, watching: "watch", beat: {clip: "joy", facing: 0}, state: "running", doing: "think"};
    expect(clipFor(scene, () => true).clip).toBe("eager");
    // standing at its spot it is sent nowhere
    chat();
    expect(eagerSpot(watchSpot(FIGURE), FIGURE)).toBe(null);
});

// the figure standing idle at the picture's top-left `corner` on the page, its head looking at `point` on the page `amount` of the way, as
// the page draws it (chat/VoiceFigure.vue lookingAt): where its head faces, and how far down and round it is turned, in degrees
function headLooking(corner, point, amount = 1) {
    const pose = new Posing(RIG, "stand", 0);
    CLIPS.find((clip) => clip.name === "idle").pose(pose, {voice: "butler", level: new Set(), busy: new Set(), carried: new Set(), free: new Set(HANDS), tablet: new Set(), shield: new Set()}, 0);
    if (point && amount) lookToward(pose, {x: (point.x - corner.x) / FIGURE.size, y: (point.y - corner.y) / FIGURE.size, amount});
    const faces = new THREE.Vector3(0, -1, 0).transformDirection(pose.moves(0).get("head"));
    return {faces, down: THREE.MathUtils.radToDeg(Math.asin(-faces.z)), round: THREE.MathUtils.radToDeg(Math.atan2(faces.x, -faces.y))};
}

// the page's picture corner for a figure standing on `spot`, and where on the page its head turns about, as the page has it
const cornerOf = (spot) => {
    const box = boxAt(spot, FIGURE);
    return {x: box.left, y: box.top};
};
const headOf = (corner) => ({x: corner.x + FIGURE.size / 2, y: corner.y + FIGURE.size * headPivotOf({rig: RIG})});

test("walking onto its mark as a bar comes into view, the head turns to the bar smoothly, never faster than the turn speed and never past the neck's reach", () => {
    const {bars} = chat();
    const spot = watchSpot(FIGURE);
    const looks = {depth: LOOK_REACH * FIGURE.size, above: eyesAboveOf({rig: RIG}) * FIGURE.size, tip: HEAD_TIP};
    const frame = 1000 / 60;
    let gaze = {point: null, toward: null, amount: 0, at: 0};
    let before = null;
    let steepest = 0;
    for (let step = 0; step < 120; step++) {
        const now = 1000 + step * frame;
        // it walks in from 150 pixels left of its spot over the first second, the bar in view from the fifth frame
        const feet = {x: spot.x - 150 * Math.max(1 - step / 60, 0), y: 540};
        const corner = cornerOf({...spot, x: feet.x});
        const edge = step >= 5 ? watchLook({x: 500, y: 563}, feet, bars.getBoundingClientRect(), FIGURE) : null;
        gaze = gazeAfter(gaze, edge, headOf(corner), now, looks);
        const eased = gaze.amount * gaze.amount * (3 - 2 * gaze.amount);
        const head = headLooking(corner, gaze.point, eased);
        // to a hundredth: the head's pivot moves a little with the idle breath, which the page does not follow
        if (before) expect(head.faces.angleTo(before.faces), `frame ${step} turns no faster than the limit`).toBeLessThanOrEqual(((LOOK_TURN_SPEED * frame) / 1000) * 1.01);
        expect(head.down, `frame ${step} tips no further down than the neck goes`).toBeLessThanOrEqual(HEAD_TIP.down + 1e-6);
        expect(Math.abs(head.round), `frame ${step} turns no further round than the neck goes`).toBeLessThanOrEqual(HEAD_TURN + 1e-6);
        steepest = Math.max(steepest, head.down);
        before = head;
    }
    expect(gaze.amount, "in the end it looks at the bar").toBe(1);
    expect(steepest, "looking down at it").toBeGreaterThan(5);
});

test("anticipating a run's end it stands back at least WATCH.back from the bar's end, and looks down along the bar at a gentle angle", () => {
    const {bars} = chat();
    const spot = watchSpot(FIGURE);
    expect(680 - spot.x).toBeGreaterThanOrEqual(WATCH.back - 1e-9);
    expect(eagerSpot({x: 420, y: 600, on: bars}, FIGURE)).toEqual(spot);
    const lookFrom = (x) => {
        const feet = {x, y: 540};
        return headLooking(cornerOf({...spot, x}), watchLook({x: 670, y: 563}, feet, bars.getBoundingClientRect(), FIGURE)).down;
    };
    const back = lookFrom(spot.x);
    const close = lookFrom(680 - 0.55 * FIGURE.size);
    expect(back, "down at the bar").toBeGreaterThan(0);
    expect(back, "more gently than from close by the bar's end").toBeLessThan(close);
    expect(back, "inside the neck's tip").toBeLessThanOrEqual(HEAD_TIP.down);
});
