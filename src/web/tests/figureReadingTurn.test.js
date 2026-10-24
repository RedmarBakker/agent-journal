// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, GLASS, HEAD_TURN, Posing, lookToward} = await import("../src/figure/figure.js");
const {READING, readingAt, readingFacing} = await import("../src/figure/reactions.js");
const {GROUNDED, clipFor} = await import("../src/domain/figureState.js");
const {FRAMED} = await import("../src/figure/frame.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const radians = THREE.MathUtils.degToRad;
const SIZE = 112;
const has = () => true;

// a figure with the middle of its picture at page x 500, and bubbles to its right, to its left and over its head
const X = 500;
const RIGHT = {left: 600, right: 900, top: 300, bottom: 360};
const LEFT = {left: 120, right: 420, top: 300, bottom: 360};
const OVER = {left: 440, right: 560, top: 300, bottom: 360};

// what the figure standing at rest plays and the way it faces, in `state`, reading at `facing` or nothing
const shown = (readingFacing, state = "idle", place = {posture: "stand", face: 0}, doing = "idle") =>
    clipFor({mode: GROUNDED, place, state, doing, doingFacing: doing === "push" ? 90 : 0, composeFacing: 30, readingFacing}, has);

test("reading a bubble to its left or right the figure turns its whole body toward it, and back once it has read it", () => {
    expect(readingFacing(RIGHT, X, SIZE)).toBe(READING.turn);
    expect(readingFacing(LEFT, X, SIZE)).toBe(-READING.turn);
    expect(readingFacing(OVER, X, SIZE), "a bubble over its head is read facing ahead").toBe(0);
    // standing at rest, waiting on the user, or doing what it does while the agent works, it faces the bubble it reads
    for (const state of ["idle", "waiting", "testing"]) {
        expect(shown(readingFacing(RIGHT, X, SIZE), state).facing, `${state} right`).toBe(READING.turn);
        expect(shown(readingFacing(LEFT, X, SIZE), state).facing, `${state} left`).toBe(-READING.turn);
    }
    // read, it faces as it did before: the viewer, or the compose box while it waits
    expect(shown(null).facing).toBe(0);
    expect(shown(null, "waiting").facing).toBe(30);
    // seated it faces as its seat does, and pushing a parcel it faces the parcel
    expect(shown(READING.turn, "idle", {posture: "sit", face: 270}).facing).toBe(270);
    expect(shown(-READING.turn, "testing", {posture: "stand", face: 0}, "push").facing).toBe(90);
});

test("turned to the bubble, its head follows the lines without turning the body further, and the glass held up to it stays on the line to the text", () => {
    // where the look is on the bubble as it reads, as a share of the figure's picture, the picture's middle at X and its top at page y 290, the bubble at its head
    const share = (point) => ({x: (point.x - (X - SIZE / 2)) / SIZE, y: (point.y - 290) / SIZE});
    for (const [box, facing] of [[RIGHT, READING.turn], [LEFT, -READING.turn]]) {
        for (let t = 0; t < READING.sweep * 3; t += 0.2) {
            const pose = new Posing(RIG, "stand", 0);
            CLIPS.find((each) => each.name === "idle").pose(pose, stanceOf("butler"), 0);
            expect(lookToward(pose, share(readingAt(box, t)), facing), `${facing} at ${t.toFixed(1)}`).toBe(0);
        }
    }
    expect(HEAD_TURN).toBeLessThan(READING.turn + 90);
    // the glass to a bubble out to its right and its left with the body turned to it: the lens on the line from the eyes to the text, the
    // text turned into the body's own way as the body is turned
    const clip = CLIPS.find((each) => each.name === "glass_bubble");
    for (const voice of Object.keys(stances)) {
        for (const [at, facing] of [[{x: 1.1, y: 0.25}, READING.turn], [{x: -0.1, y: 0.3}, -READING.turn]]) {
            for (let frame = 0; frame < clip.frames; frame += 8) {
                const pose = new Posing(RIG, "stand", 0);
                pose.at = at;
                pose.facing = facing;
                clip.pose(pose, stanceOf(voice), frame / clip.frames);
                const moves = pose.moves(0);
                const glass = pose.props.get("magnifying_glass");
                const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(RIG.eyes.length).applyMatrix4(moves.get("head"));
                const turned = new THREE.Matrix4().extractRotation(moves.get(glass.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(radians(glass.turn.x), radians(glass.turn.y), radians(glass.turn.z), "ZYX")));
                const lens = glass.at.clone().applyMatrix4(moves.get(glass.bone)).addScaledVector(new THREE.Vector3(0, 0, 1).transformDirection(turned), (GLASS.handle / 2 + GLASS.radius) * glass.size);
                const text = new THREE.Vector3((at.x - 0.5) * FRAMED.height, 0.3, FRAMED.middle + (0.5 - at.y) * FRAMED.height).applyAxisAngle(new THREE.Vector3(0, 0, 1), radians(-facing));
                const line = text.clone().sub(eyes);
                const along = lens.clone().sub(eyes).dot(line) / line.lengthSq();
                const off = lens.clone().sub(eyes.clone().addScaledVector(line, along)).length();
                const label = `${voice} facing ${facing} frame ${frame}`;
                // held in the hand on the text's side it is out between the eyes and the text; a voice whose hand on that side is busy
                // reaches across with the other and holds it up at its visor, as it does facing ahead
                const across = Math.sign(text.x) !== (glass.bone === "hand_l" ? 1 : -1);
                expect(along, label).toBeGreaterThan(across ? -0.02 : 0.1);
                expect(along, label).toBeLessThan(0.85);
                expect(off, label).toBeLessThan(0.3);
            }
        }
    }
});
