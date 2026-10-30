// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, drawnPose} from "../src/figure/figure.js";
import {GAIT, RUN, strideAtDistance, travelAt} from "../src/figure/gait.js";
import {SPRINT, tripBetween, tripTo} from "../src/figure/places.js";
import {legAt} from "../src/domain/figureMotion.js";
import {TRAVELLING, clipFor} from "../src/domain/figureState.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = (name) => CLIPS.find((each) => each.name === name);
const FIGURE = {size: 112, below: 0.05};
const from = {x: 100, y: 500};
const to = {x: 400, y: 500};

test("pressing and sprinting trips plan a separate run, including a pressing trip that began at walking pace", () => {
    for (const options of [{pressing: true}, {sprinting: true}, {pace: SPRINT}]) {
        const trip = tripBetween(from, to, FIGURE.size, options);
        expect(trip).toMatchObject({running: true, pace: SPRINT});
        expect(trip.legs.filter((leg) => leg.ms > 0)).toMatchObject([{clip: "run", ramp: 140}]);
        const seated = tripTo({...from, posture: "sit"}, {...to, posture: "stand"}, FIGURE, options);
        expect(seated.running).toBe(true);
        expect(seated.legs.find((leg) => !leg.hopping).clip).toBe("run");
    }
    const normal = tripBetween(from, to, FIGURE.size);
    expect(normal.running).toBe(false);
    expect(normal.legs.find((leg) => !leg.hopping).clip).toBeUndefined();
    const hop = tripBetween(from, {...to, y: 300}, FIGURE.size, {pressing: true, random: () => 1});
    expect(hop.legs.map((leg) => leg.clip)).toEqual(["run", "jump"]);
});

test("a pressing ground leg runs instead of accelerating the walk or keeping a walking gesture", () => {
    for (const running of [{pressing: true}, {sprinting: true}, {running: true}, {pace: SPRINT}]) {
        for (const moves of [false, true]) {
            const trip = {started: true, moves, hopping: false, way: -1, ...running};
            const shown = clipFor({mode: TRAVELLING, trip, place: {posture: "stand"}, doing: "think", state: "thinking"}, () => true);
            expect(shown).toMatchObject({clip: "run", facing: 270});
            if (!moves) expect(shown.startsLeg).toBe(true);
        }
    }
});

test("ground trips start and finish at zero speed and keep their cruise speed without overshooting on short trips", () => {
    for (const pace of [1, SPRINT]) {
        for (const across of [6, 100, 600]) {
            const leg = tripBetween(from, {...from, x: from.x + across}, FIGURE.size, {pace}).legs.find((each) => !each.hopping);
            const at = (time) => legAt(leg, from, time).x;
            expect(at(-100)).toBe(from.x);
            expect(at(leg.ms + 100)).toBe(from.x + across);
            expect(at(1) - at(0)).toBeLessThan(0.001);
            expect(at(leg.ms) - at(leg.ms - 1)).toBeLessThan(0.001);
            for (let time = 1; time <= leg.ms; time += 5) {
                const step = at(time) - at(time - 1);
                expect(step).toBeGreaterThanOrEqual(-1e-9);
                expect(step).toBeLessThanOrEqual(90 * pace / 1000 + 1e-8);
            }
            expect(travelAt(leg.ms / 2, leg.ms, leg.ramp)).toBeCloseTo(0.5, 10);
        }
    }
});

test("run soles stay fixed on the page throughout each support, including acceleration and braking", () => {
    for (const size of [112, 224]) {
        for (const way of [-1, 1]) {
            const leg = tripBetween(from, {...from, x: from.x + way * 300}, size, {pressing: true}).legs.find((each) => !each.hopping);
            const planted = new Map();
            for (let elapsed = 0; elapsed <= leg.ms; elapsed += 5) {
                const distance = Math.abs(legAt(leg, from, elapsed).x - from.x);
                const cycle = strideAtDistance(distance, size, true);
                const facing = way > 0 ? 90 : 270;
                const {pose} = drawnPose(RIG, stanceOf("butler"), clip("run"), cycle * clip("run").frames, facing);
                for (const [side, offset] of [["l", 0], ["r", 0.5]]) {
                    if ((cycle + offset) % 1 >= RUN.planted) continue;
                    const foot = pose.head(`foot_${side}`, pose.moves(facing).get(`foot_${side}`));
                    const page = foot.x * size / 5.4 + distance * way;
                    const key = `${side}/${Math.floor(cycle + offset)}`;
                    if (planted.has(key)) expect(page, `${key} at ${elapsed}ms`).toBeCloseTo(planted.get(key), 6);
                    else planted.set(key, page);
                    expect(foot.z).toBeCloseTo(RIG.heads.get(`foot_${side}`).z, 7);
                }
            }
        }
    }
});

test("the run has longer strides, a forward lean, bent pumping arms and an airborne phase of its own", () => {
    expect(RUN.length).toBeGreaterThan(GAIT.length);
    expect(RUN.planted).toBeLessThan(0.5);
    const poses = (name) => Array.from({length: 100}, (_, frame) => drawnPose(RIG, stanceOf("butler"), clip(name), frame / 100 * clip(name).frames, 0).pose);
    const walk = poses("walk"), run = poses("run");
    const along = (poses) => poses.map((pose) => pose.head("foot_l", pose.matrix("foot_l")).y);
    const span = (values) => Math.max(...values) - Math.min(...values);
    expect(span(along(run))).toBeGreaterThan(span(along(walk)) * 1.15);
    const chest = (pose) => new THREE.Vector3(0, 0, 1).transformDirection(pose.matrix("chest"));
    expect(chest(run[0]).y).toBeLessThan(chest(walk[0]).y - 0.1);
    const hands = run.map((pose) => pose.head("hand_l", pose.matrix("hand_l")).z);
    expect(span(hands)).toBeGreaterThan(0.7);
    expect(run.some((pose) => ["l", "r"].every((side) => pose.head(`foot_${side}`, pose.matrix(`foot_${side}`)).z > RIG.heads.get(`foot_${side}`).z + 0.005))).toBe(true);
});

test("the run loops without a seam and all five voices stay within the unchanged leg reach", () => {
    const running = clip("run");
    for (const voice of Object.keys(stances)) {
        const stance = stanceOf(voice);
        const first = drawnPose(RIG, stance, running, 0, 0).pose.moves(0);
        const last = drawnPose(RIG, stance, running, running.frames, 0).pose.moves(0);
        for (const name of RIG.order) {
            for (let i = 0; i < 16; i++) expect(last.get(name).elements[i], `${voice}/${name}`).toBeCloseTo(first.get(name).elements[i], 9);
        }
        for (let frame = 0; frame <= 200; frame++) {
            const {pose} = drawnPose(RIG, stance, running, frame / 200 * running.frames, 0);
            expect([...pose.moves(0).values()].every((matrix) => matrix.elements.every(Number.isFinite)), `${voice}/${frame}`).toBe(true);
        }
    }
});

test("walking and running feet meet and leave the floor with continuous position and velocity", () => {
    const delta = 1e-5;
    for (const [name, gait] of [["walk", GAIT], ["run", RUN]]) {
        const footAt = (phase) => {
            const {pose} = drawnPose(RIG, stanceOf("butler"), clip(name), phase * clip(name).frames, 0);
            return pose.head("foot_l", pose.matrix("foot_l"));
        };
        for (const phase of [0, gait.planted, 1]) {
            const at = footAt(phase);
            const before = at.clone().sub(footAt(phase - delta)).divideScalar(delta);
            const after = footAt(phase + delta).sub(at).divideScalar(delta);
            expect(before.distanceTo(after), `${name} phase ${phase}`).toBeLessThan(0.002);
        }
    }
});
