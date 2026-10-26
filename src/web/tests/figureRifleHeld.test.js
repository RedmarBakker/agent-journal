// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, rifleTarget, Posing, RIFLE_HOLD, RIFLE_PARTS, burstKick, rifleAim} = await import("../src/figure/figure.js");
const {ACTS} = await import("../src/figure/acts.js");
const {FRAMED} = await import("../src/figure/frame.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "bug_shot");
const act = ACTS.bug_shot;
const radians = THREE.MathUtils.degToRad;
const SIZES = [112, 224];

// bugs on the chat's walls about the figure, as shares of its picture: on the left wall, the right wall, the top wall and high on the right
const TARGETS = [{x: -1.4, y: 0.2}, {x: 2.2, y: 0.35}, {x: 0.3, y: -1.6}, {x: 1.9, y: -1.1}];
// the handguard along the barrel from the grip, and its underside, in the rifle's own units as held (RIFLE_PARTS)
const [[guardAt], [guardSize]] = [[RIFLE_PARTS.handguard[0][0] * RIFLE_PARTS.scale], [RIFLE_PARTS.handguard[1].map((part) => part * RIFLE_PARTS.scale)]];
const guardBottom = (RIFLE_PARTS.handguard[0][2] * RIFLE_PARTS.scale) - guardSize[2] / 2;

// the rifle as held `u` of the way through the shot at `target` for `voice`: its place and turn, so a point of the figure can be read in
// the rifle's own axes, the hands that hold it, and the target in the figure's units
function held(u, target, voice) {
    const pose = new Posing(RIG, "stand", 0);
    pose.target = target;
    clip.pose(pose, stanceOf(voice), u);
    const moves = pose.moves(0);
    const rifle = pose.props.get("rifle");
    const origin = rifle.at.clone().applyMatrix4(moves.get(rifle.bone));
    const turned = new THREE.Matrix4().extractRotation(moves.get(rifle.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(radians(rifle.turn.x || 0), radians(rifle.turn.y || 0), radians(rifle.turn.z || 0), "ZYX")));
    const local = (point) => point.clone().sub(origin).applyMatrix4(turned.clone().transpose());
    const gripOf = (side) => pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`));
    const point = rifleTarget(target);
    return {rifle, origin, turned, local, gripOf, point, way: rifleAim(target, 0).way};
}

test("through the shooting, for every voice, one hand grips the rifle's grip and the other holds it from under the handguard, the rifle resting in that palm", () => {
    for (const voice of Object.keys(stances)) {
        for (const target of TARGETS) {
            for (let u = act.turn[0] + 0.08; u < act.turn[1]; u += 0.02) {
                const shot = held(u, target, voice);
                const [grip, fore] = shot.way > 0 ? ["r", "l"] : ["l", "r"];
                const label = `${voice} at ${target.x},${target.y} u ${u.toFixed(2)}`;
                expect(shot.rifle.bone, label).toBe(`hand_${grip}`);
                // the gripping hand's grip is where the rifle's grip is
                expect(shot.local(shot.gripOf(grip)).length(), `${label} on the grip`).toBeLessThan(0.02);
                // the other hand's palm under the handguard: along it, below its underside, and not off to its side
                const palm = shot.local(shot.gripOf(fore));
                expect(Math.abs(palm.x - guardAt), `${label} along the handguard`).toBeLessThan(guardSize[0] / 2 + 0.05);
                expect(palm.z, `${label} under the handguard`).toBeLessThan(guardBottom);
                expect(palm.z, `${label} close under it`).toBeGreaterThan(guardBottom - 0.3);
                expect(Math.abs(palm.y), `${label} not beside it`).toBeLessThan(0.15);
            }
        }
    }
    expect(RIFLE_HOLD.fore).toBeCloseTo(guardAt, 6);
});

test("it aims along the barrel at the bug it shoots: the barrel's line passes within a few pixels of the bug at both sizes, the kick and the hands with it", () => {
    for (const voice of Object.keys(stances)) {
        for (const target of TARGETS) {
            const kicks = [];
            for (let u = act.turn[0] + 0.08; u < act.turn[1]; u += 0.01) {
                const shot = held(u, target, voice);
                const barrel = new THREE.Vector3(1, 0, 0).applyMatrix4(shot.turned);
                const from = shot.origin.clone().add(new THREE.Vector3(0, 0, RIFLE_HOLD.barrel).applyMatrix4(shot.turned));
                const toward = shot.point.clone().sub(from);
                // the muzzle points at the bug, never away from it
                expect(toward.dot(barrel), `${voice} ${u.toFixed(2)} pointing at it`).toBeGreaterThan(0);
                const off = toward.clone().sub(barrel.clone().multiplyScalar(toward.dot(barrel))).length();
                for (const size of SIZES) expect((off / FRAMED.height) * size, `${voice} at ${target.x},${target.y} u ${u.toFixed(2)} size ${size}`).toBeLessThan(3);
                kicks.push({kick: burstKick(u), grip: shot.origin.clone()});
            }
            // a burst kicks the rifle, its grip and so the hand on it back from where it sat between bursts
            const still = kicks.find((each) => each.kick === 0);
            const kicked = kicks.reduce((best, each) => (each.kick > best.kick ? each : best));
            expect(kicked.kick).toBeGreaterThan(0.5);
            expect(kicked.grip.distanceTo(still.grip), `${voice} the hands with the kick`).toBeGreaterThan(0.05);
        }
    }
});
