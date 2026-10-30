// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, REACTING, drawnPose, moveProps, propsOf} from "../src/figure/figure.js";
import {BUTLER, topHatGeometry} from "../src/figure/butler.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stance = Object.fromEntries(Object.entries(stances.butler).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "tantrum");
const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2), fromGlb = toGlb.clone().invert();
const position = topHatGeometry().attributes.position;
const vertices = Array.from({length: position.count}, (_, i) => new THREE.Vector3().fromBufferAttribute(position, i));

function sampled(u, props = propsOf()) {
    const {pose, turned} = drawnPose(RIG, stance, clip, u * (clip.frames - 1), 0);
    const moves = pose.moves(turned);
    moveProps({propByName: props}, pose, moves);
    const hat = props.get("top_hat");
    hat.updateMatrixWorld(true);
    const worn = toGlb.clone().multiply(moves.get("head")).multiply(fromGlb).multiply(new THREE.Matrix4().makeTranslation(0, BUTLER.hat.base, 0));
    return {pose, moves, hat, placed: hat.visible ? hat.matrixWorld.clone() : worn, at: (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone))};
}

test("the Butler removes one opaque, rigid hat, leaves it on the floor, and puts it back at its raised resting height", () => {
    const props = propsOf();
    let lowest = Infinity;
    for (let sample = 0; sample <= 480; sample++) {
        const u = sample / 480;
        const {pose, hat, placed} = sampled(u, props);
        expect(pose.stowed.has("butler_top_hat"), `worn crown at ${u}`).toBe(hat.visible);
        expect(pose.stowed.has("butler_top_hat_band"), `worn band at ${u}`).toBe(hat.visible);
        const scale = new THREE.Vector3().setFromMatrixScale(placed);
        expect(scale.distanceTo(new THREE.Vector3(1, 1, 1)), `rigid hat at ${u}`).toBeLessThan(1e-7);
        expect(placed.elements.every(Number.isFinite), `finite hat at ${u}`).toBe(true);
        hat.traverse((part) => {
            for (const material of [part.material ?? []].flat()) {
                expect(material.opacity, `opaque hat at ${u}`).toBe(1);
                expect(material.transparent, `solid hat at ${u}`).toBe(false);
            }
        });
        lowest = Math.min(lowest, ...vertices.map((point) => point.clone().applyMatrix4(placed).y));
    }
    expect(lowest, "the brim never passes through the floor").toBeGreaterThanOrEqual(0);
    expect(lowest, "the thrown hat reaches the floor").toBeLessThan(0.06);
    for (const u of [0, 1]) {
        const {pose, hat} = sampled(u, props);
        expect(hat.visible).toBe(false);
        expect(pose.props.size).toBe(0);
        expect(pose.stowed.size).toBe(0);
    }
});

test("the fingers remain on the actual curled brim through the pickup, lift and placement", () => {
    const props = propsOf();
    const side = stance.busy.has("r") ? "l" : "r";
    const angle = THREE.MathUtils.degToRad(REACTING.hatGripAngle);
    const radius = BUTLER.hat.crown + BUTLER.hat.brim;
    const local = new THREE.Vector3((side === "r" ? -1 : 1) * radius * Math.cos(angle), BUTLER.hat.curl * Math.cos(angle) ** 2 + BUTLER.hat.thick / 2, radius * Math.sin(angle));
    for (const [from, to] of [[0.12, 0.18], [0.7, 0.96]]) {
        for (let sample = 0; sample <= 60; sample++) {
            const u = from + (to - from) * sample / 60;
            const {pose, moves, placed} = sampled(u, props);
            const fingers = pose.grip(side, [REACTING.hatFingers, 0, 0]).applyMatrix4(moves.get(`hand_${side}`)).applyMatrix4(toGlb);
            expect(local.clone().applyMatrix4(placed).distanceTo(fingers), `brim grip at ${u}`).toBeLessThan(1e-5);
        }
    }
});

test("six frantic hops happen while the released hat stays independently on the floor", () => {
    const props = propsOf();
    const heights = [];
    const floor = sampled(0.4, props).placed;
    for (let sample = 0; sample <= 600; sample++) {
        const u = 0.34 + 0.26 * sample / 600;
        const {at, placed} = sampled(u, props);
        heights.push(at("root").z);
        if (u >= 0.4) expect(Math.max(...placed.elements.map((value, i) => Math.abs(value - floor.elements[i]))), `floor hat at ${u}`).toBeLessThan(1e-8);
    }
    const peaks = heights.slice(1, -1).filter((height, i) => height > heights[i] && height >= heights[i + 2] && height > 0.25);
    expect(peaks).toHaveLength(6);
    expect(Math.min(...peaks), "every hop has an emphatic airborne rise").toBeGreaterThan(0.35);
});

test("the hat waits on the floor until the hand grasps it and then stays supported by that hand", () => {
    const props = propsOf();
    const grounded = sampled(0.4, props).placed;
    for (let sample = 0; sample <= 160; sample++) {
        const u = 0.4 + 0.32 * sample / 160;
        const {placed} = sampled(u, props);
        expect(Math.max(...placed.elements.map((value, i) => Math.abs(value - grounded.elements[i]))), `grounded until grasp at ${u}`).toBeLessThan(1e-5);
    }
    for (const u of [0.71, 0.75, 0.8, 0.85, 0.905]) {
        const {pose} = sampled(u, props);
        const held = pose.props.get("top_hat");
        expect(held.bone, `hand support at ${u}`).toBe("hand_r");
        expect(held.frame, `hand orientation at ${u}`).toBe("hand_r");
    }
    expect(sampled(0.8, props).placed.elements[13], "the grasped hat leaves the floor").toBeGreaterThan(1);
});

test("the thrown hat crosses its release, landing, retrieval and worn handoffs continuously", () => {
    const props = propsOf();
    for (const u of [0.12, 0.18, 0.22, 0.26, 0.34, 0.39, 0.6, 0.64, 0.7, 0.72, 0.78, 0.81, 0.84, 0.85, 0.91, 0.96]) {
        const before = sampled(u - 1e-6, props), after = sampled(u + 1e-6, props);
        for (const point of vertices) {
            expect(point.clone().applyMatrix4(before.placed).distanceTo(point.clone().applyMatrix4(after.placed)), `hat surface at ${u}`).toBeLessThan(0.001);
        }
        for (const bone of RIG.order) expect(before.at(bone).distanceTo(after.at(bone)), `${bone} at ${u}`).toBeLessThan(0.001);
    }
});
