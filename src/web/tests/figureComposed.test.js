// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {CLIPS, COMPOSED, LEGS, Posing, turnsToViewer} = await import("../src/figure/figure.js");
const {choicesFor} = await import("../src/figure/pile.js");
const {COMPOSED_ALONG, composedSpot} = await import("../src/figure/perches.js");
const {GROUNDED, clipFor} = await import("../src/domain/figureState.js");
const {write} = await import("./figurePage.js");

const FIGURE = {size: 112, below: 0.05};
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// a chat with its compose box, the floor the figure stands on
function chat() {
    const thread = {...boxed({left: 200, top: 100, right: 900, bottom: 800}), querySelector: () => null};
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
    return home;
}

test("now and then, with nothing to do, the figure sits composed near the middle of the floor it stands on, facing the viewer", () => {
    // one of the idle stays, for the figure with nothing to do
    expect(choicesFor({moment: "roam", free: true}).some((entry) => entry.name === "composed")).toBe(true);
    expect(choicesFor({moment: "roam", free: false}).some((entry) => entry.name === "composed")).toBe(false);
    // on the compose box: at its middle, on its top, facing the viewer
    const home = chat();
    const spot = composedSpot(FIGURE, {x: 360, y: 600, on: home});
    expect(spot).toMatchObject({x: 500, y: 600, face: 0, posture: "composed", on: home});
    expect(clipFor({mode: GROUNDED, place: spot, state: "idle", doing: "idle"}, () => true).facing).toBe(0);
    // where it would hide words at the middle, a little to one side, never far from it
    write([{left: 492, right: 508, top: 520, bottom: 590}]);
    const aside = composedSpot(FIGURE, {x: 360, y: 600, on: home});
    expect([300 + 400 * COMPOSED_ALONG[1], 300 + 400 * COMPOSED_ALONG[2]].includes(aside.x)).toBe(true);
    // on no floor it stands on, no composed sit
    expect(composedSpot(FIGURE, {x: 360, y: 600, on: {}})).toBe(null);
});

test("sitting composed, both hands lie flat on the floor at its sides, beside the hips and not behind them, for every voice", () => {
    const idle = CLIPS.find((clip) => clip.name === "idle");
    expect(idle.postures.includes("composed")).toBe(true);
    for (const voice of Object.keys(stances)) {
        const pose = new Posing(RIG, "composed", 0);
        LEGS.composed.under(pose);
        idle.pose(pose, stanceOf(voice), 0);
        LEGS.composed.over(pose);
        const moves = pose.moves(0);
        const at = (name) => pose.head(name, moves.get(name));
        const hips = at("hips");
        for (const [side, sign] of [["l", 1], ["r", -1]]) {
            const hand = at(`hand_${side}`);
            expect(Math.abs(hand.z - COMPOSED.floor), `${voice} ${side} on the floor line`).toBeLessThan(0.2);
            expect(sign * (hand.x - hips.x), `${voice} ${side} at its side`).toBeGreaterThan(0.45);
            expect(Math.abs(hand.y - hips.y), `${voice} ${side} not behind`).toBeLessThan(0.3);
        }
        // upright, not leaning back as it does lounging
        const back = at("neck").sub(hips).normalize();
        expect(back.z, voice).toBeGreaterThan(Math.cos(THREE.MathUtils.degToRad(15)));
        // its knees up and its feet flat on the floor before it, never its legs straight out toward the viewer
        for (const side of ["l", "r"]) {
            const knee = at(`shin_${side}`);
            const foot = at(`foot_${side}`);
            expect(knee.z, `${voice} ${side} knee up`).toBeGreaterThan(at(`thigh_${side}`).z + 0.15);
            expect(knee.z, `${voice} ${side} knee over the foot`).toBeGreaterThan(foot.z + 0.25);
            expect(foot.y - hips.y, `${voice} ${side} foot near`).toBeGreaterThan(-0.9);
        }
    }
});

test("lounging, its legs straight out, the figure is only ever side-on: every lounge spot faces sideways and nothing turns it toward the viewer", async () => {
    const {seatAt} = await import("../src/figure/places.js");
    const {ledgeSpot} = await import("../src/figure/perches.js");
    const box = {left: 300, width: 400, top: 600};
    for (const side of ["left", "right"]) expect([90, 270].includes(seatAt(box, side, FIGURE).face), side).toBe(true);
    const home = chat();
    for (const along of [1 / 3, 1 / 2, 2 / 3]) {
        const spot = ledgeSpot(along, FIGURE, {on: home});
        expect(spot.posture).toBe("lounge");
        expect([90, 270].includes(spot.face), String(along)).toBe(true);
    }
    // whatever it plays there, a look, a beat facing the viewer or a wait turned to the compose box, it keeps its side-on facing
    const place = {...seatAt(box, "right", FIGURE), on: home};
    for (const scene of [{doing: "idle"}, {beat: {clip: "nod", facing: 0}}, {state: "waiting", composeFacing: 30}, {watching: "watch"}]) {
        expect(clipFor({mode: GROUNDED, place, state: "idle", doing: "idle", ...scene}, () => true).facing, JSON.stringify(scene)).toBe(place.face);
    }
    // and its picture never turns to the viewer for a look or a lit visor, nor its head to look at anything
    expect(turnsToViewer("lounge")).toBe(false);
    expect(turnsToViewer("composed")).toBe(true);
    expect(turnsToViewer("stand")).toBe(true);
});
