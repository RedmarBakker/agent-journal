// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, drawnPose} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const names = ["yawn", "whistle", "sip", "salute", "hat_tip", "monocle", "toast", "shaka", "shades", "fire", "thumbs_up", "peer", "thanks", "party_popper", "shield_up", "castle", "ask_sign", "file_card", "vacuum", "eager", "write", "compacting", "wipe_brow", "shield_polish", "read", "rest", "tickle_swat", "ponder", "think_cloud", "got_it"];
const clips = names.map((name) => CLIPS.find((clip) => clip.name === name));
const rotation = (matrix) => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().extractRotation(matrix));

function posed(clip, frame, voice = clip.voices?.[0] ?? "butler") {
    const {pose} = drawnPose(RIG, stanceOf(voice), clip, frame, 0);
    const moves = pose.moves(0);
    return {pose, moves, point: (bone, offset = new THREE.Vector3()) => RIG.heads.get(bone).clone().add(offset).applyMatrix4(moves.get(bone))};
}

test("gesture shoulders, wrists and fingers leave and return to the same resting pose without a first-frame snap", () => {
    const offsets = [new THREE.Vector3(), new THREE.Vector3(0.5, 0, 0), new THREE.Vector3(0, 0.5, 0), new THREE.Vector3(0, 0, 0.5)];
    for (const clip of clips) {
        for (const voice of clip.voices ?? Object.keys(stances)) {
            for (const [end, near] of [[0, 0.00001], [clip.frames - 1, clip.frames - 1.00001]]) {
                const a = posed(clip, end, voice);
                const b = posed(clip, near, voice);
                for (const role of ["upper_arm", "forearm", "hand"]) {
                    for (const side of ["l", "r"]) {
                        const bone = `${role}_${side}`;
                        for (const offset of offsets) expect(a.point(bone, offset).distanceTo(b.point(bone, offset)), `${clip.name} ${voice} ${bone} at ${end}`).toBeLessThan(0.0001);
                    }
                }
            }
        }
    }
});

test("gesture wrists turn continuously and neither arm stretches during its approach or return", () => {
    for (const clip of clips) {
        let before = null;
        for (let index = 0; index <= 400; index++) {
            const frame = (clip.frames - 1) * index / 400;
            const now = posed(clip, frame);
            for (const side of ["l", "r"]) {
                const hand = `hand_${side}`;
                if (before) expect(rotation(now.moves.get(hand)).angleTo(rotation(before.moves.get(hand))), `${clip.name} ${side} at ${frame}: wrist turn`).toBeLessThan(0.3);
                for (const [from, to] of [["upper_arm", "forearm"], ["forearm", "hand"]]) {
                    const a = `${from}_${side}`;
                    const b = `${to}_${side}`;
                    expect(now.point(a).distanceTo(now.point(b)), `${clip.name} ${side} at ${frame}: limb length`).toBeCloseTo(RIG.heads.get(a).distanceTo(RIG.heads.get(b)), 6);
                }
            }
            before = now;
        }
    }
});

test("a sip lifts the mug from its carried height and returns it there without dipping through the waist", () => {
    const clip = CLIPS.find((each) => each.name === "sip");
    const voice = "colleague";
    const side = [...stanceOf(voice).level][0];
    const hand = `hand_${side}`;
    const start = posed(clip, 0, voice);
    const grip = (step) => step.pose.grip(side, [0, 0, 0]).applyMatrix4(step.moves.get(hand));
    let highest = grip(start).z;
    for (let index = 0; index <= 200; index++) {
        const step = posed(clip, (clip.frames - 1) * index / 200, voice);
        const height = grip(step).z;
        expect(height).toBeGreaterThan(grip(start).z - 0.08);
        highest = Math.max(highest, height);
    }
    expect(highest - grip(start).z).toBeGreaterThan(0.2);
    expect(grip(posed(clip, clip.frames - 1, voice)).distanceTo(grip(start))).toBeLessThan(0.000001);
});

test("the colleague's arrival keeps the carried mug continuous when its sip begins and ends", () => {
    const clip = CLIPS.find((each) => each.name === "enter");
    const side = [...stanceOf("colleague").level][0];
    for (const u of [0.72, 0.98]) {
        const before = posed(clip, (u - 0.000001) * (clip.frames - 1), "colleague");
        const after = posed(clip, (u + 0.000001) * (clip.frames - 1), "colleague");
        const hand = `hand_${side}`;
        expect(before.point(hand).distanceTo(after.point(hand))).toBeLessThan(0.0001);
        expect(rotation(before.moves.get(hand)).angleTo(rotation(after.moves.get(hand)))).toBeLessThan(0.0001);
    }
});

test("sleep settles from the yawn into the held body pose and repeats that breath without a join", () => {
    const clip = CLIPS.find((each) => each.name === "sleep");
    for (const voice of Object.keys(stances)) {
        for (const [aFrame, bFrame] of [[clip.intro - 0.00001, clip.intro], [clip.frames - 0.00001, clip.intro]]) {
            const a = posed(clip, aFrame, voice);
            const b = posed(clip, bFrame, voice);
            for (const bone of ["head", "chest", "hand_l", "hand_r"]) {
                expect(a.point(bone).distanceTo(b.point(bone)), `${voice} ${bone}: sleep position`).toBeLessThan(0.0001);
                expect(rotation(a.moves.get(bone)).angleTo(rotation(b.moves.get(bone))), `${voice} ${bone}: sleep direction`).toBeLessThan(0.0001);
            }
            expect(a.pose.eyes).toBeCloseTo(b.pose.eyes, 6);
        }
    }
});

test("reading keeps both grips fixed while the head scans and returns smoothly at each line and page", () => {
    const clip = CLIPS.find((each) => each.name === "read");
    const begin = clip.intro;
    const end = clip.frames - clip.outro;
    for (const voice of Object.keys(stances)) {
        const start = posed(clip, begin, voice);
        for (let frame = begin; frame < end; frame += 0.5) {
            const step = posed(clip, frame, voice);
            expect(step.pose.book).toMatchObject({open: 1, visible: true});
            for (const side of ["l", "r"]) {
                const hand = `hand_${side}`;
                const contact = (at) => at.pose.grip(side, [0, 0, 0]).applyMatrix4(at.moves.get(hand));
                expect(contact(step).distanceTo(contact(start)), `${voice} frame ${frame}: steady book grip`).toBeLessThan(0.000001);
            }
        }
        for (let frame = begin + 6; frame <= end; frame += 6) {
            const a = posed(clip, frame - 0.00001, voice);
            const b = posed(clip, frame === end ? begin : frame + 0.00001, voice);
            expect(rotation(a.moves.get("head")).angleTo(rotation(b.moves.get("head"))), `${voice} frame ${frame}: gaze return`).toBeLessThan(0.00001);
        }
    }
});

test("thinking hands settle smoothly when the cloud or raised-finger phase releases them", () => {
    for (const name of ["ponder", "think_cloud", "got_it"]) {
        const clip = CLIPS.find((each) => each.name === name);
        const act = ACTS[name];
        const boundaries = [...new Set([...(act.into ?? []), ...act.rise, ...(act.fades ?? [])])];
        for (const voice of Object.keys(stances)) {
            for (const u of boundaries.filter((u) => u > 0 && u < 1)) {
                const a = posed(clip, (u - 0.000001) * (clip.frames - 1), voice);
                const b = posed(clip, (u + 0.000001) * (clip.frames - 1), voice);
                for (const side of ["l", "r"]) {
                    const hand = `hand_${side}`;
                    expect(a.point(hand).distanceTo(b.point(hand)), `${name} ${voice} ${u}: wrist position`).toBeLessThan(0.001);
                    expect(rotation(a.moves.get(hand)).angleTo(rotation(b.moves.get(hand))), `${name} ${voice} ${u}: wrist direction`).toBeLessThan(0.001);
                }
            }
        }
    }
});

test("alternating swats exchange the active hand without dropping the previous hand in a single step", () => {
    const clip = CLIPS.find((each) => each.name === "tickle_swat");
    for (const voice of Object.keys(stances)) {
        for (const frame of [6, 12, 18]) {
            const a = posed(clip, frame - 0.00001, voice);
            const b = posed(clip, frame + 0.00001, voice);
            for (const side of ["l", "r"]) {
                const hand = `hand_${side}`;
                expect(a.point(hand).distanceTo(b.point(hand)), `${voice} ${frame}: swat exchange`).toBeLessThan(0.0001);
                expect(rotation(a.moves.get(hand)).angleTo(rotation(b.moves.get(hand)))).toBeLessThan(0.0001);
            }
        }
    }
});
