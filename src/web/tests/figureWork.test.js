// @vitest-environment node
import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import * as THREE from "three";
import {CLIPS, Posing, WORK} from "../src/figure/figure.js";

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
const STEPS = 64;

test("a running command's figure swings a hammer in its free hand, one blow a loop, never an empty arm pumping", () => {
    const clip = CLIPS.find((each) => each.name === "work");
    const heights = [];
    for (let step = 0; step <= STEPS; step++) {
        const pose = new Posing(RIG, "sit", 0);
        clip.pose(pose, STANCE, step / STEPS);
        expect(pose.props.get("work_hammer")?.bone).toBe("hand_r");
        heights.push(new THREE.Vector3(-1, 0, 0).transformDirection(pose.matrix("upper_arm_r")).z);
    }
    const turns = heights.slice(2).filter((height, index) => Math.sign(height - heights[index + 1]) !== Math.sign(heights[index + 1] - heights[index])).length;
    expect(turns).toBe(1);
    expect(heights[0]).toBeCloseTo(heights[STEPS], 6);
    // the hammer comes down quick and lifts back slower: the lowest point comes well before the middle of the loop
    const landed = heights.indexOf(Math.min(...heights));
    expect(landed / STEPS).toBeCloseTo(WORK.lands, 1);
    expect(landed).toBeLessThan(STEPS - landed);
});

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const REAL = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("on its feet the figure hammers side-on, its face toward the parcel on the floor, which shows only while it hammers", () => {
    const work = CLIPS.find((each) => each.name === "work");
    for (const voice of Object.keys(stances)) {
        for (let step = 0; step <= STEPS; step++) {
            const pose = new Posing(REAL, "stand", 0);
            work.pose(pose, stanceOf(voice), step / STEPS);
            const moves = pose.moves(0);
            const parcel = pose.props.get("code_parcel");
            const at = parcel.at.clone().applyMatrix4(moves.get(parcel.bone));
            expect(at.z, `${voice} ${step}`).toBeCloseTo(0, 6);
            // the face looks across the picture, toward the side the parcel stands on
            const facing = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("head"));
            expect(Math.abs(facing.x), `${voice} ${step}`).toBeGreaterThan(0.9);
            expect(Math.sign(facing.x)).toBe(Math.sign(at.x));
        }
        for (const posture of ["sit", "walk"]) {
            const pose = new Posing(REAL, posture, 0);
            work.pose(pose, stanceOf(voice), 0);
            expect(pose.props.has("code_parcel"), `${voice} ${posture}`).toBe(false);
        }
        for (const other of CLIPS.filter((each) => each !== work && (!each.voices || each.voices.includes(voice)))) {
            const pose = new Posing(REAL, other.postures[0], 0);
            other.pose(pose, stanceOf(voice), 0.5);
            expect(pose.props.has("code_parcel"), `${voice} ${other.name}`).toBe(false);
        }
    }
});
