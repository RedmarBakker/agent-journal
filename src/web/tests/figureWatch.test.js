// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {BAR, PROGRESS, WATCH, watchLook, watchSpot} = await import("../src/figure/places.js");
const {eagerSpot, targetFor} = await import("../src/figure/perches.js");
const {HEAD_TURN, Posing, lookToward} = await import("../src/figure/figure.js");
const {eagerFor} = await import("../src/figure/reactions.js");
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
    expect(680 - spot.x).toBeCloseTo(WATCH.aside * FIGURE.size, 5);
    expect(680 - spot.x).toBeGreaterThan(FIGURE.size / 2);
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

test("it looks along the bar at its leading edge, never straight down, its head turned to the mark from in front of it and down at it facing the viewer from on top", () => {
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
    // on top of the mark it looks down at it facing the viewer; below it, in front of it, it turns to it on the page behind
    expect(watchLook({x: 400, y: 563}, feet, mark, FIGURE).behind).toBe(false);
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
    expect(eagerFor({...near(1), ended: "good"}, eager, () => 0, 151).eager.on).toBe(false);
    // the eager wait is drawn over a beat waiting to play and over the UFO or the crane it would watch
    const scene = {place: {posture: "stand"}, eager: true, watching: "watch", beat: {clip: "joy", facing: 0}, state: "running", doing: "think"};
    expect(clipFor(scene, () => true).clip).toBe("eager");
    // standing at its spot it is sent nowhere
    chat();
    expect(eagerSpot(watchSpot(FIGURE), FIGURE)).toBe(null);
});
