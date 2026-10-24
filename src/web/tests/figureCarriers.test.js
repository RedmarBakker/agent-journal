// @vitest-environment node
import * as THREE from "three";
import {expect, test} from "vitest";

const {ENDS, GRAB, PARCEL, UFO, beamOf, boxTop, grabMs, grabSpan, grabberAt, grabsOf, kindsOf, pileSlot, ufoAt, stopsOf} = await import("../src/figure/parcels.js");
const {SAUCER, lightSaucer, saucerOf} = await import("../src/figure/figure.js");
const {FRAMED} = await import("../src/figure/frame.js");

const seeded = (seed) => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
const SCENE = {top: 100, floor: 700, right: 1280};
// the crane coming in from the right or the left of the window
const sides = [{...SCENE, from: 1320, away: -40}, {...SCENE, from: -40, away: 1320}];
// a pile of `count` boxes at the floor's right end, and a loose box or two further along
const pileOf = (count) => Array.from({length: count}, (_, index) => ({id: index + 1, x: 1180 + pileSlot(index).left, up: pileSlot(index).up}));
const loose = [{id: 20, x: 420, up: 0}, {id: 21, x: 760, up: 0}];
const plans = [];
for (let seed = 1; seed <= 40; seed++) for (const scene of sides) for (const items of [pileOf(1), pileOf(3), [...pileOf(4), loose[0]], [...pileOf(6), ...loose]]) plans.push({scene, items, grabs: grabsOf(items, scene, seeded(seed))});
const where = (grab, scene, box = grab) => ({...scene, box: {x: box.x, top: boxTop(box, scene.floor)}});

test("the crane sends one grabber for each box waiting, each lifting its own box and no other, every one done by the visit's end", () => {
    for (const {scene, items, grabs} of plans) {
        expect(grabs.map((grab) => grab.id).sort((a, b) => a - b)).toEqual(items.map((box) => box.id).sort((a, b) => a - b));
        const end = Math.max(...grabs.map((grab) => grab.start + grabMs(grab, scene)));
        for (const grab of grabs) expect(grabberAt(grab, end + 1, where(grab, scene)).done).toBe(true);
    }
});

test("no two grabbers are ever at the same place along the window at the same moment, so one whose box lies in another's way waits its turn", () => {
    for (const {scene, grabs} of plans) {
        const end = Math.max(...grabs.map((grab) => grab.start + grabMs(grab, scene)));
        for (let ms = 0; ms <= end; ms += 25) {
            const spans = grabs.map((grab) => grabSpan(grab, ms, scene)).filter(Boolean);
            for (const [index, one] of spans.entries()) for (const other of spans.slice(index + 1)) expect(one[0] < other[1] && other[0] < one[1], `at ${ms} ms`).toBe(false);
        }
    }
    // several are out at once all the same, following one another in
    const busy = plans.filter(({scene, grabs}) => grabs.some((grab, index) => grabs.slice(index + 1).some((other) => other.start < grab.start + grabMs(grab, scene))));
    expect(busy.length).toBeGreaterThan(plans.length / 4);
});

test("a box with another on it waits until that one is lifted out of the way, and the arm waits for every box between it and the right edge", () => {
    for (const {scene, items, grabs} of plans) {
        const of = new Map(grabs.map((grab) => [grab.id, grab]));
        const outOfTheWay = (grab) => {
            for (let ms = grab.start; ; ms += 25) {
                const at = grabberAt(grab, ms, where(grab, scene));
                if (at.done || at.lifted >= PARCEL.height * 3 || at.carried > 0) return ms;
            }
        };
        for (const box of items) {
            const above = items.filter((other) => Math.abs(other.x - box.x) < PARCEL.width && other.up > box.up);
            for (const other of above) expect(of.get(box.id).start).toBeGreaterThanOrEqual(outOfTheWay(of.get(other.id)));
            if (of.get(box.id).kind !== "arm") continue;
            const between = items.filter((other) => other.x > box.x && Math.abs(other.up - box.up) < PARCEL.height);
            for (const other of between) expect(of.get(box.id).start).toBeGreaterThanOrEqual(outOfTheWay(of.get(other.id)));
        }
    }
});

test("each cable lets out as far as its own box is when it gets there, and the arm's rod shoots out to its own box's side and pulls it out past the edge", () => {
    for (const {scene, grabs} of plans.slice(0, 40)) {
        for (const grab of grabs) {
            const grips = (at) => at.open < 1;
            let gripped = null;
            for (let ms = grab.start; !gripped; ms += 10) {
                const at = grabberAt(grab, ms, where(grab, scene));
                if (grips(at)) gripped = at;
            }
            if (grab.kind === "arm") {
                expect(gripped.tip).toBeCloseTo(grab.x + PARCEL.width / 2 + ENDS.arm.clear, 6);
                expect(gripped.y).toBeCloseTo(boxTop(grab, scene.floor) + PARCEL.height / 2, 6);
                const last = grabberAt(grab, grab.start + grabMs(grab, scene) - 1, where(grab, scene));
                expect(grab.x + last.carried - PARCEL.width / 2).toBeGreaterThan(scene.right - 2);
            } else {
                expect(scene.top + gripped.chain).toBeCloseTo(boxTop(grab, scene.floor) - ENDS[grab.kind].clear, 6);
                expect(gripped.x).toBeCloseTo(grab.x, 6);
            }
        }
    }
    // worked out on the spot: a box found higher than when the crane set off is reached where it is now
    const [grab] = grabsOf(pileOf(1), sides[0], () => 0.5);
    const enter = Math.abs(grab.x - grab.from) / GRAB.zip;
    const higher = {x: grab.x, top: boxTop(grab, SCENE.floor) - 40};
    expect(SCENE.top + grabberAt(grab, enter + GRAB.lower, {...sides[0], box: higher}).chain).toBeCloseTo(higher.top - ENDS.claw.clear, 6);
});

test("the claw always takes a single box; with several, the kinds are drawn at random, the arm never taking them all, and never the same sequence twice running", () => {
    for (let seed = 1; seed <= 200; seed++) expect(kindsOf(1, seeded(seed))).toEqual(["claw"]);
    const drawn = new Set();
    for (let seed = 1; seed <= 300; seed++) {
        for (const count of [2, 3, 5, 8]) {
            const kinds = kindsOf(count, seeded(seed));
            kinds.forEach((kind) => drawn.add(kind));
            expect(kinds.filter((kind) => kind === "arm").length, `${count} boxes`).toBeLessThanOrEqual(Math.floor(count / 2));
            expect(kindsOf(count, seeded(seed), kinds).join()).not.toBe(kinds.join());
        }
    }
    expect([...drawn].sort()).toEqual(["arm", "claw", "cup", "magnet"]);
    // the arm is the quickest of them
    const scene = sides[0];
    const [box] = pileOf(1);
    const time = (kind) => grabMs({...box, kind, from: scene.from, away: scene.away, pace: 1, y: 300, start: 0}, scene);
    for (const kind of ["claw", "cup", "magnet"]) expect(time("arm"), kind).toBeLessThan(time(kind));
});

test("the UFO is drawn in 3D as the figure is, three quarters of the figure's picture across, its rim lights blinking in turn and its beam reaching the boxes from its belly", () => {
    const SIZE = 112;
    expect(UFO.width).toBeGreaterThanOrEqual(0.7 * SIZE);
    const perPixel = FRAMED.height / SIZE;
    const saucer = saucerOf(perPixel);
    // a solid as wide as it is deep, a saucer turned round its axis, not a flat picture
    const size = new THREE.Vector3();
    new THREE.Box3().setFromObject(saucer.scene.getObjectByName("saucer").children.find((part) => part.name === "saucer_hull")).getSize(size);
    expect(size.x / perPixel).toBeCloseTo(UFO.width, 0);
    expect(size.z).toBeGreaterThan(size.x * 0.4);
    // every part shaded and outlined as the figure's own are
    const parts = saucer.scene.getObjectByName("saucer").children;
    expect(parts.map((part) => part.name)).toEqual(expect.arrayContaining(["saucer_hull", "saucer_band", "saucer_dome", "saucer_lamp", "saucer_light_0"]));
    for (const part of parts) {
        expect(part.material.type, part.name).toBe("ShaderMaterial");
        expect(part.children.some((hull) => hull.material.side === THREE.BackSide), part.name).toBe(true);
    }
    // the lights run round the rim: over the blink's steps each is lit once
    const lit = Array.from({length: SAUCER.lights}, () => 0);
    for (let phase = 0; phase < UFO.blink; phase++) {
        lightSaucer(saucer, phase);
        saucer.lights.forEach((light, index) => (lit[index] += light.material.uniforms.colour.value.length() > new THREE.Vector3(...new THREE.Color(SAUCER.colours.dark).toArray()).length() ? 1 : 0));
    }
    expect(lit).toEqual(Array.from({length: SAUCER.lights}, () => 1));
    // the lamp under its belly is where the beam leaves, UFO belly pixels under its middle, and the beam reaches down to the floor the boxes stand on
    const lamp = new THREE.Vector3().setFromMatrixPosition(saucer.scene.getObjectByName("saucer_lamp").matrixWorld);
    expect((FRAMED.middle - lamp.y) / perPixel).toBeCloseTo(UFO.belly, 6);
    const floor = 700;
    const stops = stopsOf([{id: 1, x: 600}]);
    const over = ufoAt(stops, UFO.enter + UFO.beamOn, floor, {x: 1400, y: 0}, {x: -100, y: 0});
    const beam = beamOf(over, floor);
    expect([over.beam, beam.top + beam.reach]).toEqual([1, floor]);
    expect(beam.top).toBe(over.y + UFO.belly);
});
