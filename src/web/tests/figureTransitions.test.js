// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test, vi} from "vitest";
import {blendMoves, jointAngles, JOINT_STEP} from "../src/figure/blend.js";
import {CLIPS, blendedMoves, drawnPose} from "../src/figure/figure.js";
import {turnFrame} from "../src/figure/frame.js";
import {CHANGE_SECONDS} from "../src/figure/places.js";
import {FigurePlayer} from "../src/figure/player.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, point]) => [name, new THREE.Vector3(...point)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((point) => new THREE.Vector3(...point))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const poseAt = (clip, frame, posture, voice = "butler") => {
    const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip, frame, 0, {posture});
    return pose.moves(turned);
};

// The actual player and skeletal blend, with only raster drawing replaced so the caught pose can be measured without WebGL.
function playerAt(voice, posture, clip = CLIPS.find((each) => each.name === "idle"), frame = 8) {
    const context = {clearRect() {}, drawImage() {}};
    const player = Object.assign(Object.create(FigurePlayer.prototype), {
        figure: {}, moves: poseAt(clip, frame, posture, voice), shape: `${clip.name}/${posture}/0`, posture, blend: null, shown: "", facing: 0,
        canvas: {width: 112, height: 112, getContext: () => context},
    });
    player.liveOf = (clip, frame, facing, options) => {
        const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip, frame, facing, options);
        const result = blendedMoves(RIG, pose, turned, options.blend);
        if (options.blend) options.blend.settled = result.settled;
        return {frame: {}, moves: result.moves};
    };
    player.frameOf = (clip, frame, facing, posture) => player.liveOf(clip, frame, facing, {posture});
    return player;
}

const sameAnchors = (before, after, label) => {
    for (const bone of RIG.order) {
        const point = RIG.heads.get(bone);
        expect(point.clone().applyMatrix4(before.get(bone)).distanceTo(point.clone().applyMatrix4(after.get(bone))), `${label} ${bone}`).toBeLessThan(1e-6);
    }
};

test("catching any seated posture blends from the exact caught picture without planting airborne feet", () => {
    const clock = vi.spyOn(performance, "now").mockReturnValue(1000);
    try {
        const fall = CLIPS.find((clip) => clip.name === "fall");
        for (const voice of Object.keys(stances)) {
            for (const posture of ["sit", "lounge", "composed"]) {
                const player = playerAt(voice, posture);
                const before = player.moves;
                player.show(fall, 0, 0, {posture: "stand", airborne: true});
                sameAnchors(before, player.moves, `${voice} caught from ${posture}`);
                expect(player.blend.plant).toBe(false);
            }
        }
    } finally {
        clock.mockRestore();
    }
});

test("catching an in-progress planted rise keeps the last displayed pose when the floor constraint goes away", () => {
    let now = 1000;
    const clock = vi.spyOn(performance, "now").mockImplementation(() => now);
    try {
        const idle = CLIPS.find((clip) => clip.name === "idle");
        for (const posture of ["sit", "lounge", "composed"]) {
            const player = playerAt("butler", posture);
            player.show(idle, 0, 0, {posture: "stand"});
            expect(player.blend.plant).toBe(true);
            now += 80;
            player.show(idle, 0.64, 0, {posture: "stand"});
            const before = player.moves;
            player.show(idle, 0.64, 0, {posture: "stand", airborne: true});
            sameAnchors(before, player.moves, `caught during ${posture} rise`);
            expect(player.blend.from).toBe(before);
            expect(player.blend.plant).toBe(false);
        }
    } finally {
        clock.mockRestore();
    }
});

test("walk and run starts and stops keep their soles above the floor at every gait phase without changing their initial pose", () => {
    let now = 1000;
    const clock = vi.spyOn(performance, "now").mockImplementation(() => now);
    const idle = CLIPS.find((clip) => clip.name === "idle");
    const floor = Math.min(RIG.heads.get("foot_l").z, RIG.heads.get("foot_r").z);
    try {
        for (const name of ["walk", "run"]) {
            const movement = CLIPS.find((clip) => clip.name === name);
            for (const [source, target] of [[idle, movement], [movement, idle]]) {
                for (let phase = 0; phase < 40; phase++) {
                    const sourceFrame = phase / 40 * source.frames;
                    const targetFrame = phase / 40 * target.frames;
                    const player = playerAt("butler", "stand", source, sourceFrame);
                    const before = player.moves;
                    const label = `${source.name} to ${target.name} phase ${phase / 40}`;
                    player.show(target, targetFrame, 0, {posture: "stand"});
                    sameAnchors(before, player.moves, label);
                    expect(player.blend.floor, label).toBe(true);
                    for (let frame = 1; frame <= 30; frame++) {
                        now += 1000 / 60;
                        player.show(target, targetFrame + frame / 60 * target.fps, 0, {posture: "stand"});
                        const lower = Math.min(...["l", "r"].map((side) => RIG.heads.get(`foot_${side}`).clone().applyMatrix4(player.moves.get(`foot_${side}`)).z));
                        expect(lower, `${label} frame ${frame}`).toBeGreaterThanOrEqual(floor - 1e-7);
                    }
                }
            }
        }
    } finally {
        clock.mockRestore();
    }
});

test("catching a grounded run stop drops the floor constraint without moving the caught frame", () => {
    let now = 1000;
    const clock = vi.spyOn(performance, "now").mockImplementation(() => now);
    try {
        const run = CLIPS.find((clip) => clip.name === "run");
        const idle = CLIPS.find((clip) => clip.name === "idle");
        const player = playerAt("butler", "stand", run, 0.175 * run.frames);
        player.show(idle, 0, 0, {posture: "stand"});
        for (let frame = 1; frame <= 8; frame++) {
            now += 1000 / 60;
            player.show(idle, frame / 60 * idle.fps, 0, {posture: "stand"});
        }
        expect(player.blend.floor).toBe(true);
        const before = player.moves;
        player.show(idle, 8 / 60 * idle.fps, 0, {posture: "stand", airborne: true});
        sameAnchors(before, player.moves, "caught while stopping");
        expect(player.blend.from).toBe(before);
        expect(player.blend.floor).toBe(false);
        expect(player.blend.plant).toBe(false);
        const wave = CLIPS.find((clip) => clip.name === "wave");
        player.show(wave, 0, 0, {posture: "stand"});
        expect(player.blend.floor, "unrelated gestures do not gain a locomotion constraint").toBe(false);
    } finally {
        clock.mockRestore();
    }
});

test("turns take the short arc across zero and begin and finish without an angular step", () => {
    let state = {facing: 350, speed: 0};
    const angles = [state.facing];
    for (let index = 0; index < 60; index++) {
        state = turnFrame(state, 10, 1 / 60, CHANGE_SECONDS);
        angles.push(state.facing);
    }
    expect(angles[1] - angles[0]).toBeLessThan(2.1);
    for (let index = 1; index < angles.length; index++) {
        expect(angles[index]).toBeGreaterThanOrEqual(angles[index - 1]);
        expect(angles[index]).toBeLessThanOrEqual(370);
    }
    expect(state).toEqual({facing: 370, speed: 0, settled: true});
});

test("turns keep their velocity when retargeted and advance by elapsed time at different display rates", () => {
    const first = turnFrame({facing: 0, speed: 0}, 40, 0.04, CHANGE_SECONDS);
    const retargeted = turnFrame(first, 50, 0, CHANGE_SECONDS);
    expect(retargeted.facing).toBe(first.facing);
    expect(retargeted.speed).toBe(first.speed);
    const at = (fps) => {
        let state = {facing: 0, speed: 0};
        for (let frame = 0; frame < fps / 5; frame++) state = turnFrame(state, 40, 1 / fps, CHANGE_SECONDS);
        return state;
    };
    expect(at(30).facing).toBeCloseTo(at(120).facing, 8);
    expect(at(30).speed).toBeCloseTo(at(120).speed, 8);
});

test("every clip can be interrupted and blended back to rest without a first-frame jump or disconnected joint", () => {
    const idle = CLIPS.find((clip) => clip.name === "idle");
    for (const clip of CLIPS) {
        const voice = clip.voices?.[0] ?? "butler";
        const posture = clip.postures[0];
        const from = poseAt(clip, clip.frames * 0.47, posture, voice);
        const to = poseAt(idle, 0, "stand", voice);
        let previous = from;
        let settled = false;
        for (let step = 0; step <= 45; step++) {
            const k = Math.min(step / 15, 1);
            const result = blendMoves(RIG, from, to, k * k * (3 - 2 * k), previous);
            for (const [bone, angle] of jointAngles(RIG, previous, result.moves)) {
                expect(angle, `${clip.name} ${bone} frame ${step}`).toBeLessThanOrEqual(JOINT_STEP + 1e-6);
                const matrix = result.moves.get(bone);
                expect(matrix.elements.every(Number.isFinite), `${clip.name} ${bone}`).toBe(true);
                if (/^(forearm|hand|shin|foot)_[lr]$|^(neck|head)$/.test(bone)) {
                    const point = RIG.heads.get(bone);
                    const parent = result.moves.get(RIG.parents.get(bone));
                    expect(point.clone().applyMatrix4(matrix).distanceTo(point.clone().applyMatrix4(parent)), `${clip.name} keeps ${bone} attached`).toBeLessThan(1e-6);
                }
                if (step === 0) {
                    const point = RIG.heads.get(bone);
                    expect(point.clone().applyMatrix4(matrix).distanceTo(point.clone().applyMatrix4(from.get(bone))), `${clip.name} starts on ${bone}`).toBeLessThan(1e-6);
                }
            }
            previous = result.moves;
            settled = result.settled;
        }
        expect(settled, clip.name).toBe(true);
    }
});

test("every idle, gesture and movement loop meets with continuous limb velocity", () => {
    const delta = 0.0001;
    for (const clip of CLIPS.filter((each) => each.loops)) {
        for (const voice of clip.voices ?? Object.keys(stances)) {
            for (const posture of clip.postures) {
                const start = clip.intro ?? 0, end = clip.frames - (clip.outro ?? 0);
                const samples = [end - 2 * delta, end - delta, start + delta, start + 2 * delta].map((frame) => poseAt(clip, frame, posture, voice));
                for (const bone of RIG.order) {
                    const positions = samples.map((moves) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone)));
                    const before = positions[1].sub(positions[0]).multiplyScalar(clip.fps / delta);
                    const after = positions[3].sub(positions[2]).multiplyScalar(clip.fps / delta);
                    expect(before.distanceTo(after), `${clip.name} ${voice} ${posture} ${bone}`).toBeLessThan(0.01);
                }
            }
        }
    }
});
