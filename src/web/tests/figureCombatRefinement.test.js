// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {ACTS, backAt, smashAt, smashPlan} from "../src/figure/acts.js";
import {BIG_MALLET, CLIPS, Posing, burstKick, malletAt} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

function boneAt(name, voice, u, bone) {
    const pose = new Posing(RIG, "stand", 0);
    CLIPS.find((clip) => clip.name === name).pose(pose, stanceOf(voice), u);
    return RIG.heads.get(bone).clone().applyMatrix4(pose.moves(0).get(bone));
}

test("backing toward a firing position eases at both ends while steps follow actual distance", () => {
    for (const way of [-1, 1]) {
        const plan = [{from: 300, to: 300 + way * 180, begin: 10, end: 30}];
        const at = (frame) => backAt(plan, frame, 112);
        const start = Math.abs(at(10.1).x - at(10).x);
        const middle = Math.abs(at(20.1).x - at(20).x);
        const end = Math.abs(at(30).x - at(29.9).x);
        expect(start).toBeLessThan(middle * 0.02);
        expect(end).toBeLessThan(middle * 0.02);
        expect(at(20).steps).toBeCloseTo(Math.abs(at(20).x - 300) / (ACTS.bug_shot.back.stride * 112), 9);
        expect(at(30)).toMatchObject({x: plan[0].to, way: 0});
    }
});

test("each rifle burst has a continuous fast attack and a longer eased recovery", () => {
    const {shots, count} = ACTS.bug_shot;
    const duration = (shots[1] - shots[0]) / count;
    for (let burst = 0; burst < count; burst++) {
        const start = shots[0] + duration * burst;
        expect(burstKick(start)).toBeCloseTo(0, 9);
        expect(burstKick(start + duration * 0.001)).toBeLessThan(0.001);
        expect(burstKick(start + duration * 0.08)).toBeCloseTo(1, 9);
        expect(burstKick(start + duration * 0.3)).toBeGreaterThan(0.1);
        expect(burstKick(start + duration * 0.5)).toBeCloseTo(0, 9);
    }
});

test("the mallet accelerates into the marked impact, rebounds clear and settles without moving the target", () => {
    const {swing, blow} = ACTS.bug_smash;
    const at = (u) => {
        const {grip, way} = malletAt(u);
        return grip.clone().addScaledVector(way, 2);
    };
    const early = at(swing[0] + 0.01).distanceTo(at(swing[0]));
    const late = at(blow).distanceTo(at(blow - 0.01));
    expect(late).toBeGreaterThan(early * 3);
    expect(at(blow + 0.035).z).toBeGreaterThan(at(blow).z + 0.1);
    expect(at(blow + 0.07).distanceTo(at(blow))).toBeLessThan(0.001);
    expect(at(blow + 0.035).x).toBeCloseTo(at(blow).x, 9);
});

test("every voice preloads its knees and compresses into the mallet blow before recovering", () => {
    const {raise, blow} = ACTS.bug_smash;
    for (const voice of Object.keys(stances)) {
        const rest = boneAt("bug_smash", voice, 0, "hips").z;
        const prepared = boneAt("bug_smash", voice, raise[1], "hips").z;
        const struck = boneAt("bug_smash", voice, blow, "hips").z;
        const recovered = boneAt("bug_smash", voice, blow + 0.12, "hips").z;
        expect(prepared, voice).toBeLessThan(rest - 0.025);
        expect(struck, voice).toBeLessThan(prepared - 0.05);
        expect(recovered, voice).toBeGreaterThan(struck + 0.1);
    }
});

// The cylindrical head's support distance follows its tilted axis, including the flat end's rim.
function malletContact(pose) {
    const held = pose.props.get("big_mallet");
    if (!held) return null;
    const moves = pose.moves(0);
    const turn = new THREE.Euler(...["x", "y", "z"].map((axis) => THREE.MathUtils.degToRad(held.turn[axis] || 0)), "ZYX");
    const rotation = new THREE.Matrix4().extractRotation(moves.get(held.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(turn));
    const origin = held.at.clone().applyMatrix4(moves.get(held.bone));
    const way = new THREE.Vector3(1, 0, 0).transformDirection(rotation);
    const axis = new THREE.Vector3(0, 0, 1).transformDirection(rotation);
    const head = origin.clone().addScaledVector(way, BIG_MALLET.handle);
    const bottom = head.z - BIG_MALLET.head * Math.sqrt(1 - axis.z ** 2) - BIG_MALLET.width * 0.5 * Math.abs(axis.z);
    const left = pose.grip("l", [0, 0, 0]).applyMatrix4(moves.get("hand_l")).sub(origin);
    return {held, head, bottom, left: left.clone().addScaledVector(way, -left.dot(way)).length()};
}

test("the mallet stays above the floor, lands over the bug, and both closed palms meet its handle", () => {
    const clip = CLIPS.find((entry) => entry.name === "bug_smash");
    for (const voice of Object.keys(stances)) {
        for (let frame = 0; frame <= clip.frames * 4; frame++) {
            const u = frame / (clip.frames * 4);
            const pose = new Posing(RIG, "stand", 0);
            clip.pose(pose, stanceOf(voice), u);
            const contact = malletContact(pose);
            if (!contact) continue;
            expect(contact.bottom, `${voice} at ${u.toFixed(3)} above floor`).toBeGreaterThanOrEqual(0);
            if (u >= ACTS.bug_smash.raise[0] && u <= ACTS.bug_smash.lower[1]) {
                expect(contact.left, `${voice} at ${u.toFixed(3)} supporting palm`).toBeLessThan(0.08);
            }
        }
        const pose = new Posing(RIG, "stand", 0);
        clip.pose(pose, stanceOf(voice), ACTS.bug_smash.blow);
        const contact = malletContact(pose);
        expect(Math.abs(contact.head.x - ACTS.bug_smash.side * ACTS.bug_smash.away * 5.4), `${voice} target`).toBeLessThan(0.04);
        expect(contact.bottom, `${voice} contact`).toBeLessThan(0.025);
    }
});

function combatFoot(name, u, placed, side) {
    const pose = new Posing(RIG, "stand", name === "bug_shot" ? -placed.steps : placed.steps);
    pose.walkWay = placed.way;
    pose.target = {x: 2.2, y: 0.35};
    CLIPS.find((clip) => clip.name === name).pose(pose, stanceOf("butler"), u);
    const point = RIG.heads.get(`foot_${side}`).clone().applyMatrix4(pose.moves(0).get(`foot_${side}`));
    const phase = ((pose.stride + (side === "l" ? 0 : 0.5)) % 1 + 1) % 1;
    return {x: point.x + (placed.figure ?? placed.x) * 5.4 / 112, z: point.z, phase};
}

test("combat feet plant against page distance through both the approach and backward side steps", () => {
    const cases = [
        {name: "bug_smash", start: 0.2, end: 0.33, placed: (u) => smashAt(smashPlan(340, {left: 0, right: 1000}, 112), u, 112)},
        {name: "bug_shot", start: 0.25, end: 0.29, placed: (u) => backAt([{from: 400, to: 250, begin: ACTS.bug_shot.draw[1] * 80, end: ACTS.bug_shot.aim[1] * 80}], u * 80, 112)},
    ];
    for (const {name, start, end, placed} of cases) {
        let planted = 0;
        for (let u = start; u < end; u += 0.001) {
            for (const side of ["l", "r"]) {
                const first = combatFoot(name, u, placed(u), side);
                const next = combatFoot(name, u + 0.001, placed(u + 0.001), side);
                if (first.phase < 0.02 || next.phase < 0.02 || first.phase > 0.58 || next.phase > 0.58) continue;
                expect(next.x, `${name} ${side} at ${u.toFixed(3)} planted`).toBeCloseTo(first.x, 6);
                expect(next.z, `${name} ${side} at ${u.toFixed(3)} grounded`).toBeCloseTo(first.z, 6);
                planted++;
            }
        }
        expect(planted, name).toBeGreaterThan(5);
    }
});
