// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, drawnPose} from "../src/figure/figure.js";
import {blendMoves} from "../src/figure/blend.js";
import {GAIT, strideAtDistance} from "../src/figure/gait.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stance = Object.fromEntries(Object.entries(stances.butler).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = (name) => CLIPS.find((each) => each.name === name);
const at = (pose, name) => pose.head(name, pose.matrix(name));

test("a late parent turn carries an already posed chest, head and arms without separating their joints", () => {
    const pose = new Posing(RIG);
    clip("idle").pose(pose, stance, 0.3);
    pose.turn("spine", {x: 24, y: 8, z: -12});
    for (const name of ["chest", "neck", "head", "upper_arm_l", "upper_arm_r", "forearm_l", "forearm_r", "hand_l", "hand_r"]) {
        const jointFromParent = pose.head(name, pose.standing(name));
        expect(at(pose, name).distanceTo(jointFromParent), name).toBeLessThan(1e-7);
    }
});

test("moving the hips after a pose carries every authored body part by the same displacement", () => {
    const pose = new Posing(RIG);
    clip("ponder").pose(pose, stance, 0.4);
    const before = new Map(RIG.order.map((name) => [name, at(pose, name)]));
    const offset = new THREE.Vector3(0.12, -0.04, -0.35);
    pose.lift("root", {x: offset.x, y: offset.y, z: offset.z});
    for (const name of RIG.order) expect(at(pose, name).sub(before.get(name)).distanceTo(offset), name).toBeLessThan(1e-7);
});

test("a transition preserves a closed grip and interpolates its scale instead of opening the fist for one frame", () => {
    const open = new Posing(RIG);
    clip("idle").pose(open, stance, 0);
    const closed = new Posing(RIG);
    clip("idle").pose(closed, stance, 0);
    closed.clench("r", 0.62);
    const from = closed.moves(0), to = open.moves(0);
    const scale = (matrix) => new THREE.Vector3().setFromMatrixScale(matrix);
    expect(scale(blendMoves(RIG, from, to, 0).moves.get("hand_r")).distanceTo(scale(from.get("hand_r")))).toBeLessThan(1e-7);
    const middle = scale(blendMoves(RIG, from, to, 0.5).moves.get("hand_r"));
    expect(middle.distanceTo(scale(from.get("hand_r")))).toBeGreaterThan(0.1);
    expect(middle.distanceTo(scale(to.get("hand_r")))).toBeGreaterThan(0.1);
    expect(blendMoves(RIG, from, to, 1, to).settled).toBe(true);
});

test("walking soles stay planted on the page during support, at different canvas sizes and walking speeds", () => {
    for (const size of [112, 160, 224]) {
        for (const [side, phases] of [["l", [0.1, 0.25, 0.45]], ["r", [0.6, 0.75, 0.95]]]) {
            const points = phases.map((phase) => {
                const distance = phase * GAIT.length * size / 5.4;
                const cycle = strideAtDistance(distance, size);
                const {pose} = drawnPose(RIG, stance, clip("walk"), cycle * clip("walk").frames, 90);
                const foot = pose.head(`foot_${side}`, pose.moves(90).get(`foot_${side}`));
                expect(foot.z).toBeCloseTo(RIG.heads.get(`foot_${side}`).z, 6);
                return foot.x * size / 5.4 + distance;
            });
            expect(Math.max(...points) - Math.min(...points), `${side} at ${size}px`).toBeLessThan(1e-5);
        }
    }
});

test("the held rope-swing loop joins its head and shoulders continuously", () => {
    const swing = clip("rope_swing");
    const first = drawnPose(RIG, stance, swing, swing.intro + 1e-6, 0, {posture: "sit"}).pose;
    const last = drawnPose(RIG, stance, swing, swing.frames - swing.outro - 1e-6, 0, {posture: "sit"}).pose;
    for (const name of ["head", "chest", "hand_l", "hand_r", "foot_l", "foot_r"]) {
        expect(at(first, name).distanceTo(at(last, name)), name).toBeLessThan(1e-5);
    }
});

test("short head gestures finish facing their initial direction", () => {
    for (const name of ["nod", "shake"]) {
        const each = clip(name);
        const first = drawnPose(RIG, stance, each, 0, 0).pose;
        const last = drawnPose(RIG, stance, each, each.frames - 1, 0).pose;
        const before = new THREE.Quaternion().setFromRotationMatrix(first.matrix("head"));
        const after = new THREE.Quaternion().setFromRotationMatrix(last.matrix("head"));
        expect(before.angleTo(after), name).toBeLessThan(1e-7);
    }
});
