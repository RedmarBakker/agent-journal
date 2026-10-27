// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, HEAD_TURN, LOOK_REACH, Posing, READING_BODY, drawnPose, lookToward} from "../src/figure/figure.js";
import {READING, gazeAfter, readingAt} from "../src/figure/reactions.js";
import {lookInFigure} from "../src/figure/looks.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const IDLE = CLIPS.find((clip) => clip.name === "idle");
const SIZE = 112;
const ORIGIN = {x: 400, y: 300};
const CENTER = {x: ORIGIN.x + SIZE / 2, y: ORIGIN.y + SIZE * 0.3};
const HEAD = {depth: LOOK_REACH * SIZE, above: 8, tip: {up: 25, down: 35}};
const degrees = THREE.MathUtils.radToDeg;
const rotationOf = (matrix) => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().extractRotation(matrix));
const yawOf = (matrix) => {
    const ahead = new THREE.Vector3(0, -1, 0).transformDirection(matrix);
    return degrees(Math.atan2(ahead.x, -ahead.y));
};
const wrapped = (angle) => degrees(Math.atan2(Math.sin(THREE.MathUtils.degToRad(angle)), Math.cos(THREE.MathUtils.degToRad(angle))));

// A line crossing behind the head, including the old atan2 branch cut on both sides of a side-facing seat.
const BOXES = [
    {left: 270, right: 640, top: 310, bottom: 390},
    {left: 120, right: 430, top: 320, bottom: 400},
    {left: 480, right: 820, top: 300, bottom: 380},
];

test("reading reaches both ends of each line and eases back onto the next without a position or velocity jump", () => {
    const box = BOXES[0];
    const scan = READING.sweep - READING.returnSeconds;
    const step = 1e-4;
    expect(readingAt(box, 0).x).toBe(box.left + READING.inset);
    expect(readingAt(box, scan).x).toBe(box.right - READING.inset);
    expect(readingAt(box, READING.sweep).x).toBe(box.left + READING.inset);
    expect(readingAt(box, READING.sweep).y).toBe(readingAt(box, 0).y + READING.line);
    for (const boundary of [scan, READING.sweep, 2 * READING.sweep, 3 * READING.sweep]) {
        const [before, at, after] = [boundary - step, boundary, boundary + step].map((time) => readingAt(box, time));
        expect(Math.hypot(after.x - before.x, after.y - before.y)).toBeLessThan(0.001);
        expect(Math.hypot(after.x - 2 * at.x + before.x, after.y - 2 * at.y + before.y) / step).toBeLessThan(0.02);
    }
    for (const tiny of [{left: 100, right: 112, top: 20, bottom: 30}, {left: 100, right: 100, top: 20, bottom: 20}]) {
        for (let time = 0; time < 5; time += 0.03) {
            const point = readingAt(tiny, time);
            expect(point.x).toBeGreaterThanOrEqual(tiny.left);
            expect(point.x).toBeLessThanOrEqual(tiny.right);
            expect(point.y).toBeGreaterThanOrEqual(tiny.top);
            expect(point.y).toBeLessThanOrEqual(tiny.bottom);
        }
    }
});

test.each(Object.keys(stances))("%s reads through yaw limits and line returns without a one-frame head or torso flip", (voice) => {
    for (const facing of [0, 90, 135, 180, 225, 270]) {
        for (const posture of ["stand", "sit"]) {
            for (const box of BOXES) {
                let gaze = {point: null, amount: 0, at: 1};
                let previous = null;
                for (let frame = 1; frame <= Math.ceil(READING.sweep * 3 * 60); frame++) {
                    const seconds = frame / 60;
                    gaze = gazeAfter(gaze, readingAt(box, seconds), CENTER, 1 + seconds * 1000, {...HEAD, facing}, 1);
                    const at = lookInFigure(gaze, ORIGIN, SIZE);
                    const {pose, turned} = drawnPose(RIG, stanceOf(voice), IDLE, 0, facing, {posture, at});
                    const moves = pose.moves(turned);
                    const current = {head: rotationOf(moves.get("head")), chest: rotationOf(moves.get("chest"))};
                    const label = `${voice} ${posture} ${facing}° frame ${frame}`;
                    if (previous && seconds > 0.6) {
                        expect(degrees(previous.head.angleTo(current.head)), label).toBeLessThan(5);
                        expect(degrees(previous.chest.angleTo(current.chest)), label).toBeLessThan(5);
                    }
                    const neck = wrapped(yawOf(pose.matrix("head")) - yawOf(pose.matrix("chest")));
                    expect(Math.abs(neck), label).toBeLessThanOrEqual(HEAD_TURN + 0.01);
                    previous = current;
                }
            }
        }
    }
});

test("the head leads while the shoulders follow, and reading leans back while leaving the seated legs planted", () => {
    const box = BOXES[0];
    const facing = 90;
    let gaze = {point: null, amount: 0, at: 1};
    let lag = 0;
    let turnedShoulders = 0;
    let leanedBack = 0;
    for (let frame = 1; frame < 240; frame++) {
        const seconds = frame / 60;
        gaze = gazeAfter(gaze, readingAt(box, seconds), CENTER, 1 + seconds * 1000, {...HEAD, facing}, 1);
        lag = Math.max(lag, Math.abs(gaze.point.readingYaw - gaze.point.readingFollow));
        const at = lookInFigure(gaze, ORIGIN, SIZE);
        const pose = new Posing(RIG, "sit");
        IDLE.pose(pose, stanceOf("butler"), 0);
        const feet = ["foot_l", "foot_r"].map((bone) => pose.matrix(bone).clone());
        lookToward(pose, at, facing);
        turnedShoulders = Math.max(turnedShoulders, Math.abs(yawOf(pose.matrix("chest"))));
        const forward = new THREE.Vector3(0, -1, 0).transformDirection(pose.matrix("chest"));
        leanedBack = Math.max(leanedBack, degrees(Math.asin(forward.z)));
        ["foot_l", "foot_r"].forEach((bone, index) => expect(pose.matrix(bone).elements).toEqual(feet[index].elements));
    }
    expect(lag).toBeGreaterThan(8);
    expect(turnedShoulders).toBeGreaterThan(25);
    expect(turnedShoulders).toBeLessThanOrEqual(READING_BODY.turn + 1);
    expect(leanedBack).toBeGreaterThan(1);
});

// Changing a seat's slant or crossing the signed facing boundary must rebase the same gaze, not restart it.
test("reading stays continuous while the body eases round and while a seated facing changes", () => {
    for (const posture of ["stand", "sit"]) {
        for (const initial of [0, 135, 175, 270]) {
            let gaze = {point: null, amount: 0, at: 1};
            let previous = null;
            for (let frame = 1; frame <= 360; frame++) {
                const seconds = frame / 60;
                const facing = wrapped(initial + 18 * Math.sin(seconds * 1.2));
                gaze = gazeAfter(gaze, readingAt(BOXES[0], seconds), CENTER, 1 + seconds * 1000, {...HEAD, facing}, 1);
                const {pose, turned} = drawnPose(RIG, stanceOf("butler"), IDLE, 0, facing, {posture, at: lookInFigure(gaze, ORIGIN, SIZE)});
                const moves = pose.moves(turned);
                const current = {head: rotationOf(moves.get("head")), chest: rotationOf(moves.get("chest"))};
                if (previous && seconds > 0.6) {
                    expect(degrees(previous.head.angleTo(current.head)), `${posture} ${initial}° frame ${frame}`).toBeLessThan(5);
                    expect(degrees(previous.chest.angleTo(current.chest)), `${posture} ${initial}° frame ${frame}`).toBeLessThan(5);
                }
                previous = current;
            }
        }
    }
});
