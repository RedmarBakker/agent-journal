// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clips = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));
const voices = Object.keys(stances);

function posed(name, u, voice) {
    const clip = clips[name];
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf(voice), u * (clip.frames - 1) / clip.frames);
    const moves = pose.moves(0);
    return {pose, moves, at: (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone))};
}

function continuousAt(name, u, voice) {
    const before = posed(name, Math.max(0, u - 1e-5), voice);
    const after = posed(name, Math.min(1, u + 1e-5), voice);
    for (const bone of RIG.order) {
        expect(after.at(bone).distanceTo(before.at(bone)), `${voice} ${name} ${bone} at ${u}`).toBeLessThan(0.003);
        const rotations = [before, after].map(({moves}) => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().extractRotation(moves.get(bone))));
        expect(rotations[0].angleTo(rotations[1]), `${voice} ${name} ${bone} turns continuously at ${u}`).toBeLessThan(0.005);
    }
}

test("the chase brakes and turns continuously at its farthest point, returning along the same path", () => {
    for (const voice of voices) {
        for (const u of [0, 0.4, 0.5, 0.6, 1]) continuousAt("squire_chase", u, voice);
        const places = Array.from({length: 101}, (_, i) => posed("squire_chase", i / 100, voice).at("root"));
        expect(places[50].x, `${voice} still chases the bug`).toBeGreaterThan(1);
        for (const [i, at] of places.entries()) {
            expect(Math.abs(at.y), `${voice} stays on the outward and return path`).toBeLessThan(1e-8);
            expect(at.x, `${voice} never teleports across home`).toBeGreaterThanOrEqual(-1e-8);
            if (i > 0 && i <= 50) expect(at.x).toBeGreaterThanOrEqual(places[i - 1].x - 1e-8);
            if (i > 50) expect(at.x).toBeLessThanOrEqual(places[i - 1].x + 1e-8);
        }
        expect(places[100].x).toBeCloseTo(places[0].x, 9);
    }
});

test("disco hands and elbows cross continuously at every beat while keeping distinct pointing poses", () => {
    for (const voice of voices) {
        for (let beat = 1; beat < ACTS.disco.beats; beat++) continuousAt("disco", beat / ACTS.disco.beats, voice);
        const rightUp = posed("disco", 0.5 / ACTS.disco.beats, voice);
        const leftUp = posed("disco", 1.5 / ACTS.disco.beats, voice);
        expect(rightUp.at("hand_r").z - rightUp.at("hand_l").z, voice).toBeGreaterThan(0.8);
        expect(leftUp.at("hand_l").z - leftUp.at("hand_r").z, voice).toBeGreaterThan(0.8);
        for (let frame = 0; frame <= 96; frame++) {
            const {at} = posed("disco", frame / 96, voice);
            for (const side of ["l", "r"]) expect(at(`foot_${side}`).z, `${voice} grounded dancing foot`).toBeCloseTo(RIG.heads.get(`foot_${side}`).z, 5);
        }
    }
});

test("fuming raises each free arm only once and eases continuously into and out of clenched fists", () => {
    for (const voice of voices) {
        for (const u of [ACTS.fume.mad[0], ACTS.fume.mad[1], 1]) continuousAt("fume", u, voice);
        const neutral = new Posing(RIG, "stand", 0);
        clips.idle.pose(neutral, stanceOf(voice), 0);
        const idle = neutral.moves(0);
        for (const u of [0, 1]) {
            const {moves} = posed("fume", u, voice);
            for (const side of stanceOf(voice).free) {
                for (const role of ["upper_arm", "forearm", "hand"]) {
                    const bone = `${role}_${side}`;
                    for (const [index, value] of moves.get(bone).elements.entries()) expect(value, `${voice} ${bone} rests naturally at ${u}`).toBeCloseTo(idle.get(bone).elements[index], 8);
                }
            }
        }
    }
});

test("each refined reaction returns to its first pose at the last authored frame", () => {
    for (const name of ["squire_chase", "disco", "fume"]) {
        for (const voice of voices) {
            const first = posed(name, 0, voice);
            const last = posed(name, 1, voice);
            for (const bone of RIG.order) expect(last.at(bone).distanceTo(first.at(bone)), `${voice} ${name} ${bone}`).toBeLessThan(1e-7);
        }
    }
});
