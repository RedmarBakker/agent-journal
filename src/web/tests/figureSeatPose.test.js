// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, LEGS, Posing, lookToward} = await import("../src/figure/figure.js");
const {LEDGE_SLANT} = await import("../src/figure/perches.js");
const {SEAT_POSE, poseAfter, posedFacing} = await import("../src/figure/places.js");
const {GLANCE, SEATED_GLANCE, glanceAfter, glancePoint} = await import("../src/figure/looks.js");
const {FRAMED} = await import("../src/figure/frame.js");
const {seeded} = await import("./support/seeded.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "ledge_sit");
// degrees from the viewer, -180 to 180, the viewer's right positive
const signed = (degrees) => ((((degrees + 180) % 360) + 360) % 360) - 180;
const degrees = THREE.MathUtils.radToDeg;

// The seats a figure sits on: a bubble's or the dock's edge facing the viewer, the composer's slanted toward its nearer end, and a corner
// of the edge at its end, turned out along it (places.js seatAt)
const SEATS = [
    {name: "ledge", face: 0, end: false},
    {name: "composer left", face: 360 - LEDGE_SLANT, end: false},
    {name: "composer right", face: LEDGE_SLANT, end: false},
    {name: "corner right", face: 70, end: true},
    {name: "corner left", face: 290, end: true},
];

// the way the figure faces through a sit of `minutes` on a seat facing `face`, a reading every tenth of a second
function sitThrough(face, minutes, random) {
    let pose = null;
    return Array.from({length: minutes * 600}, (_, step) => {
        pose = poseAfter(pose, face, step / 10, random);
        return posedFacing(pose, step / 10);
    });
}

// the figure sat on an edge `u` of the way through its sit for `voice`, turned `facing`, looking at `at` (shares of its picture) or not
function seated(voice, facing, u, at) {
    const pose = new Posing(RIG, "sit", 0);
    LEGS.sit.under(pose);
    clip.pose(pose, stanceOf(voice), u);
    LEGS.sit.over(pose);
    if (at) lookToward(pose, at, facing);
    const moves = pose.moves(facing);
    return {at: (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone)), moves};
}

// which way the legs hang from the hips, in degrees from straight out toward the viewer
function legsWay(figure) {
    const hips = figure.at("thigh_l").add(figure.at("thigh_r")).multiplyScalar(0.5);
    const feet = figure.at("foot_l").add(figure.at("foot_r")).multiplyScalar(0.5);
    return degrees(Math.atan2(feet.x - hips.x, -(feet.y - hips.y)));
}

// which way the head faces, in degrees from straight at the viewer
const headWay = (figure) => {
    const ahead = new THREE.Vector3(0, -1, 0).transformDirection(figure.moves.get("head"));
    return degrees(Math.atan2(ahead.x, -ahead.y));
};

test("over a long sit the figure poses on its seat, turned a little either way or forward, never fully sideways but at an edge's end", () => {
    for (const seat of SEATS) {
        const facings = sitThrough(seat.face, 30, seeded(2918)).map(signed);
        const furthest = Math.max(Math.abs(signed(seat.face)), ...SEAT_POSE.turns.map(Math.abs));
        for (const [index, facing] of facings.entries()) expect(Math.abs(facing), `${seat.name} at ${index / 10}s`).toBeLessThanOrEqual(furthest + 1e-9);
        // a little to the left and to the right of the viewer, and straight at it, each for a while
        const held = (test) => facings.filter(test).length / facings.length;
        expect(held((facing) => facing < -5 && facing >= -SEAT_POSE.turns.at(-1)), `${seat.name} turned left`).toBeGreaterThan(0.05);
        expect(held((facing) => facing > 5 && facing <= SEAT_POSE.turns.at(-1)), `${seat.name} turned right`).toBeGreaterThan(0.05);
        expect(held((facing) => Math.abs(facing) < 1), `${seat.name} facing forward`).toBeGreaterThan(0.05);
        // fully sideways only on a corner, along the edge past its end
        if (seat.end) expect(held((facing) => Math.abs(facing - signed(seat.face)) < 1), `${seat.name} along the edge`).toBeGreaterThan(0.05);
        else expect(Math.max(...facings.map(Math.abs)), seat.name).toBeLessThan(45);
        // it poses now and then, easing round, never twitching from one way to the next
        const moves = facings.slice(1).map((facing, index) => Math.abs(signed(facing - facings[index])));
        expect(Math.max(...moves), `${seat.name} eases`).toBeLessThan(15);
        const poses = facings.filter((facing, index) => index > 0 && Math.abs(signed(facing - facings[index - 1])) > 0.01 && Math.abs(signed(facings[index - 1] - (facings[index - 2] ?? facings[index - 1]))) <= 0.01);
        expect(poses.length, `${seat.name} poses`).toBeGreaterThan(30 * 60 / SEAT_POSE.every[1] / 3);
        expect(poses.length, `${seat.name} poses`).toBeLessThan(30 * 60 / SEAT_POSE.every[0]);
    }
});

test("on an edge facing the viewer its legs hang over the front of what it sits on, or a little to one side, for every voice", () => {
    const facings = sitThrough(0, 10, seeded(48493));
    for (const voice of Object.keys(stances)) {
        const ways = [];
        for (let index = 0; index < facings.length; index += 50) {
            const way = legsWay(seated(voice, facings[index], (index % 320) / 320));
            ways.push(way);
            expect(Math.abs(way), `${voice} at ${index / 10}s`).toBeLessThan(30);
            // the legs go the way the body turns
            expect(Math.abs(way - signed(facings[index])), `${voice} at ${index / 10}s`).toBeLessThan(10);
        }
        expect(Math.min(...ways.map(Math.abs)), `${voice} over the front`).toBeLessThan(3);
        expect(Math.min(...ways), `${voice} a little to the left`).toBeLessThan(-8);
        expect(Math.max(...ways), `${voice} a little to the right`).toBeGreaterThan(8);
    }
});

test("seated it now and then looks a little to one side or straight at the viewer, its gaze moving between them", () => {
    const random = seeded(1060);
    let glance = null;
    const sides = [];
    for (let step = 0; step < 10 * 600; step++) {
        glance = glanceAfter(glance, step / 10, random, SEATED_GLANCE);
        if (glancePoint(glance, step / 10, {x: 0, y: 0}, 112) && sides.at(-1)?.at !== glance.at) sides.push(glance);
    }
    // all three, each many times, the gaze moving on from one to another
    for (const side of [-1, 0, 1]) expect(sides.filter((each) => each.side === side).length, `side ${side}`).toBeGreaterThan(10);
    expect(sides.filter((each, index) => index > 0 && each.side !== sides[index - 1].side).length).toBeGreaterThan(sides.length / 3);
    // seated it glances less far than standing
    expect(SEATED_GLANCE.aside).toBeLessThan(GLANCE.aside);
    for (const voice of Object.keys(stances)) {
        for (const facing of [0, 20, 340, 70]) {
            const head = seated(voice, facing, 0).at("head");
            const point = (side) => glancePoint({at: 0, side, kind: SEATED_GLANCE}, 0, {x: 56, y: (0.5 - (head.z - FRAMED.middle) / FRAMED.height) * 112}, 112);
            const looking = (side) => headWay(seated(voice, facing, 0, {x: point(side).x / 112, y: point(side).y / 112}));
            const label = `${voice} facing ${facing}`;
            // straight at the viewer however it sits, and a little either way of it
            expect(Math.abs(looking(0)), `${label} at the viewer`).toBeLessThan(8);
            if (facing === 70) continue;
            expect(looking(-1), `${label} to the left`).toBeLessThan(-8);
            expect(looking(-1), `${label} a little to the left`).toBeGreaterThan(-50);
            expect(looking(1), `${label} to the right`).toBeGreaterThan(8);
            expect(looking(1), `${label} a little to the right`).toBeLessThan(50);
        }
    }
});
