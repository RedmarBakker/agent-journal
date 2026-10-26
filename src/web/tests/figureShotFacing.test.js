// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {ACTS, bugShotScene} from "../src/figure/acts.js";
import {CLIPS, RIFLE_PARTS, blendedMoves, drawnPose, rifleTarget} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "bug_shot");
const cases = [
    {wall: "left", facing: 270, target: {x: -1.4, y: 0.2, back: 0}, side: -1},
    {wall: "right", facing: 90, target: {x: 2.2, y: 0.35, back: 0}, side: 1},
    {wall: "top", facing: 180, target: {x: 0.3, y: -1.6, back: 1}},
];

function sample(voice, target, facing, u = 0.36) {
    const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip, u * clip.frames, facing, {target});
    const moves = pose.moves(turned);
    const held = pose.props.get("rifle");
    const rotation = new THREE.Matrix4().extractRotation(moves.get(held.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(...["x", "y", "z"].map((axis) => THREE.MathUtils.degToRad(held.turn[axis] || 0)), "ZYX")));
    const origin = held.at.clone().applyMatrix4(moves.get(held.bone));
    return {pose, moves, origin, rotation};
}

test("all voices turn from their feet into profile for side walls and show their back toward the top wall", () => {
    for (const voice of Object.keys(stances)) {
        for (const {wall, facing, target, side} of cases) {
            const {moves} = sample(voice, target, facing);
            const forward = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("root"));
            if (side) {
                expect(forward.x * side, `${voice} faces ${wall}`).toBeGreaterThan(0.98);
                expect(Math.abs(forward.y), `${voice} side profile`).toBeLessThan(0.12);
            } else expect(forward.y, `${voice} faces the screen`).toBeGreaterThan(0.9);
            for (const bone of ["hips", "foot_l", "foot_r"]) {
                const direction = new THREE.Vector3(0, -1, 0).transformDirection(moves.get(bone));
                expect(direction.dot(forward), `${voice} ${bone} turns with the body`).toBeGreaterThan(0.98);
            }
        }
    }
});

test("the stock meets the shooting shoulder and the eyes follow the barrel toward each bug", () => {
    const butt = (RIFLE_PARTS.stock[0][0] - RIFLE_PARTS.stock[1][0] / 2) * RIFLE_PARTS.scale;
    for (const voice of Object.keys(stances)) {
        for (const {wall, facing, target} of cases) {
            const {pose, moves, origin, rotation} = sample(voice, target, facing);
            const stock = new THREE.Vector3(butt, 0, 0).applyMatrix4(rotation).add(origin);
            const shoulder = RIG.heads.get("upper_arm_r").clone().applyMatrix4(moves.get("upper_arm_r"));
            expect(stock.distanceTo(shoulder), `${voice} ${wall} stock against the shoulder`).toBeLessThan(0.27);
            const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(RIG.eyes.length).applyMatrix4(moves.get("head"));
            const sight = rifleTarget(target).sub(eyes).normalize();
            const gaze = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("head"));
            expect(THREE.MathUtils.radToDeg(gaze.angleTo(sight)), `${voice} ${wall} looks along the shot`).toBeLessThan(8);
            expect(pose.headContact, "ambient looks cannot turn the aiming head to the viewer").toBe(1);
        }
    }
});

test("the target moves continuously onto the screen plane between a side-wall and a top-wall bug", () => {
    const bugs = [{wall: "left", along: 0.3, way: 0}, {wall: "top", along: 0.55, way: 0}];
    const world = {left: 0, right: 900, top: 0, bottom: 700};
    const repeat = (ACTS.bug_shot.turn[1] - ACTS.bug_shot.turn[0]) * ACTS.bug_shot.frames;
    const from = ACTS.bug_shot.aim[0] * ACTS.bug_shot.frames + repeat;
    const to = ACTS.bug_shot.aim[1] * ACTS.bug_shot.frames + repeat;
    expect(bugShotScene(bugs, world, from).target.back).toBe(0);
    expect(bugShotScene(bugs, world, (from + to) / 2).target.back).toBeCloseTo(0.5);
    expect(bugShotScene(bugs, world, to).target.back).toBe(1);
});

// VoiceFigure chooses the first wall's base facing before starting the draw; FigurePlayer blends into that facing.
test("a left-wall first shot enters through the short left turn instead of a full clockwise pirouette", () => {
    const target = cases[0].target;
    const idle = CLIPS.find((each) => each.name === "idle");
    for (const voice of Object.keys(stances)) {
        const rest = drawnPose(RIG, stanceOf(voice), idle, 0, 0).pose.moves(0);
        const first = drawnPose(RIG, stanceOf(voice), clip, 0, 270, {target});
        let previous = rest;
        for (let step = 0; step <= 45; step++) {
            const {moves} = blendedMoves(RIG, first.pose, first.turned, {from: rest, previous, k: step / 45});
            const direction = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("root"));
            const yaw = THREE.MathUtils.radToDeg(Math.atan2(direction.x, -direction.y));
            expect(yaw, `${voice} turns left during entry`).toBeLessThanOrEqual(1e-6);
            expect(yaw, `${voice} does not go around the back first`).toBeGreaterThanOrEqual(-90.000001);
            previous = moves;
        }
        for (let step = 0; step <= 30; step++) {
            const shot = drawnPose(RIG, stanceOf(voice), clip, clip.frames * ACTS.bug_shot.draw[1] * step / 30, 270, {target});
            const moves = shot.pose.moves(shot.turned);
            const direction = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("root"));
            expect(direction.x, `${voice} keeps the left wall during the draw`).toBeLessThan(-0.98);
        }
    }
});
