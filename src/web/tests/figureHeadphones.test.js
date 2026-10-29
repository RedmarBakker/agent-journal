// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, drawnPose} from "../src/figure/figure.js";
import {headphoneContacts, headphoneGrip, headphonesAt, headphonesOf, moveHeadphones} from "../src/figure/homie.js";
import {PROP_FADE_SECONDS} from "../src/figure/propTransition.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stance = Object.fromEntries(Object.entries(stances.homie).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "groove");
const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
const posed = (u, posture = "stand", facing = 0) => {
    const {pose, turned} = drawnPose(RIG, stance, clip, u * (clip.frames - 1), facing, {posture});
    return {pose, moves: pose.moves(turned)};
};
const difference = (a, b) => Math.max(...a.cups.flatMap((cup, index) => [cup.at.distanceTo(b.cups[index].at), cup.turn.angleTo(b.cups[index].turn)]), ...a.band.map((point, index) => point.distanceTo(b.band[index])));
const accessory = () => headphonesOf((root, name, geometry, colour, at = [0, 0, 0]) => {
    const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({color: colour}));
    mesh.name = `${root.name}_${name}`;
    mesh.position.fromArray(at);
    mesh.add(new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({side: THREE.BackSide})));
    root.add(mesh);
    return mesh;
});
const materials = (root) => {
    const found = [];
    root.traverse((mesh) => { if (mesh.material) found.push(mesh.material); });
    return found;
};

test.each(clip.postures)("Homie visibly holds both cup rims while lifting and lowering in %s", (posture) => {
    let contacts = 0;
    for (const facing of [0, 90, 180, 270]) for (let sample = 0; sample <= 240; sample++) {
        const u = sample / 240;
        if (headphoneGrip(u) < 1 - 1e-9) continue;
        const {pose, moves} = posed(u, posture, facing);
        const cups = headphoneContacts(headphonesAt(u, moves));
        for (const [index, side] of ["l", "r"].entries()) {
            const fingers = pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`)).applyMatrix4(toGlb);
            expect(fingers.distanceTo(cups[index].at), `${posture} ${side} ${u} ${facing}`).toBeLessThan(2e-5);
            contacts++;
        }
    }
    expect(contacts).toBeGreaterThan(800);
});

test.each(clip.postures)("the music gesture returns to the same loose-neck pose in %s without a limb jump", (posture) => {
    const first = posed(0, posture), last = posed(1, posture);
    expect(difference(headphonesAt(0, first.moves), headphonesAt(1, last.moves))).toBeLessThan(1e-7);
    for (const bone of RIG.order) expect(Math.max(...first.moves.get(bone).elements.map((value, index) => Math.abs(value - last.moves.get(bone).elements[index]))), bone).toBeLessThan(1e-7);
    let previous = null, maximumStep = 0, maximumTurn = 0;
    const samples = Math.ceil((clip.frames - 1) / clip.fps * 120);
    for (let sample = 0; sample <= samples; sample++) {
        const {moves} = posed(sample / samples, posture);
        const state = headphonesAt(sample / samples, moves);
        expect([...state.cups.flatMap((cup) => [...cup.at, ...cup.turn]), ...state.band.flatMap((point) => [...point])].every(Number.isFinite)).toBe(true);
        if (previous) for (let i = 0; i < 2; i++) {
            maximumStep = Math.max(maximumStep, state.cups[i].at.distanceTo(previous.cups[i].at));
            maximumTurn = Math.max(maximumTurn, state.cups[i].turn.angleTo(previous.cups[i].turn));
        }
        previous = state;
    }
    expect(maximumStep).toBeLessThan(0.08);
    expect(maximumTurn).toBeLessThan(0.12);
});

test("cups remain rigid and opaque for the complete authored music gesture", () => {
    const headset = accessory(), materialState = materials(headset.root);
    const originals = headset.cups.map((cup) => cup.children.map((mesh) => [...mesh.geometry.attributes.position.array]));
    for (let sample = 0; sample <= 120; sample++) {
        const u = sample / 120, {moves} = posed(u);
        expect(moveHeadphones(headset, {u}, moves, sample / 18)).toBe(false);
        expect(headset.root.visible).toBe(true);
        expect(materialState.every((material) => material.opacity === 1 && !material.transparent && material.depthWrite)).toBe(true);
        for (const cup of headset.cups) expect(cup.scale.toArray()).toEqual([1, 1, 1]);
    }
    headset.cups.forEach((cup, i) => cup.children.forEach((mesh, j) => expect([...mesh.geometry.attributes.position.array]).toEqual(originals[i][j])));
});

test.each([0.08, 0.17, 0.26, 0.48, 0.8, 0.96])("cancelling music at %s preserves the displayed headset, then retires it before restoring the neck pose", (u) => {
    const headset = accessory(), {moves} = posed(u), idle = posed(0).moves;
    moveHeadphones(headset, {u}, moves, 3);
    const displayed = headset.previous;
    expect(moveHeadphones(headset, null, idle, 4)).toBe(true);
    expect(difference(displayed, headset.previous)).toBeLessThan(1e-7);
    expect(materials(headset.root).every((material) => material.opacity === 1)).toBe(true);
    moveHeadphones(headset, null, idle, 4 + PROP_FADE_SECONDS / 2);
    expect(materials(headset.root).every((material) => Math.abs(material.opacity - 0.5) < 1e-8 && material.transparent && !material.depthWrite)).toBe(true);
    moveHeadphones(headset, null, idle, 4 + PROP_FADE_SECONDS);
    expect(headset.root.visible).toBe(false);
    expect(difference(headset.previous, headphonesAt(null, idle))).toBeLessThan(1e-9);
    expect(moveHeadphones(headset, null, idle, 4 + 2 * PROP_FADE_SECONDS + 1e-8)).toBe(false);
    expect(headset.root.visible).toBe(true);
    expect(headset.returning).toBe(null);
    expect(materials(headset.root).every((material) => material.opacity === 1 && !material.transparent && material.depthWrite)).toBe(true);
});

test("restarting music during its retirement does not flash or rewind opacity; static samples clear live recovery", () => {
    const headset = accessory(), {moves} = posed(0.48);
    moveHeadphones(headset, {u: 0.48}, moves, 2);
    moveHeadphones(headset, null, posed(0).moves, 3);
    moveHeadphones(headset, null, posed(0).moves, 3.08);
    const alpha = materials(headset.root)[0].opacity;
    moveHeadphones(headset, {u: 0.02}, posed(0.02).moves, 3.08);
    expect(materials(headset.root)[0].opacity).toBe(alpha);
    moveHeadphones(headset, {u: 0.02}, posed(0.02).moves, 2);
    expect(materials(headset.root)[0].opacity).toBe(alpha);
    expect(moveHeadphones(headset, null, posed(0).moves)).toBe(false);
    expect(headset.returning).toBe(null);
    expect(materials(headset.root).every((material) => material.opacity === 1 && !material.transparent && material.depthWrite)).toBe(true);
});
