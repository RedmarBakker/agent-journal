import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, LEGS, Posing, SWING, drawnPose, moveProps, propsOf} = await import("../src/figure/figure.js");
const {ACTS, heldPhases, offSwing, swingAt} = await import("../src/figure/acts.js");
const {FRAMED} = await import("../src/figure/frame.js");
const {BUTLER, topHatGeometry} = await import("../src/figure/butler.js");

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
// bone's head is, and each mesh's box in the seat's own axes, so contact is checked along the tilted seat and ropes, not a world-aligned
// bounding box. `world` and `point` give the actual suspended bones and prop points in the scene (z up, forward -y).
function seated(frame, voice, props = propsOf(), posture = "sit") {
    const pose = new Posing(RIG, posture, 0);
    LEGS[posture].under(pose);
    clip.pose(pose, stanceOf(voice), frame / FRAMES);
    LEGS[posture].over(pose);
    const moves = pose.moves(0);
    moveProps({propByName: props}, pose, moves);
    const swing = props.get("rope_swing");
    swing.updateMatrixWorld(true);
    const fromGlb = new THREE.Matrix4().makeRotationX(Math.PI / 2);
    const unswing = pose.suspension?.clone().invert() ?? new THREE.Matrix4();
    const meshOf = (name) => swing.getObjectByName(`rope_swing_${name}`);
    const box = (name) => {
        const mesh = meshOf(name);
        mesh.geometry.computeBoundingBox();
        const local = mesh.geometry.boundingBox.clone().applyMatrix4(unswing.clone().multiply(fromGlb).multiply(mesh.matrixWorld));
        return {left: local.min.x, right: local.max.x, front: local.min.y, back: local.max.y, bottom: local.min.z, top: local.max.z};
    };
    const world = (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone));
    const point = (name, at = [0, 0, 0]) => new THREE.Vector3(...at).applyMatrix4(meshOf(name).matrixWorld).applyMatrix4(fromGlb);
    return {at: (bone) => world(bone).applyMatrix4(unswing), world, point, box, shown: swing.visible};
}

// points along a bone from its head to the next bone's head, `count` of them
const along = (at, from, to, count = 8) => Array.from({length: count + 1}, (_, index) => at(from).lerp(at(to), index / count));

test("every supported swing posture keeps both hands on the ropes instead of planting them on a floor", () => {
    const props = propsOf();
    const length = (act.rope + act.under) * FRAMED.height;
    for (const posture of clip.postures) {
        for (const voice of Object.keys(stances)) {
            const {at, world, point} = seated(act.intro, voice, props, posture);
            for (const side of ["l", "r"]) {
                const wrist = world(`hand_${side}`);
                const rope = new THREE.Line3(point(`rope_${side}`, [0, 0, -length / 2]), point(`rope_${side}`, [0, 0, length / 2]));
                expect(rope.closestPointToPoint(wrist, true, new THREE.Vector3()).distanceTo(wrist), `${voice} ${posture} ${side} rope grip`).toBeLessThan(0.45);
                expect(at(`hand_${side}`).z - at("hips").z, `${voice} ${posture} ${side} hand beside the head`).toBeGreaterThan(0.9);
            }
        }
    }
});

test("the swing is a seat with depth, two ropes and their knots in the figure's scene, shown in every frame of the act, and the figure sits down onto it", () => {
    const props = propsOf();
    const swing = props.get("rope_swing");
    for (const part of ["seat", "rope_l", "rope_r", "knot_l", "knot_r"]) expect(swing.getObjectByName(`rope_swing_${part}`)?.isMesh, part).toBe(true);
    for (let frame = 0; frame < FRAMES; frame++) expect(seated(frame, "butler", props).shown, `frame ${frame}`).toBe(true);
    const seat = seated(0, "butler", props).box("seat");
    expect(seat.back - seat.front).toBeCloseTo(SWING.back - SWING.front, 6);
    expect(seat.top - seat.bottom).toBeCloseTo(SWING.thick, 6);
    // its seat keeps its shape in the swing's own frame while the figure sits down and rises off it
    for (const frame of [act.intro, FRAMES - 1]) {
        const box = seated(frame, "butler", props).box("seat");
        for (const key of Object.keys(seat)) expect(box[key], key).toBeCloseTo(seat[key], 8);
    }
    expect(offSwing(0)).toBe(1);
    const held = (act.intro + act.hold / 2) / FRAMES;
    expect(heldPhases(act, held).held).not.toBe(null);
    expect(offSwing(held)).toBe(0);
    expect(offSwing(0.999)).toBeGreaterThan(0.9);
    for (const voice of Object.keys(stances)) expect(seated(0, voice).at("hips").z, voice).toBeGreaterThan(seated(FRAMES / 2, voice).at("hips").z + 0.1);
});

test("in every frame the feet and shins hang down before the seat's front, never through it, and the hips rest on its top while it swings", () => {
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
            const under = Math.min(at("thigh_l").z, at("thigh_r").z) - BODY.leg;
            expect(Math.abs(seat.top - under), `${label} seat under the hips`).toBeLessThan(PIXEL);
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

test("the knots stay fixed and both straight ropes keep their length while their seat follows a circular arc", () => {
    const props = propsOf();
    const start = seated(0, "butler", props);
    const knots = Object.fromEntries(["l", "r"].map((side) => [side, start.point(`knot_${side}`)]));
    const pivot = knots.l.clone().lerp(knots.r, 0.5);
    const radius = start.point("seat").distanceTo(pivot);
    const length = (act.rope + act.under) * FRAMED.height;
    for (let frame = 0; frame <= FRAMES; frame += 0.5) {
        const now = seated(frame, "butler", props);
        expect(now.point("seat").distanceTo(pivot), `seat radius at ${frame}`).toBeCloseTo(radius, 8);
        expect(now.point("seat").x, `no sideways drift at ${frame}`).toBeCloseTo(0, 8);
        for (const side of ["l", "r"]) {
            expect(now.point(`knot_${side}`).distanceTo(knots[side]), `${side} fixed knot at ${frame}`).toBeLessThan(1e-8);
            const top = now.point(`rope_${side}`, [0, 0, length / 2]);
            const bottom = now.point(`rope_${side}`, [0, 0, -length / 2]);
            expect(top.distanceTo(knots[side]), `${side} rope tied to knot at ${frame}`).toBeLessThan(1e-8);
            expect(top.distanceTo(bottom), `${side} constant rope at ${frame}`).toBeCloseTo(length, 8);
            const onSeat = now.point("seat", [(side === "l" ? 1 : -1) * act.ties * FRAMED.height / 2, 0, SWING.thick / 2]);
            expect(bottom.distanceTo(onSeat), `${side} rope tied to seat at ${frame}`).toBeLessThan(1e-8);
        }
    }
});

test("the seat rises at both ends, travels fastest at the bottom, and stops at each end of the swing", () => {
    const props = propsOf();
    const cycle = act.hold / act.swings;
    const at = (phase) => seated(act.intro + cycle * phase, "butler", props).point("seat");
    const bottom = at(0);
    const front = at(0.25);
    const back = at(0.75);
    expect(front.z).toBeGreaterThan(bottom.z + 0.18);
    expect(back.z).toBeCloseTo(front.z, 8);
    expect(front.y).toBeLessThan(bottom.y - 1);
    expect(back.y).toBeGreaterThan(bottom.y + 1);
    expect(at(0.5).z).toBeCloseTo(bottom.z, 8);
    const speed = (phase) => at(phase + 1e-4).distanceTo(at(phase - 1e-4)) / 2e-4;
    expect(speed(0.25)).toBeLessThan(1e-6);
    expect(speed(0.75)).toBeLessThan(1e-6);
    expect(speed(0.5)).toBeGreaterThan(speed(0.125));
    expect(speed(0.125)).toBeGreaterThan(speed(0.24));
});

test("starting, stopping and repeating the swing keep position and velocity continuous", () => {
    const delta = 1e-6;
    const speed = (u, direction) => (swingAt(u + direction * delta) - swingAt(u)) / (direction * delta);
    const start = act.intro / FRAMES;
    const end = (act.intro + act.hold) / FRAMES;
    for (const u of [0, start, end, 1]) {
        expect(Math.abs(speed(u, -1) - speed(u, 1)), `velocity at ${u}`).toBeLessThan(0.001);
        expect(Math.abs(swingAt(u - delta) - swingAt(u + delta)), `position at ${u}`).toBeLessThan(0.0001);
    }
    expect(swingAt(0)).toBeCloseTo(0, 8);
    expect(swingAt(1)).toBeCloseTo(0, 8);
    expect(speed(0, 1)).toBeCloseTo(0, 3);
    expect(speed(1, -1)).toBeCloseTo(0, 3);
    expect(speed(start, 1)).toBeCloseTo(speed(end, -1), 3);
});

test("the tall Butler hat stays inside the camera through boarding, both full arcs and rising off", () => {
    const geometry = topHatGeometry();
    const positions = geometry.attributes.position;
    const hat = Array.from({length: positions.count}, (_, index) => new THREE.Vector3(positions.getX(index), -positions.getZ(index), positions.getY(index) + BUTLER.hat.base));
    const ceiling = FRAMED.middle + FRAMED.height / 2;
    for (let frame = 0; frame <= FRAMES; frame += 0.5) {
        const {pose, turned} = drawnPose(RIG, stanceOf("butler"), clip, frame, 0, {posture: "sit"});
        const head = pose.moves(turned).get("head");
        const top = Math.max(...hat.map((point) => point.clone().applyMatrix4(head).z));
        expect(top, `hat at frame ${frame}`).toBeLessThan(ceiling - 0.07);
    }
    geometry.dispose();
});
