// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, drawnPose} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, point]) => [name, new THREE.Vector3(...point)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((point) => new THREE.Vector3(...point))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("paper sorting and thoughtful typing ease each small hand lift into contact, including across the held loop", () => {
    for (const name of ["compacting", "type_ponder"]) {
        const clip = CLIPS.find((entry) => entry.name === name);
        const begin = clip.intro ?? 0;
        const length = clip.frames - begin - (clip.outro ?? 0);
        const delta = 0.0001;
        for (const voice of Object.keys(stances)) {
            for (const posture of clip.postures) {
                const at = (frame, hand) => {
                    const wrapped = begin + ((frame - begin) % length + length) % length;
                    const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip, wrapped, 0, {posture});
                    return RIG.heads.get(hand).clone().applyMatrix4(pose.moves(turned).get(hand));
                };
                for (const phase of [0, 0.25, 0.5, 0.75]) {
                    const frame = begin + phase * length;
                    for (const hand of ["hand_l", "hand_r"]) {
                        const before = at(frame - delta, hand).sub(at(frame - 2 * delta, hand)).multiplyScalar(clip.fps / delta);
                        const after = at(frame + 2 * delta, hand).sub(at(frame + delta, hand)).multiplyScalar(clip.fps / delta);
                        expect(before.distanceTo(after), `${name} ${voice} ${posture} ${hand} at ${phase}`).toBeLessThan(0.001);
                    }
                }
            }
        }
    }
});
