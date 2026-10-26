// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, TOOLS, drawnPose} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const files = JSON.parse(readFileSync(new URL("../public/voices/figures/figures.json", import.meta.url)));
const bytes = readFileSync(new URL(`../public/voices/figures/${files.colleague}`, import.meta.url));
const model = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
const bounds = (name) => {
    const node = model.nodes.find((each) => each.name === name);
    return model.accessors[model.meshes[node.mesh].primitives[0].attributes.POSITION];
};
const shell = bounds("head_shell");
const cup = bounds("colleague_mug__cup");
const glove = bounds("hand_shell_l");
const rim = new THREE.Vector3(cup.min[0], -(cup.min[2] + cup.max[2]) / 2, cup.max[1]);
const named = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));

function sample(name, voice, u, posture = "stand", options = {}) {
    const {facing = 0, ...extra} = options;
    const {pose} = drawnPose(RIG, stanceOf(voice), named[name], u * (named[name].frames - 1), facing, {posture, ...extra});
    const moves = pose.moves(0);
    const head = moves.get("head").clone().invert();
    return {pose, moves, head, local: (point) => point.clone().applyMatrix4(head)};
}

function lowerFace(point, label) {
    expect(Math.abs(point.x), label).toBeLessThan(0.3);
    expect(point.y, label).toBeGreaterThan(-shell.max[2] - 0.2);
    expect(point.y, label).toBeLessThan(-shell.max[2] - 0.035);
    expect(point.z, label).toBeGreaterThan(shell.min[1] + 0.1);
    expect(point.z, label).toBeLessThan(shell.min[1] + 0.32);
}

test("yawn fingers cover the lower face for every voice and supported posture", () => {
    for (const voice of Object.keys(stances)) for (const posture of named.yawn.postures) for (const u of [0.25, 0.5, 0.75]) {
        const step = sample("yawn", voice, u, posture);
        const side = stanceOf(voice).busy.has("r") ? "l" : "r";
        lowerFace(step.local(step.pose.grip(side, [0, 0, 0]).applyMatrix4(step.moves.get(`hand_${side}`))), `${voice} ${posture} ${u}`);
    }
});

test("seated face contacts leave and regain their support without an arm snap", () => {
    for (const [name, voice] of [["yawn", "butler"], ["whistle", "coach"], ["sip", "colleague"], ["salute", "squire"], ["wipe_brow", "butler"]]) {
        for (const posture of ["lounge", "composed"]) for (const options of [{}, {facing: 25}, {facing: -25, leanWay: 1}, {facing: 25, leanWay: -1}]) for (const [u, nearby] of [[0, 0.000001], [1, 0.999999]]) {
            const a = sample(name, voice, u, posture, options);
            const b = sample(name, voice, nearby, posture, options);
            for (const side of ["l", "r"]) {
                const hand = `hand_${side}`;
                for (const offset of [[0, 0, 0], [0.3, 0, 0], [0, 0.3, 0], [0, 0, 0.3]]) {
                    const point = RIG.heads.get(hand).clone().add(new THREE.Vector3(...offset));
                    expect(point.clone().applyMatrix4(a.moves.get(hand)).distanceTo(point.clone().applyMatrix4(b.moves.get(hand))), `${name} ${posture} ${u} ${side}`).toBeLessThan(0.0001);
                }
            }
        }
    }
});

test("the actual whistle mouthpiece reaches the lower face while its body stays in front", () => {
    for (const posture of named.whistle.postures) for (const u of [0.25, 0.5, 0.75]) {
        const step = sample("whistle", "coach", u, posture);
        const prop = step.pose.props.get("hand_whistle");
        const mouth = new THREE.Vector3(TOOLS.whistle.mouthAt[0], -TOOLS.whistle.mouthAt[2] + TOOLS.whistle.mouthpiece[2] / 2, TOOLS.whistle.mouthAt[1]);
        const rotation = new THREE.Matrix4().extractRotation(step.moves.get(prop.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(0, 0, THREE.MathUtils.degToRad(prop.turn.z), "ZYX")));
        const origin = prop.at.clone().applyMatrix4(step.moves.get(prop.bone));
        lowerFace(step.local(mouth.applyMatrix4(rotation).add(origin)), `${posture} ${u}`);
        expect(step.local(origin).y).toBeLessThan(-shell.max[2] - 0.15);
    }
});

test("the supplied mug's near rim meets the lower face through the sip and arrival sip", () => {
    for (const [name, phases] of [["sip", [0.25, 0.4, 0.5, 0.6, 0.75]], ["enter", [0.82, 0.86, 0.9]]]) {
        for (const posture of named[name].postures) for (const u of phases) {
            const step = sample(name, "colleague", u, posture);
            lowerFace(step.local(rim.clone().applyMatrix4(step.moves.get("hand_l"))), `${name} ${posture} ${u}`);
            expect(step.pose.stowed.has("colleague_mug")).toBe(false);
            const radius = (cup.max[0] - cup.min[0]) / 2;
            for (const z of [cup.min[1], cup.max[1]]) for (let index = 0; index < 16; index++) {
                const angle = index * Math.PI / 8;
                const surface = new THREE.Vector3((cup.min[0] + cup.max[0]) / 2 + radius * Math.cos(angle), rim.y + radius * Math.sin(angle), z);
                const local = step.local(surface.applyMatrix4(step.moves.get("hand_l")));
                if (local.z >= shell.min[1]) expect(local.y, `${name} ${posture}: mug clear of face`).toBeLessThan(-shell.max[2] - 0.025);
            }
            if (name === "sip" && u === 0.5) {
                const up = new THREE.Vector3(0, 0, 1).transformDirection(step.moves.get("hand_l")).transformDirection(step.head);
                expect(up.y, "the mug tips toward the face").toBeGreaterThan(0.15);
            }
        }
    }
});

test("the salute fingers reach the upper temple while the palm stays outside the head shell", () => {
    for (const posture of named.salute.postures) for (const u of [0.25, 0.5, 0.75]) {
        const step = sample("salute", "squire", u, posture);
        const side = [...stanceOf("squire").free][0];
        const point = step.local(step.pose.grip(side, [0, 0, 0]).applyMatrix4(step.moves.get(`hand_${side}`)));
        expect(Math.abs(point.x)).toBeGreaterThan(shell.max[0] + 0.035);
        expect(Math.abs(point.x)).toBeLessThan(shell.max[0] + 0.15);
        expect(Math.abs(point.y)).toBeLessThan(0.25);
        expect(point.z).toBeGreaterThan(shell.min[1] + 0.95);
        expect(point.z).toBeLessThan(shell.max[1] - 0.3);
        const wrist = step.local(RIG.heads.get(`hand_${side}`).clone().applyMatrix4(step.moves.get(`hand_${side}`)));
        expect(Math.abs(wrist.x)).toBeGreaterThan(shell.max[0] + 0.1);
    }
});

test("the back of the supplied glove sweeps across the brow with its whole surface clear of the shell", () => {
    const eyeHeight = RIG.eyes.reduce((sum, eye) => sum + eye.z, 0) / RIG.eyes.length;
    for (const voice of Object.keys(stances)) for (const posture of named.wipe_brow.postures) for (const options of [{}, {facing: 25, leanWay: -1}, {facing: -25, leanWay: 1}]) {
        const side = stanceOf(voice).busy.has("r") ? "l" : "r";
        const sign = side === "l" ? 1 : -1;
        const across = [];
        for (const u of [0.25, 0.3, 0.4, 0.525, 0.65, 0.75]) {
            const step = sample("wipe_brow", voice, u, posture, options);
            const hand = step.moves.get(`hand_${side}`);
            const back = step.local(new THREE.Vector3(sign * (glove.min[0] + glove.max[0]) / 2, -glove.min[2], (glove.min[1] + glove.max[1]) / 2).applyMatrix4(hand));
            const label = `${voice} ${posture} ${u} ${options.facing ?? 0}`;
            expect(back.z, `${label}: above the eyes`).toBeGreaterThan(eyeHeight + 0.18);
            expect(back.z, `${label}: below the crown`).toBeLessThan(eyeHeight + 0.42);
            expect(back.y, `${label}: back of glove near brow`).toBeGreaterThan(-shell.max[2] - 0.13);
            expect(back.y, `${label}: back of glove clear of brow`).toBeLessThan(-shell.max[2] - 0.03);
            expect(Math.abs(back.x), `${label}: across the forehead`).toBeLessThan(0.65);
            expect(step.pose.inUse.has(side), label).toBe(true);
            expect(step.pose.inUse.size, `${label}: other hand stays free to support its prop or seat`).toBe(1);
            for (const x of [glove.min[0], glove.max[0]]) for (const y of [glove.min[1], glove.max[1]]) for (const z of [glove.min[2], glove.max[2]]) {
                const surface = step.local(new THREE.Vector3(sign * x, -z, y).applyMatrix4(hand));
                expect(surface.y, `${label}: entire glove remains in front of the face`).toBeLessThan(-shell.max[2] - 0.03);
            }
            if (u === 0.3 || u === 0.525) across.push(back);
        }
        expect(Math.abs(across[0].x) - Math.abs(across[1].x), `${voice} ${posture}: visible sweep`).toBeGreaterThan(0.35);
        expect(Math.abs(across[0].z - across[1].z), `${voice} ${posture}: follows the brow`).toBeLessThan(0.04);
    }
});
