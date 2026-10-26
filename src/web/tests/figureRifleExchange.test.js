// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, LOOK_DEPTH, RIFLE, RIFLE_HOLD, RIFLE_PARTS, drawnPose} from "../src/figure/figure.js";
import {jointAngles} from "../src/figure/blend.js";
import {FRAMED} from "../src/figure/frame.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((entry) => entry.name === "bug_shot");

function sample(voice, u, target, facing = 0) {
    const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip, u * clip.frames, facing, {target});
    const moves = pose.moves(turned);
    const rifle = pose.props.get("rifle");
    const origin = rifle.at.clone().applyMatrix4(moves.get(rifle.bone));
    const rotation = new THREE.Matrix4().extractRotation(moves.get(rifle.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(...["x", "y", "z"].map((axis) => THREE.MathUtils.degToRad(rifle.turn[axis] || 0)), "ZYX")));
    return {pose, moves, rifle, origin, rotation};
}

function noJump(voice, u, target, axis, facing = 0) {
    const before = sample(voice, u, {...target, [axis]: target[axis] - 1e-7}, facing);
    const after = sample(voice, u, {...target, [axis]: target[axis] + 1e-7}, facing);
    for (const [bone, angle] of jointAngles(RIG, before.moves, after.moves)) {
        expect(angle, `${voice} ${bone} at ${u}`).toBeLessThan(0.0001);
        const a = RIG.heads.get(bone).clone().applyMatrix4(before.moves.get(bone));
        const b = RIG.heads.get(bone).clone().applyMatrix4(after.moves.get(bone));
        expect(a.distanceTo(b), `${voice} ${bone} stays joined`).toBeLessThan(0.0001);
    }
    expect(before.origin.distanceTo(after.origin), `${voice} rifle handoff`).toBeLessThan(0.0001);
    const a = new THREE.Quaternion().setFromRotationMatrix(before.rotation);
    const b = new THREE.Quaternion().setFromRotationMatrix(after.rotation);
    expect(a.angleTo(b), `${voice} barrel turn`).toBeLessThan(0.0001);
}

test("the rifle exchanges hands continuously through the centre and steep upward aim thresholds", () => {
    const across = [-3, 0, 3].map((x) => ({target: {x: 0.5 + x / FRAMED.height, y: 0.275}, axis: "x"}));
    const upward = [-5, -1, -0.1].flatMap((x) => [-65, -60, -55].map((down) => ({
        target: {x: 0.5 + x / FRAMED.height, y: 0.5 - (RIFLE.grip[2] + Math.tan(THREE.MathUtils.degToRad(-down)) * Math.hypot(x, LOOK_DEPTH) - FRAMED.middle) / FRAMED.height},
        axis: "y",
    })));
    for (const voice of Object.keys(stances)) {
        for (const u of [0.11, 0.165, 0.36, 0.765]) {
            for (const {target, axis} of [...across, ...upward]) noJump(voice, u, target, axis);
            for (const facing of [-35, 35]) {
                const x = 0.5 - LOOK_DEPTH * Math.tan(THREE.MathUtils.degToRad(facing)) / FRAMED.height;
                noJump(voice, u, {x, y: 0.275}, "x", facing);
            }
        }
    }
});

test("a dense target sweep has no interior wrist or elbow rotation flips during the exchange", () => {
    for (const voice of Object.keys(stances)) {
        for (const u of [0.165, 0.36, 0.765]) {
            let before;
            let largest = 0;
            for (let step = 0; step <= 480; step++) {
                const after = sample(voice, u, {x: -0.1 + step / 400, y: 0.275});
                if (before) {
                    for (const angle of jointAngles(RIG, before.moves, after.moves).values()) largest = Math.max(largest, angle);
                    expect(before.origin.distanceTo(after.origin), `${voice} rifle ${u} ${step}`).toBeLessThan(0.02);
                }
                before = after;
            }
            expect(largest, `${voice} ${u} maximum adjacent rotation`).toBeLessThan(0.15);
        }
    }
});

test("both palms stay beside the receiver and handguard while the barrel remains on the target", () => {
    const front = (RIFLE_PARTS.handguard[0][0] + RIFLE_PARTS.handguard[1][0] / 2) * RIFLE_PARTS.scale;
    for (const voice of Object.keys(stances)) {
        for (const x of [0.15, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85]) {
            for (const u of [0.32, 0.335, 0.36, 0.43]) {
                const target = {x, y: 0.275};
                const shot = sample(voice, u, target);
                const inverse = shot.rotation.clone().transpose();
                for (const side of ["l", "r"]) {
                    const palm = shot.pose.grip(side, [0, 0, 0]).applyMatrix4(shot.moves.get(`hand_${side}`)).sub(shot.origin).applyMatrix4(inverse);
                    expect(palm.x, `${voice} ${side} along receiver`).toBeGreaterThan(-0.06);
                    expect(palm.x, `${voice} ${side} behind muzzle`).toBeLessThan(front);
                    expect(Math.abs(palm.y), `${voice} ${side} beside weapon`).toBeLessThan(0.18);
                    expect(palm.z, `${voice} ${side} below weapon`).toBeLessThan(0.04);
                    expect(palm.z, `${voice} ${side} close to underside`).toBeGreaterThan(-0.3);
                }
                const barrel = new THREE.Vector3(1, 0, 0).applyMatrix4(shot.rotation);
                const from = shot.origin.clone().add(new THREE.Vector3(0, 0, RIFLE_HOLD.barrel).applyMatrix4(shot.rotation));
                const point = new THREE.Vector3((target.x - 0.5) * FRAMED.height, LOOK_DEPTH, FRAMED.middle + (0.5 - target.y) * FRAMED.height);
                const toward = point.sub(from);
                expect(toward.dot(barrel), `${voice} points toward target`).toBeGreaterThan(0);
                const off = toward.sub(barrel.multiplyScalar(toward.dot(barrel))).length();
                expect(off / FRAMED.height * 224, `${voice} aimed during exchange`).toBeLessThan(3);
            }
        }
    }
});
