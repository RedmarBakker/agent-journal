import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, LEGS, Posing, SWING, moveProps, propsOf} = await import("../src/figure/figure.js");
const {ACTS, heldPhases, offSwing} = await import("../src/figure/acts.js");
const {FRAMED} = await import("../src/figure/frame.js");

const {rig, stances} = JSON.parse(readFileSync("tests/figureRig.json"));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "rope_swing");
const act = ACTS.rope_swing;
const FRAMES = act.intro + act.hold + act.outro;

// The figure's body as every voice's model has it (public/voices/figures, the meshes' bounds): its legs 0.28 thick about their bones and
// 0.75 out from the middle, its coat 0.6, and its sleeves 0.27 thick about the arm at the wrist, in the figure's units
const BODY = {leg: 0.28, legs: 0.75, coat: 0.6, sleeve: 0.27};
// a pixel of the larger of the figure's two pictures, 224 pixels square, in the figure's units
const PIXEL = FRAMED.height / 224;

// the figure seated on the swing at `frame` of the act for `voice`, posed as the page draws it seated (figure.js Stage.draw): where each
// bone's head is, and the box each of the swing's meshes takes up in the figure's scene, in the figure's units (z up, forward -y)
function seated(frame, voice, props = propsOf()) {
    const pose = new Posing(RIG, "sit", 0);
    LEGS.sit.under(pose);
    clip.pose(pose, stanceOf(voice), frame / FRAMES);
    LEGS.sit.over(pose);
    const moves = pose.moves(0);
    moveProps({propByName: props}, pose, moves);
    const swing = props.get("rope_swing");
    swing.updateMatrixWorld(true);
    const box = (name) => {
        const glb = new THREE.Box3().setFromObject(swing.getObjectByName(`rope_swing_${name}`), true);
        return {left: glb.min.x, right: glb.max.x, front: -glb.max.z, back: -glb.min.z, bottom: glb.min.y, top: glb.max.y};
    };
    return {at: (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone)), box, shown: swing.visible};
}

// points along a bone from its head to the next bone's head, `count` of them
const along = (at, from, to, count = 8) => Array.from({length: count + 1}, (_, index) => at(from).lerp(at(to), index / count));

test("the swing is a seat with depth, two ropes and their knots in the figure's scene, shown in every frame of the act, and the figure sits down onto it", () => {
    const props = propsOf();
    const swing = props.get("rope_swing");
    for (const part of ["seat", "rope_l", "rope_r", "knot_l", "knot_r"]) expect(swing.getObjectByName(`rope_swing_${part}`)?.isMesh, part).toBe(true);
    for (let frame = 0; frame < FRAMES; frame++) expect(seated(frame, "butler", props).shown, `frame ${frame}`).toBe(true);
    const seat = seated(0, "butler", props).box("seat");
    expect(seat.back - seat.front).toBeCloseTo(SWING.back - SWING.front, 6);
    expect(seat.top - seat.bottom).toBeCloseTo(SWING.thick, 6);
    // it hangs where it is all the act long, while the figure sits down onto it and rises off it
    for (const frame of [act.intro, FRAMES - 1]) expect(seated(frame, "butler", props).box("seat")).toEqual(seat);
    expect(offSwing(0)).toBe(1);
    const held = (act.intro + act.hold / 2) / FRAMES;
    expect(heldPhases(act, held).held).not.toBe(null);
    expect(offSwing(held)).toBe(0);
    expect(offSwing(0.999)).toBeGreaterThan(0.9);
    for (const voice of Object.keys(stances)) expect(seated(0, voice).at("hips").z, voice).toBeGreaterThan(seated(FRAMES / 2, voice).at("hips").z + 0.2);
});

test("in every frame the feet and shins hang down before the seat's front, never through it, and the thighs rest on its top while it swings", () => {
    const props = propsOf();
    for (const voice of Object.keys(stances)) {
        for (let frame = 0; frame < FRAMES; frame++) {
            const {at, box} = seated(frame, voice, props);
            const seat = box("seat");
            const label = `${voice} frame ${frame}`;
            for (const side of ["l", "r"]) {
                for (const point of along(at, `shin_${side}`, `foot_${side}`)) expect(point.y + BODY.leg, `${label} ${side} shin before the seat`).toBeLessThan(seat.front);
                expect(at(`foot_${side}`).z + BODY.leg, `${label} ${side} foot under the thighs`).toBeLessThan(at(`thigh_${side}`).z);
            }
            if (frame < act.intro || frame >= act.intro + act.hold) continue;
            const under = Math.min(...["thigh_l", "shin_l", "thigh_r", "shin_r"].map((bone) => at(bone).z)) - BODY.leg;
            expect(Math.abs(seat.top - under), `${label} seat at the thighs`).toBeLessThan(PIXEL);
            expect(at("hips").y, `${label} hips over the seat`).toBeGreaterThan(seat.front);
            expect(at("hips").y, `${label} hips over the seat`).toBeLessThan(seat.back);
        }
    }
});

test("the figure sits between the ropes, which rise from the seat's ends to the bubble's edge beside it and behind its hands", () => {
    const props = propsOf();
    for (const voice of Object.keys(stances)) {
        for (let frame = 0; frame < FRAMES; frame += 3) {
            const {at, box} = seated(frame, voice, props);
            const [seat, left, right] = [box("seat"), box("rope_l"), box("rope_r")];
            const label = `${voice} frame ${frame}`;
            const ropes = [left, right].sort((a, b) => a.left - b.left);
            const across = Math.max(...["l", "r"].map((side) => Math.abs(at(`hand_${side}`).x) + BODY.sleeve), BODY.legs, BODY.coat);
            // the body and the arms between the ropes, the seat a little wider than it, the ropes from near its ends
            expect((ropes[0].left + ropes[0].right) / 2, `${label} left rope beside the body`).toBeLessThan(-across);
            expect((ropes[1].left + ropes[1].right) / 2, `${label} right rope beside the body`).toBeGreaterThan(across);
            expect(seat.right, `${label} seat wider than the body`).toBeGreaterThan(across);
            expect(seat.right, `${label} a little wider`).toBeLessThan(across * 1.3);
            for (const rope of ropes) {
                expect(rope.left, `${label} rope on the seat`).toBeGreaterThanOrEqual(seat.left);
                expect(rope.right, `${label} rope on the seat`).toBeLessThanOrEqual(seat.right);
                expect(rope.bottom, `${label} rope from the seat`).toBeCloseTo(seat.top, 6);
                expect(rope.top, `${label} rope to the bubble's edge`).toBeCloseTo(seat.top + (act.rope + act.under) * FRAMED.height, 6);
                for (const side of ["l", "r"]) expect(rope.front, `${label} rope behind the ${side} hand`).toBeGreaterThan(at(`hand_${side}`).y);
            }
        }
    }
});
