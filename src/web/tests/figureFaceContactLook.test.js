// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, drawnPose} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const named = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));
const external = {at: {x: 1.2, y: 0.2, amount: 0.75}, eyes: {mood: "amused", seconds: 1, lasts: 3}, tilt: 18, grabbed: true};
const contacts = [["yawn", "butler", 0.5], ["sleep", "butler", 0.3], ["whistle", "coach", 0.5], ["sip", "colleague", 0.5], ["enter", "colleague", 0.85], ["salute", "squire", 0.5], ["wipe_brow", "butler", 0.5]];
const offsets = [[0, 0, 0], [0.3, 0, 0], [0, 0.3, 0], [0, 0, 0.3]];

function sample(name, voice, u, posture, options = {}) {
    const {pose} = drawnPose(RIG, stanceOf(voice), named[name], u * (named[name].frames - 1), 25, {posture, ...options});
    return {pose, moves: pose.moves(0)};
}

function distanceAt(a, b, bone, offset) {
    const point = RIG.heads.get(bone).clone().add(new THREE.Vector3(...offset));
    return point.clone().applyMatrix4(a.moves.get(bone)).distanceTo(point.clone().applyMatrix4(b.moves.get(bone)));
}

test("held face contacts resist an external look, viewer turn, and head tilt without changing clip metadata", () => {
    for (const [name, voice, u] of contacts) for (const posture of named[name].postures) {
        const plain = sample(name, voice, u, posture);
        const looking = sample(name, voice, u, posture, external);
        expect(plain.pose.headContact, `${name} ${posture}`).toBe(1);
        for (const bone of ["head", "hand_l", "hand_r"]) for (const offset of offsets) {
            expect(distanceAt(plain, looking, bone, offset), `${name} ${posture} ${bone}`).toBeLessThan(0.000001);
        }
    }
});

test("gaze and tilt yield continuously at each face-contact start and release", () => {
    for (const [name, voice] of contacts) {
        const boundaries = name === "sleep" ? [0, 27 / 45] : name === "enter" ? [0.72, 0.98] : [0, 1];
        for (const posture of named[name].postures) for (const u of boundaries) {
            const a = sample(name, voice, Math.max(0, u - 0.000001), posture, external);
            const b = sample(name, voice, Math.min(1, u + 0.000001), posture, external);
            for (const bone of ["head", "hand_l", "hand_r"]) for (const offset of offsets) {
                expect(distanceAt(a, b, bone, offset), `${name} ${posture} ${u} ${bone}`).toBeLessThan(0.0001);
            }
        }
    }
});

test("the contact guard leaves ordinary looks active at rest and suppresses them gradually", () => {
    const plain = sample("yawn", "butler", 0, "stand");
    const looking = sample("yawn", "butler", 0, "stand", {at: external.at});
    expect(plain.pose.headContact).toBe(0);
    expect(distanceAt(plain, looking, "head", [0, -0.5, 0])).toBeGreaterThan(0.1);
    const midway = sample("yawn", "butler", 0.1, "stand", external);
    expect(midway.pose.headContact).toBeGreaterThan(0);
    expect(midway.pose.headContact).toBeLessThan(1);
});
