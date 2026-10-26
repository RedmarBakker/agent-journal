// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, drawnPose} from "../src/figure/figure.js";
import {BUTLER, topHatGeometry} from "../src/figure/butler.js";
import {FRAMED} from "../src/figure/frame.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const voices = Object.keys(stances);
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clips = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));

// The root is an animation origin below the hips, not a point on the rendered silhouette.
const bodyBones = RIG.order.filter((bone) => bone !== "root");

// Actual top-hat vertices cover the tallest head silhouette; rig joints cover the tucked body.
const hatGeometry = topHatGeometry();
const hatPositions = hatGeometry.attributes.position;
const hat = Array.from({length: hatPositions.count}, (_, index) => new THREE.Vector3(hatPositions.getX(index), -hatPositions.getZ(index), hatPositions.getY(index) + BUTLER.hat.base));

function posed(name, u, voice, facing = 0) {
    const clip = clips[name];
    const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip, u * (clip.frames - 1), facing, {posture: "stand"});
    const moves = pose.moves(turned);
    return {moves, at: (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone))};
}

test("the complete inverted hat and rig remain inside the unchanged production camera", () => {
    const half = FRAMED.height / 2;
    const margin = 0.04;
    const extent = {left: Infinity, right: -Infinity, bottom: Infinity, top: -Infinity};
    const point = new THREE.Vector3();
    for (const voice of voices) {
        for (const facing of [0, 45, 90, 135, 180, 225, 270, 315]) {
            for (let frame = 0; frame <= 128; frame++) {
                const {moves, at} = posed("backflip", frame / 128, voice, facing);
                const points = [...bodyBones.map(at), ...hat.map((vertex) => point.copy(vertex).applyMatrix4(moves.get("head")).clone())];
                for (const vertex of points) {
                    extent.left = Math.min(extent.left, vertex.x);
                    extent.right = Math.max(extent.right, vertex.x);
                    extent.bottom = Math.min(extent.bottom, vertex.z);
                    extent.top = Math.max(extent.top, vertex.z);
                }
            }
        }
    }
    expect(extent.left).toBeGreaterThan(-half + margin);
    expect(extent.right).toBeLessThan(half - margin);
    expect(extent.bottom, "the inverted hat clears the bottom of the canvas").toBeGreaterThan(FRAMED.middle - half + margin);
    expect(extent.top).toBeLessThan(FRAMED.middle + half - margin);
});

test("takeoff preparation lowers the body while both shoes remain planted", () => {
    for (const name of ["jump", "backflip"]) {
        for (const voice of voices) {
            const before = posed(name, 0, voice);
            for (let frame = 0; frame <= 26; frame++) {
                const pose = posed(name, frame / 100, voice);
                for (const side of ["l", "r"]) {
                    expect(pose.at(`foot_${side}`).z, `${name} ${voice} ${side} preparation`).toBeCloseTo(before.at(`foot_${side}`).z, 7);
                    const up = new THREE.Vector3(0, 0, 1).transformDirection(pose.moves.get(`foot_${side}`));
                    expect(up.z, `${name} ${voice} ${side} sole stays flat`).toBeCloseTo(1, 7);
                }
            }
            const crouched = posed(name, 0.26, voice);
            expect(crouched.at("root").z - before.at("root").z).toBeCloseTo(-0.28, 7);
            expect(crouched.at("chest").z).toBeLessThan(before.at("chest").z - 0.25);
        }
    }
});

test("landing absorbs the weight above fixed feet and returns exactly to its contact pose", () => {
    for (const voice of voices) {
        const before = posed("land", 0, voice);
        for (let frame = 0; frame <= 100; frame++) {
            const pose = posed("land", frame / 100, voice);
            for (const side of ["l", "r"]) {
                expect(pose.at(`foot_${side}`).distanceTo(before.at(`foot_${side}`)), `${voice} ${side} contact`).toBeLessThan(1e-7);
                const up = new THREE.Vector3(0, 0, 1).transformDirection(pose.moves.get(`foot_${side}`));
                expect(up.z, `${voice} ${side} flat sole`).toBeCloseTo(1, 7);
            }
        }
        const deepest = posed("land", 0.2, voice);
        expect(deepest.at("root").z).toBeCloseTo(-0.32, 7);
        expect(deepest.at("chest").z).toBeLessThan(before.at("chest").z - 0.3);
        for (const name of ["land", "backflip"]) {
            const first = posed(name, 0, voice);
            const last = posed(name, 1, voice);
            for (const bone of RIG.order) {
                const difference = Math.max(...first.moves.get(bone).elements.map((value, index) => Math.abs(value - last.moves.get(bone).elements[index])));
                expect(difference, `${name} ${voice} ${bone} returns to its exact starting pose`).toBeLessThan(1e-9);
            }
        }
    }
    expect([clips.jump.frames, clips.jump.fps, clips.backflip.frames, clips.backflip.fps, clips.land.frames, clips.land.fps]).toEqual([16, 20, 22, 20, 6, 20]);
});
