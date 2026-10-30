// @vitest-environment node
import * as THREE from "three";
import {beforeAll, expect, test} from "vitest";
import {ACTS} from "../src/figure/acts.js";
import {FRAMED} from "../src/figure/frame.js";
import {POSTURES} from "../src/figure/places.js";
import {armPropCrossings, armSurfaceDistance, nearestPropPoint, phoneArmMeshes, phoneClip, phonePose, phoneProps, phoneRig, phoneVoices, posedArm} from "./support/phoneGeometry.js";

const armsByVoice = new Map();
const cases = phoneVoices.flatMap((voice) => [
    {voice, posture: "stand", phoneWay: 1},
    ...["sit", "composed"].flatMap((posture) => [-1, 1].map((phoneWay) => ({voice, posture, phoneWay}))),
]);
const phases = ["drop", "settle", "reach", "lift", "finger", "dial", "back", "talk", "hang", "goes"];
const transitionSamples = [0.17, 0.19, 0.195, 0.225, 0.23, 0.235, 0.24, 0.245, 0.25, 0.2566666667, 0.744, 0.755, 0.76, 0.765, 0.77, 0.775, 0.78, 0.7875, 0.845, 0.87, 0.89, 0.91];
const samples = [...new Set([...Array.from({length: phoneClip.frames}, (_, index) => index / (phoneClip.frames - 1)), ...phases.flatMap((phase) => ACTS.phone_call[phase]), ...transitionSamples])].sort((a, b) => a - b);
const angledCases = phoneVoices.flatMap((voice) => [
    {voice, posture: "sit", facing: 70, leanWay: 0, phoneWay: -1},
    {voice, posture: "sit", facing: 290, leanWay: 0, phoneWay: 1},
    ...[-1, 1].flatMap((leanWay) => [-1, 1].map((phoneWay) => ({voice, posture: "composed", facing: leanWay * 25, leanWay, phoneWay}))),
]);
const reachSamples = [...new Set([
    ...Array.from({length: 25}, (_, index) => ACTS.phone_call.reach[0] + (ACTS.phone_call.lift[1] - ACTS.phone_call.reach[0]) * index / 24),
    ...Array.from({length: 25}, (_, index) => ACTS.phone_call.hang[0] + (ACTS.phone_call.goes[0] - ACTS.phone_call.hang[0]) * index / 24),
    ACTS.phone_call.reach[1], ACTS.phone_call.hang[1], ACTS.phone_call.dial[0], ACTS.phone_call.dial[1],
    ...transitionSamples,
])].sort((a, b) => a - b);

beforeAll(async () => {
    for (const voice of phoneVoices) armsByVoice.set(voice, await phoneArmMeshes(voice));
}, 120000);

function cordHeight(figure) {
    const group = figure.propByName.get("telephone_cord");
    if (!group.visible) return Infinity;
    const mesh = group.getObjectByName("telephone_cord_cord"), point = new THREE.Vector3();
    const positions = mesh.geometry.attributes.position;
    let lowest = Infinity;
    for (let index = 0; index < positions.count; index++) lowest = Math.min(lowest, point.fromBufferAttribute(positions, index).applyMatrix4(mesh.matrixWorld).y);
    return lowest;
}

test.each(phoneVoices)("%s collision vertices match the dressed runtime model and Three's skinning", (voice) => {
    const arms = armsByVoice.get(voice), figure = arms.figure;
    const {moves} = phonePose(0.36, voice, {posture: "composed", phoneWay: -1, facing: 25});
    const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2), fromGlb = toGlb.clone().invert();
    const world = new Map();
    for (const bone of figure.rig.bones) {
        expect(figure.rig.heads.get(bone.name).distanceTo(phoneRig.heads.get(bone.name)), `${voice}/${bone.name}: fixture rig`).toBeLessThan(1e-6);
        const placed = toGlb.clone().multiply(moves.get(bone.name)).multiply(fromGlb).multiply(figure.rig.rest.get(bone.name));
        world.set(bone.name, placed);
        const parent = bone.parent.isBone ? world.get(bone.parent.name) : bone.parent.matrixWorld;
        parent.clone().invert().multiply(placed).decompose(bone.position, bone.quaternion, bone.scale);
    }
    figure.scene.updateMatrixWorld(true);
    for (const skeleton of new Set(arms.map(({mesh}) => mesh.skeleton))) skeleton.update();
    for (const arm of arms) {
        const points = posedArm(arm, moves), count = arm.mesh.geometry.attributes.position.count;
        const blended = arm.remap.findIndex((index) => arm.influence[index].length > 1);
        const shoulder = arm.remap.findIndex((index) => arm.influence[index].some(({bone}) => bone.startsWith("upper_arm_")) && arm.influence[index].some(({bone}) => !/^(upper_arm|forearm|hand|wrist)(_|$)/.test(bone)));
        for (const index of new Set([0, Math.floor(count / 3), Math.floor(count * 2 / 3), count - 1, blended, shoulder].filter((index) => index >= 0))) {
            const runtime = arm.mesh.getVertexPosition(index, new THREE.Vector3()).applyMatrix4(arm.mesh.matrixWorld);
            expect(runtime.distanceTo(points[arm.remap[index]]), `${voice}/${arm.name}/${index}`).toBeLessThan(2e-6);
        }
    }
});

test.each(cases)("$voice $posture phone $phoneWay: every authored frame and phase boundary keeps solid arms outside the telephone, receiver and cord", ({voice, posture, phoneWay}) => {
    const arms = armsByVoice.get(voice), figure = phoneProps(), crossings = [];
    let lowest = {height: Infinity};
    for (const u of samples) {
        const {moves} = phonePose(u, voice, {posture, phoneWay}, figure);
        const hit = armPropCrossings(arms, moves, figure)[0];
        if (hit && crossings.length < 8) crossings.push({u, ...hit});
        const height = cordHeight(figure);
        if (height < lowest.height) lowest = {u, height};
    }
    const support = posture === "stand" ? 0 : POSTURES[posture].drop * FRAMED.height;
    expect(lowest.height, `${lowest.u}: cord stays above its supporting floor or seat`).toBeGreaterThanOrEqual(support - 1e-5);
    expect(crossings).toEqual([]);
}, 60000);

test.each(phoneVoices)("%s: the idle glove clears the floor and its outline while standing reaches and hangs up", (voice) => {
    const arms = armsByVoice.get(voice), figure = phoneProps(), options = {posture: "stand", phoneWay: 1};
    const holder = phonePose(0.6, voice, options, figure).pose.props.get("telephone_handset").bone.at(-1);
    const glove = arms.find(({name}) => name === `hand_shell_${holder === "l" ? "r" : "l"}`);
    for (const phase of [[ACTS.phone_call.reach[0], ACTS.phone_call.lift[1]], [ACTS.phone_call.hang[0], ACTS.phone_call.goes[0]]]) {
        for (let index = 0; index <= 60; index++) {
            const u = phase[0] + (phase[1] - phase[0]) * index / 60;
            const {moves} = phonePose(u, voice, options, figure);
            const height = Math.min(...posedArm(glove, moves).map((point) => point.y));
            expect(height, `${u}: glove and outline above the standing floor`).toBeGreaterThanOrEqual(0.036);
        }
    }
}, 30000);

test.each(angledCases)("$voice $posture facing $facing lean $leanWay phone $phoneWay: angled pickup and return clear the supported arm and its clothes", ({voice, ...options}) => {
    const arms = armsByVoice.get(voice), figure = phoneProps(), crossings = [];
    let lowest = {height: Infinity};
    for (const u of reachSamples) {
        const {moves} = phonePose(u, voice, options, figure);
        const hit = armPropCrossings(arms, moves, figure)[0];
        if (hit && crossings.length < 8) crossings.push({u, ...hit});
        const height = cordHeight(figure);
        if (height < lowest.height) lowest = {u, height};
    }
    expect(lowest.height, `${lowest.u}: cord stays above the supporting seat`).toBeGreaterThanOrEqual(POSTURES[options.posture].drop * FRAMED.height - 1e-5);
    expect(crossings).toEqual([]);
}, 60000);

test.each(cases)("$voice $posture phone $phoneWay: the coiled cord's centreline moves continuously through lifting and lowering", ({voice, posture, phoneWay}) => {
    const figure = phoneProps();
    for (const phase of [ACTS.phone_call.lift, ACTS.phone_call.hang]) {
        let previous = null, previousCoarse = null, fine = null, coarse = null;
        for (let step = 0; step <= 180; step++) {
            const u = phase[0] + (phase[1] - phase[0]) * step / 180;
            phonePose(u, voice, {posture, phoneWay}, figure);
            const cord = figure.propByName.get("telephone_cord").getObjectByName("telephone_cord_cord");
            // Helix controls keep their identity; tube rings are redistributed by arc length whenever the geometry is rebuilt.
            const current = cord.geometry.parameters.path.points.map((point) => point.clone().applyMatrix4(cord.matrixWorld));
            fine ??= new Float64Array(current.length);
            coarse ??= new Float64Array(current.length);
            if (previous) {
                expect(current.length, `${u}: stable cord topology`).toBe(previous.length);
                for (let index = 0; index < current.length; index++) fine[index] = Math.max(fine[index], current[index].distanceTo(previous[index]));
            }
            if (step % 2 === 0) {
                if (previousCoarse) for (let index = 0; index < current.length; index++) coarse[index] = Math.max(coarse[index], current[index].distanceTo(previousCoarse[index]));
                previousCoarse = current;
            }
            previous = current;
        }
        // Smooth movement approaches half the step when time is halved. A near-vertical winding flip stays large instead.
        for (let index = 0; index < fine.length; index++) expect(fine[index], `${phase}: helix point ${index} converges under time subdivision`).toBeLessThanOrEqual(coarse[index] * 0.65 + 1e-4);
    }
}, 30000);

test.each(cases)("$voice $posture phone $phoneWay: the actual glove stays at the turning finger hole until release", ({voice, posture, phoneWay}) => {
    const arms = armsByVoice.get(voice), figure = phoneProps();
    const {dial} = ACTS.phone_call;
    for (let index = 0; index <= 20; index++) {
        const u = dial[0] + (dial[1] - dial[0]) * index / 20;
        const {pose, moves} = phonePose(u, voice, {posture, phoneWay}, figure);
        const holder = pose.props.get("telephone_handset").bone.at(-1);
        const glove = arms.find(({name}) => name === `hand_shell_${holder === "l" ? "r" : "l"}`);
        const hole = figure.propByName.get("telephone").getObjectByName("telephone_hole_0");
        const contact = new THREE.Vector3(0, hole.geometry.parameters.height / 2, 0).applyMatrix4(hole.matrixWorld);
        const distance = armSurfaceDistance(glove, moves, contact);
        expect(distance, `${u}: actual fingertip at the visible hole`).toBeLessThan(0.025);
        expect(pose.props.get("telephone_handset").bone, `${u}: receiver held throughout dialling`).toMatch(/^hand_[lr]$/);
    }
}, 30000);

test.each(cases)("$voice $posture phone $phoneWay: the finger clears the hole before the rotary dial springs back", ({voice, posture, phoneWay}) => {
    const arms = armsByVoice.get(voice), figure = phoneProps();
    const {back} = ACTS.phone_call;
    phonePose(back[0], voice, {posture, phoneWay}, figure);
    const hole = figure.propByName.get("telephone").getObjectByName("telephone_hole_0");
    const heldAngle = hole.parent.rotation.y;
    let released = false;
    for (let index = 1; index <= 80; index++) {
        const u = back[0] + (back[1] - back[0]) * index / 80;
        const {pose, moves} = phonePose(u, voice, {posture, phoneWay}, figure);
        if (Math.abs(hole.parent.rotation.y - heldAngle) <= 1e-5) continue;
        const holder = pose.props.get("telephone_handset").bone.at(-1);
        const glove = arms.find(({name}) => name === `hand_shell_${holder === "l" ? "r" : "l"}`);
        const contact = new THREE.Vector3(0, hole.geometry.parameters.height / 2, 0).applyMatrix4(hole.matrixWorld);
        expect(armSurfaceDistance(glove, moves, contact), `${u}: clear before the wheel moves`).toBeGreaterThan(hole.geometry.parameters.radiusTop);
        released = true;
        break;
    }
    expect(released, "the dial returns after the finger leaves").toBe(true);
}, 30000);

test.each(cases)("$voice $posture phone $phoneWay: the solid glove touches the handle through pickup, lift, dial, talk and replacement", ({voice, posture, phoneWay}) => {
    const arms = armsByVoice.get(voice), figure = phoneProps();
    const {reach, hang} = ACTS.phone_call;
    for (let index = 0; index <= 24; index++) {
        const u = reach[1] + (hang[1] - reach[1] - 1e-7) * index / 24;
        const {pose, moves} = phonePose(u, voice, {posture, phoneWay}, figure);
        const holder = pose.props.get("telephone_handset").bone.at(-1);
        const glove = arms.find(({name}) => name === `hand_shell_${holder}`);
        const handle = figure.propByName.get("telephone_handset").getObjectByName("telephone_handset_handle");
        const palm = pose.grip(holder, [0, 0, 0]).applyMatrix4(moves.get(`hand_${holder}`)).applyMatrix4(new THREE.Matrix4().makeRotationX(-Math.PI / 2));
        const contact = nearestPropPoint(handle, palm);
        expect(armSurfaceDistance(glove, moves, contact), `${u}: handle contact rather than a floating grip`).toBeLessThan(0.02);
    }
}, 30000);
