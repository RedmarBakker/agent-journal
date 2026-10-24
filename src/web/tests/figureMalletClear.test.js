// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {BIG_MALLET, CLIPS, Posing} = await import("../src/figure/figure.js");
const {ACTS, bugAt} = await import("../src/figure/acts.js");
const {FRAMED} = await import("../src/figure/frame.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "bug_smash");
const act = ACTS.bug_smash;
const radians = THREE.MathUtils.degToRad;

// The head's parts as every voice wears them, read from the models' bounds (public/voices/figures, the meshes on head_root) and the
// butler's top hat (butler.js BUTLER hat), each a box in the figure's units at rest, across, forward (less is toward the viewer) and up:
// the shell, the visor with the eyes and the colleague's glasses before it, the ears, the hats and the coach's cap visor
const HEAD_PARTS = {
    shell: {min: [-0.92, -0.88, 2.47], max: [0.92, 0.88, 4.0]},
    face: {min: [-0.77, -1.05, 2.73], max: [0.77, 0, 3.45]},
    ears: {min: [-1.23, -0.35, 2.73], max: [1.23, 0.35, 3.44]},
    hats: {min: [-1.1, -1.1, 3.38], max: [1.1, 1.1, 4.55]},
    cap_visor: {min: [-0.79, -1.32, 3.38], max: [0.79, -0.56, 3.54]},
};
const boxes = Object.entries(HEAD_PARTS).map(([name, {min, max}]) => ({name, box: new THREE.Box3(new THREE.Vector3(...min), new THREE.Vector3(...max))}));

// the mallet as held `u` of the way through the smash for `voice`, in the figure's units: points along its handle and its head's middle,
// each with how far round it its part reaches, and the head's move that carries the head's parts
function posed(u, voice) {
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf(voice), u);
    const moves = pose.moves(0);
    const held = pose.props.get("big_mallet");
    if (!held) return {pose, moves, mallet: null};
    const origin = held.at.clone().applyMatrix4(moves.get(held.bone));
    const turned = new THREE.Matrix4().extractRotation(moves.get(held.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(radians(held.turn.x || 0), radians(held.turn.y || 0), radians(held.turn.z || 0), "ZYX")));
    const way = new THREE.Vector3(1, 0, 0).transformDirection(turned);
    const handle = Array.from({length: 21}, (_, step) => ({at: origin.clone().addScaledVector(way, (BIG_MALLET.handle * step) / 20), reach: BIG_MALLET.grip * 1.2}));
    const head = {at: origin.clone().addScaledVector(way, BIG_MALLET.handle), reach: Math.hypot(BIG_MALLET.head, BIG_MALLET.width / 2)};
    return {pose, moves, mallet: {handle, head}};
}

// how far a point of the figure's units, carried back into the head's own place at rest by the head's move, is from the nearest of its parts
const clearance = (moves, point) => {
    const local = point.clone().applyMatrix4(moves.get("head").clone().invert());
    return Math.min(...boxes.map(({box}) => box.distanceToPoint(local)));
};

test("through every frame of the bug smash, for every voice, the mallet's head and handle stay clear of the figure's head, its visor and any hat", () => {
    for (const voice of Object.keys(stances)) {
        for (let frame = 0; frame < clip.frames; frame++) {
            const {moves, mallet} = posed(frame / clip.frames, voice);
            if (!mallet) continue;
            const label = `${voice} frame ${frame}`;
            for (const {at, reach} of mallet.handle) expect(clearance(moves, at), `${label} handle`).toBeGreaterThan(reach);
            expect(clearance(moves, mallet.head.at), `${label} head`).toBeGreaterThan(mallet.head.reach);
        }
    }
});

test("at the top of the swing the mallet stands above and in front of the head, held there for the wind-up, and at the blow it strikes at the bug's spot", () => {
    for (const voice of Object.keys(stances)) {
        // held up through the wind-up, from the end of the raise to the start of the swing, a good part of a second
        expect((act.swing[0] - act.raise[1]) * clip.frames / clip.fps).toBeGreaterThan(0.4);
        for (let u = act.raise[1]; u < act.swing[0]; u += 0.01) {
            const {moves, mallet} = posed(u, voice);
            const local = mallet.head.at.clone().applyMatrix4(moves.get("head").clone().invert());
            const eyes = RIG.eyes[0].z;
            expect(local.z, `${voice} ${u.toFixed(2)} above the eyes`).toBeGreaterThan(eyes + 0.3);
            expect(local.y, `${voice} ${u.toFixed(2)} in front of the visor`).toBeLessThan(HEAD_PARTS.face.min[1] - mallet.head.reach);
        }
        // the blow: the mallet's head down on the floor where the bug lies, out on the figure's left
        const {mallet} = posed(act.blow, voice);
        const bug = (bugAt(act, act.blow, 112).out / 112) * FRAMED.height;
        expect(Math.abs(mallet.head.at.x - bug), `${voice} across, at the bug`).toBeLessThan(0.6);
        expect(mallet.head.at.z - mallet.head.reach, `${voice} down on the floor`).toBeLessThan(0.3);
    }
});
