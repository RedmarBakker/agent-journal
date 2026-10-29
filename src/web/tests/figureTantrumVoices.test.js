// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, drawnPose} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const voices = ["homie", "coach", "colleague", "squire"];
const tracked = ["hips", "head", "hand_l", "hand_r", "shin_l", "shin_r", "foot_l", "foot_r"];
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = () => CLIPS.find((each) => each.name === "tantrum");
const at = (voice, u) => {
    const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip(), u * (clip().frames - 1), 0, {posture: "stand"});
    const moves = pose.moves(turned);
    const points = new Map(tracked.map((bone) => [bone, RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone))]));
    return {pose, moves, points};
};

test.each(voices)("%s finishes its tantrum in the same relaxed pose, with its carried items restored", (voice) => {
    const first = at(voice, 0), last = at(voice, 1);
    for (const bone of RIG.order) {
        const a = first.moves.get(bone).elements, b = last.moves.get(bone).elements;
        expect(Math.max(...a.map((value, index) => Math.abs(value - b[index]))), bone).toBeLessThan(1e-8);
    }
    expect([...last.pose.stowed]).toEqual([...first.pose.stowed]);
    expect(last.pose.eyes).toBe(first.pose.eyes);
    expect(last.pose.eyeShape).toBe(first.pose.eyeShape);
});

test.each(voices)("%s keeps a supporting foot planted and returns every stamp above the floor", (voice) => {
    const floor = Math.min(...["foot_l", "foot_r"].map((bone) => RIG.heads.get(bone).z));
    let lifted = 0;
    for (let sample = 0; sample <= 360; sample++) {
        const {points} = at(voice, sample / 360);
        const feet = [points.get("foot_l").z, points.get("foot_r").z];
        expect(Math.min(...feet), `${voice} supporting foot at ${sample}`).toBeCloseTo(floor, 6);
        expect(Math.max(...feet), `${voice} stamping foot at ${sample}`).toBeGreaterThanOrEqual(floor - 1e-7);
        lifted = Math.max(lifted, ...feet.map((height) => height - floor));
    }
    expect(lifted, "the foot actually leaves the floor during the performance").toBeGreaterThan(0.2);
});

test.each(voices)("%s has finite, continuous full-body motion at playback sampling", (voice) => {
    const samples = Math.ceil((clip().frames - 1) / clip().fps * 120);
    let previous = null, maximumStep = 0, maximumTurn = 0;
    for (let sample = 0; sample <= samples; sample++) {
        const current = at(voice, sample / samples);
        for (const [bone, matrix] of current.moves) {
            expect(matrix.elements.every(Number.isFinite), `${voice} ${bone} at ${sample}`).toBe(true);
        }
        if (previous) {
            for (const bone of tracked) {
                maximumStep = Math.max(maximumStep, current.points.get(bone).distanceTo(previous.points.get(bone)));
                const rotation = (matrix) => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().extractRotation(matrix));
                maximumTurn = Math.max(maximumTurn, rotation(current.moves.get(bone)).angleTo(rotation(previous.moves.get(bone))));
            }
        }
        previous = current;
    }
    expect(maximumStep, "no single-frame limb displacement at 120 Hz").toBeLessThan(0.12);
    expect(maximumTurn, "no single-frame joint flip at 120 Hz").toBeLessThan(0.22);
});

test("the four persona tantrums have visibly different head, hand, and foot trajectories", () => {
    const paths = new Map(voices.map((voice) => [voice, Array.from({length: 25}, (_, index) => at(voice, index / 24).points)]));
    for (let left = 0; left < voices.length; left++) {
        for (let right = left + 1; right < voices.length; right++) {
            let distance = 0, count = 0;
            paths.get(voices[left]).forEach((points, index) => {
                for (const bone of ["head", "hand_l", "hand_r", "foot_l", "foot_r"]) {
                    distance += points.get(bone).distanceToSquared(paths.get(voices[right])[index].get(bone));
                    count++;
                }
            });
            expect(Math.sqrt(distance / count), `${voices[left]} and ${voices[right]}`).toBeGreaterThan(0.06);
        }
    }
});
