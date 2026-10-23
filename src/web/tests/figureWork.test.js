// @vitest-environment node
import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import * as THREE from "three";
import {CLIPS, Posing, TOOLS, WORK, blowsLandAt} from "../src/figure/figure.js";
import {PARCEL, workLook} from "../src/figure/parcels.js";
import {canSwitch} from "../src/figure/timeline.js";

// a rig whose every bone stands at rest, the arms straight out to the sides as Blender's rig holds them, z up; it has no
// leg lengths, so the figure is posed seated
const atRest = (make) => ({get: () => make(), has: () => true, set() {}, forEach() {}, *[Symbol.iterator]() {}});
const RIG = {
    parents: atRest(() => ""),
    heads: atRest(() => new THREE.Vector3()),
    tails: atRest(() => new THREE.Vector3(0, 0, 0.1)),
    rest: atRest(() => new THREE.Matrix4()),
    along: {...atRest(() => new THREE.Vector3(1, 0, 0)), get: (name) => new THREE.Vector3(name.endsWith("_r") ? -1 : 1, 0, 0)},
    order: [],
    eyes: [],
};
const STANCE = {voice: "butler", level: new Set(["l"]), busy: new Set(["l"]), carried: new Set(), free: new Set(["r"]), tablet: new Set(), cloth: new Set(), shield: new Set()};
// a few poses for each blow, enough to see each come down and lift back
const STEPS_A_BLOW = 16;

test("the hammering is one blow a loop, so it can stop after any blow, each coming down quick and lifting back slower", () => {
    const clip = CLIPS.find((each) => each.name === "work");
    expect([WORK.blows, clip.frames]).toEqual([1, WORK.blowFrames]);
    expect([clip.loops, Boolean(clip.interruptible), Boolean(clip.leaves)]).toEqual([true, false, false]);
    for (let frame = 1; frame < clip.frames; frame++) expect(canSwitch(clip, frame, frame - 1), `${frame}`).toBe(false);
    expect(canSwitch(clip, clip.frames, clip.frames - 1)).toBe(true);
    const steps = WORK.blows * STEPS_A_BLOW;
    const heights = [];
    for (let step = 0; step <= steps; step++) {
        const pose = new Posing(RIG, "sit", 0);
        clip.pose(pose, STANCE, step / steps);
        expect(pose.props.get("work_hammer")?.bone).toBe("hand_r");
        heights.push(new THREE.Vector3(-1, 0, 0).transformDirection(pose.matrix("upper_arm_r")).z);
    }
    expect(heights[0]).toBeCloseTo(heights[steps], 6);
    for (let blow = 0; blow < WORK.blows; blow++) {
        const one = heights.slice(blow * STEPS_A_BLOW, (blow + 1) * STEPS_A_BLOW + 1);
        const turns = one.slice(2).filter((height, index) => Math.sign(height - one[index + 1]) !== Math.sign(one[index + 1] - one[index])).length;
        expect(turns, `${blow}`).toBe(1);
        const landed = one.indexOf(Math.min(...one));
        expect(landed / STEPS_A_BLOW, `${blow}`).toBeCloseTo(WORK.lands, 1);
        expect(landed, `${blow}`).toBeLessThan(STEPS_A_BLOW - landed);
    }
});

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const REAL = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("on its feet the figure hammers side-on, its face toward the side its blows land on, where the page stands the parcel", () => {
    const work = CLIPS.find((each) => each.name === "work");
    expect(work.postures).not.toContain("walk");
    for (const voice of Object.keys(stances)) {
        const lands = blowsLandAt(stanceOf(voice));
        expect(Math.abs(lands), voice).toBeGreaterThan(0.15);
        expect(Math.abs(lands), voice).toBeLessThan(0.4);
        for (let step = 0; step <= 64; step++) {
            const pose = new Posing(REAL, "stand", 0);
            work.pose(pose, stanceOf(voice), step / 64);
            const facing = new THREE.Vector3(0, -1, 0).transformDirection(pose.moves(0).get("head"));
            expect(Math.abs(facing.x), `${voice} ${step}`).toBeGreaterThan(0.9);
            expect(Math.sign(facing.x), `${voice} ${step}`).toBe(Math.sign(lands));
            expect([...pose.props.keys()], `${voice} ${step}`).toEqual(["work_hammer"]);
        }
    }
});

// where the hammer's head is in the figure's units, its prop held as figure.js heldPropOf places it: on the bone that carries it, turned as
// the hand is and then as the prop is, the head the handle's length past the grip
function hammerHead(pose, moves) {
    const held = pose.props.get("work_hammer");
    const radians = (degrees) => (degrees * Math.PI) / 180;
    const turned = new THREE.Matrix4().extractRotation(moves.get(held.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(radians(held.turn.x || 0), radians(held.turn.y || 0), radians(held.turn.z || 0), "ZYX")));
    return held.at.clone().applyMatrix4(moves.get(held.bone)).add(new THREE.Vector3(0, 0, TOOLS.hammer.handleLength - TOOLS.hammer.gripFrom).applyMatrix4(turned));
}

test("the figure hammers from a little further back than it did, and every blow still comes down on the box's top where the page sets it", () => {
    const work = CLIPS.find((each) => each.name === "work");
    // the box's top in the figure's units over its feet, at the chat's 112-pixel picture of 5.4 units
    const top = (PARCEL.height * 5.4) / 112;
    for (const voice of Object.keys(stances)) {
        const lands = blowsLandAt(stanceOf(voice));
        // further from the feet than the 0.256 of the picture it stood at before, some five pixels more at the chat's size
        expect(Math.abs(lands) * 112, voice).toBeGreaterThan(0.256 * 112 + 4);
        // the hammer's head comes down through the box's top within the box's width, where the page stands it
        const heads = Array.from({length: 65}, (_, step) => {
            const pose = new Posing(REAL, "stand", 0);
            work.pose(pose, stanceOf(voice), step / 64);
            return hammerHead(pose, pose.moves(0));
        });
        const crossing = heads.find((head, step) => step && head.z <= top && heads[step - 1].z > top);
        expect(crossing, voice).toBeTruthy();
        expect(Math.abs(crossing.x - lands * 5.4), voice).toBeLessThan((PARCEL.width / 2) * (5.4 / 112));
    }
});

test("while it builds, pushes or stacks a box the figure looks at that box, and never at a progress bar", () => {
    const xOf = (box) => 300 + box.along;
    // hammering, pushing and hopping it up onto the pile: the top of the box in hand, where it is now
    for (const state of ["building", "built"]) {
        for (const up of [0, 24]) {
            const parcels = [{along: 40, state: "piled", up: 0}, {along: 120, state, up}];
            expect(workLook(parcels, true, xOf, 600), `${state} ${up}`).toEqual({at: {x: 420, y: 600 - up - PARCEL.height}});
        }
    }
    // setting out to build one, before it is begun: no look at all, so nothing turns its head to a bar
    expect(workLook([{along: 40, state: "piled", up: 0}], true, xOf, 600)).toEqual({at: null});
    // with no box in hand and none to build the work holds no look, and the bar may have it
    expect(workLook([{along: 40, state: "piled", up: 0}], false, xOf, 600)).toBe(null);
});
