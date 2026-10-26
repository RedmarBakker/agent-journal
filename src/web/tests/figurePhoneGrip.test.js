// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {ACTS} from "../src/figure/acts.js";
import {CALL, CLIPS, LEGS, Posing, SIDES, telephoneOf} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const call = CLIPS.find((clip) => clip.name === "phone_call");
const act = ACTS.phone_call;
const seats = [["stand", 0, 0], ["sit", 0, 0], ["composed", 0, 0], ["composed", 25, 1], ["composed", -25, -1]];
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const groups = ["telephone", "telephone_handset", "telephone_cord", "telephone_poof"].map((name) => Object.assign(new THREE.Group(), {name}));
telephoneOf(...groups);
groups[1].updateMatrixWorld(true);
const grilles = Object.fromEntries(["ear", "mouth"].map((name) => {
    const point = groups[1].getObjectByName(`telephone_handset_${name}_grille`).getWorldPosition(new THREE.Vector3());
    return [name, new THREE.Vector3(point.x, -point.z, point.y)];
}));

function posed(u, voice, posture, phoneWay, facing = 0, leanWay = 0) {
    const pose = new Posing(RIG, posture);
    Object.assign(pose, {phoneWay, facing, leanWay});
    LEGS[posture]?.under(pose);
    call.pose(pose, stanceOf(voice), u * (call.frames - 1) / call.frames);
    LEGS[posture]?.over(pose);
    const moves = pose.moves(0);
    const held = pose.props.get("telephone_handset");
    const origin = held.at.clone().applyMatrix4(moves.get(held.bone));
    const {x = 0, y = 0, z = 0} = held.turn;
    const rotation = new THREE.Matrix4().extractRotation(moves.get(held.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(...[x, y, z].map(THREE.MathUtils.degToRad), "ZYX")));
    return {pose, moves, held, origin, rotation, cup: (name) => grilles[name].clone().applyMatrix4(rotation).add(origin)};
}

test("the real receiver grille follows the ear and the mouthpiece stays beside the lower face through every talking nod", () => {
    for (const voice of Object.keys(stances)) {
        for (const [posture, facing, leanWay] of seats) {
            for (const phoneWay of [-1, 1]) {
                for (const u of [0.51, 0.54, 0.58, 0.62, 0.66, 0.7]) {
                    const {pose, moves, held, cup} = posed(u, voice, posture, phoneWay, facing, leanWay);
                    const side = held.bone.at(-1);
                    const ear = new THREE.Vector3(SIDES[side] * CALL.ear[0], CALL.ear[1], CALL.ear[2]).applyMatrix4(moves.get("head"));
                    const mouth = new THREE.Vector3(SIDES[side] * 0.63, -1.05, 2.54).applyMatrix4(moves.get("head"));
                    const label = `${voice} ${posture} ${phoneWay} ${u}`;
                    expect(cup("ear").distanceTo(ear), `${label}: receiver contact`).toBeLessThan(0.025);
                    expect(cup("mouth").distanceTo(mouth), `${label}: mouthpiece by lower face`).toBeLessThan(0.16);
                    const palm = pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(held.bone));
                    expect(palm.distanceTo(cup("ear")), `${label}: hand grasps the handle below the receiver`).toBeGreaterThan(0.5);
                    expect(moves.get(held.bone).determinant(), `${label}: glove closes around the handle`).toBeCloseTo(CALL.grip, 5);
                }
            }
        }
    }
});

test("pickup and replacement keep the handset in contact with its cradle across the ownership change", () => {
    for (const voice of Object.keys(stances)) {
        for (const [posture, facing, leanWay] of seats) {
            for (const phoneWay of [-1, 1]) {
                const take = (posture === "stand" ? act : act.seated).reach[1];
                for (const u of [take, act.hang[1]]) {
                    const before = posed(u - 0.000001, voice, posture, phoneWay, facing, leanWay);
                    const after = posed(u + 0.000001, voice, posture, phoneWay, facing, leanWay);
                    const label = `${voice} ${posture} ${phoneWay} ${u}`;
                    expect(after.origin.distanceTo(before.origin), `${label}: no translation jump`).toBeLessThan(0.005);
                    const a = new THREE.Quaternion().setFromRotationMatrix(before.rotation);
                    const b = new THREE.Quaternion().setFromRotationMatrix(after.rotation);
                    expect(a.angleTo(b), `${label}: no wrist or receiver flip`).toBeLessThan(0.005);
                }
            }
        }
    }
});

test("the held handset travels continuously along its arc without stretching either arm", () => {
    for (const posture of ["stand", "sit", "composed"]) {
        for (const phoneWay of [-1, 1]) {
            let last = null;
            for (let index = 0; index <= 360; index++) {
                const u = 0.13 + 0.78 * index / 360;
                const step = posed(u, "butler", posture, phoneWay);
                if (last) expect(step.origin.distanceTo(last), `${posture} ${phoneWay} ${u}: arc continuity`).toBeLessThan(0.15);
                last = step.origin;
                for (const side of ["l", "r"]) {
                    for (const [from, to] of [["upper_arm", "forearm"], ["forearm", "hand"]]) {
                        const names = [from, to].map((name) => `${name}_${side}`);
                        const points = names.map((name) => step.pose.head(name, step.moves.get(name)));
                        expect(points[0].distanceTo(points[1])).toBeCloseTo(RIG.heads.get(names[0]).distanceTo(RIG.heads.get(names[1])), 6);
                    }
                }
            }
        }
    }
});
