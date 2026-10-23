// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing} from "../src/figure/figure.js";
import {PARCEL, PILE, PUSH, UFO, behind, flightMs, pileSlot, pushStand, pushedTo, stopsOf, ufoAt} from "../src/figure/parcels.js";
import {clipFor} from "../src/domain/figureState.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("finished parcels pile up at the floor's right end, stacked three high, each new one on top or starting the next column leftward", () => {
    const slots = Array.from({length: 7}, (_, index) => pileSlot(index));
    expect(slots[0].left).toBe(-(PARCEL.inside + PARCEL.width / 2));
    expect(slots.slice(0, PILE.high).map((slot) => slot.left)).toEqual(Array(PILE.high).fill(slots[0].left));
    expect(slots.slice(0, PILE.high).map((slot) => slot.up)).toEqual([0, 17, 34]);
    expect(slots[PILE.high]).toEqual({left: slots[0].left - PARCEL.width - PILE.gap, up: 0});
    const boxes = slots.map((slot) => `${slot.left}/${slot.up}`);
    expect(new Set(boxes).size).toBe(slots.length);
});

test("the figure goes round behind a parcel, then walks it along to the pile, carrying it in front of its hands and never past the pile", () => {
    const parcel = 300;
    const to = 520;
    // standing to the parcel's right, where it was hammered, it goes round behind it first
    const round = pushStand(parcel, to, 330);
    expect(round).toBeLessThan(parcel - PUSH.reach);
    expect(pushedTo(parcel, 330, to, -1)).toBe(parcel);
    // walking left past the parcel moves it not at all
    for (let feet = 330; feet >= round; feet -= 3) expect(pushedTo(parcel, feet, to, -1)).toBe(parcel);
    expect(behind(parcel, round)).toBe(true);
    // from behind it walks on to where the parcel meets the pile, the parcel carried in front of it
    const along = pushStand(parcel, to, round);
    expect(along).toBe(to - PUSH.reach);
    let at = parcel;
    for (let feet = round; feet <= along; feet += 2) {
        at = pushedTo(at, feet, to, 1);
        expect(at).toBeLessThanOrEqual(to);
        expect(at).toBeGreaterThanOrEqual(parcel);
    }
    expect(at).toBe(to);
});

test("the UFO's beam is as wide as the pile it lifts, and parcels further apart than one beam are taken one stop at a time", () => {
    const pile = [700, 700, 700, 675, 675].map((x, index) => ({id: index + 1, x}));
    const [one] = stopsOf(pile);
    expect(stopsOf(pile)).toHaveLength(1);
    expect(one.ids.sort()).toEqual([1, 2, 3, 4, 5]);
    expect(one.x).toBeCloseTo(687.5);
    expect(one.beam).toBeGreaterThanOrEqual(700 - 675 + PARCEL.width);
    expect(stopsOf(pile.slice(0, 1))[0].beam).toBeLessThan(one.beam);
    // a parcel the figure had not pushed onto the pile in time lies too far off for the same beam
    const loose = stopsOf([...pile, {id: 6, x: 420}]);
    expect(loose.map((stop) => stop.ids.length)).toEqual([1, 5]);
    expect(loose[0].x).toBe(420);
    for (const stop of loose) expect(stop.right - stop.left + PARCEL.width).toBeLessThanOrEqual(UFO.beamMost);
});

test("the UFO flies in from far off, stops over each group with its beam on while they rise to it, and flies away", () => {
    const stops = stopsOf([{id: 1, x: 420}, {id: 2, x: 700}, {id: 3, x: 676}]);
    const floor = 768;
    const from = {x: 1200, y: 0};
    const away = {x: -100, y: 0};
    const fly = (ms) => ufoAt(stops, ms, floor, from, away);
    expect(fly(0)).toMatchObject({...from, coming: true, beam: 0, taken: 0, gone: false});
    const total = flightMs(stops.length);
    let previous = fly(0);
    const seen = [];
    for (let ms = 0; ms <= total; ms += 20) {
        const now = fly(ms);
        if (now.beam > 0.99) seen.push(now.stop);
        expect(now.taken).toBeGreaterThanOrEqual(previous.taken);
        if (now.beam > 0) expect([now.x, now.y]).toEqual([stops[now.stop].x, floor - UFO.hover]);
        if (now.beam > 0) expect(now.width).toBe(stops[now.stop].beam);
        previous = now;
    }
    expect([...new Set(seen)]).toEqual([0, 1]);
    expect(fly(UFO.enter + UFO.beamOn + UFO.lift)).toMatchObject({stop: 0, risen: 1, taken: 0});
    expect(fly(total)).toMatchObject({...away, taken: 2, gone: true});
});

test("while the UFO is here the figure stops whatever it does to watch it: its head follows it, a hand shades its eyes, and it steps back", () => {
    const watch = CLIPS.find((clip) => clip.name === "watch");
    expect(watch.cuts).toBe(true);
    // once the UFO is gone the figure carries on within a second
    expect(watch.frames / watch.fps).toBeLessThanOrEqual(1);
    const place = {posture: "stand", x: 0, y: 0};
    expect(clipFor({place, state: "running", doing: "work", watching: true}, () => true).clip).toBe("watch");
    expect(clipFor({place, state: "running", doing: "work", watching: false}, () => true).clip).toBe("work");
    for (const voice of Object.keys(stances)) {
        const posed = (sky) => {
            const pose = new Posing(RIG, "stand", 0);
            pose.sky = sky;
            watch.pose(pose, stanceOf(voice), 0);
            return pose.moves(0);
        };
        const forward = (moves) => new THREE.Vector3(0, -1, 0).transformDirection(moves.get("head"));
        // far off up to the right, then right overhead
        const right = forward(posed({at: {x: 1.6, y: -0.6}, shade: 0, back: 0}));
        expect(right.x, voice).toBeGreaterThan(0.3);
        expect(right.z, voice).toBeGreaterThan(0);
        const above = forward(posed({at: {x: 0.5, y: -0.8}, shade: 0, back: 1}));
        expect(above.z, voice).toBeGreaterThan(0.3);
        // the free hand shading the eyes is up beside the head
        const side = stanceOf(voice).free.has("r") ? "r" : "l";
        const shaded = posed({at: {x: 1.6, y: -0.6}, shade: 1, back: 0});
        const hand = new THREE.Vector3().copy(RIG.heads.get(`hand_${side}`)).applyMatrix4(shaded.get(`hand_${side}`));
        expect(hand.z, voice).toBeGreaterThan(2.4);
        // stepped back, away from the viewer
        const root = (moves) => RIG.heads.get("root").clone().applyMatrix4(moves.get("root"));
        expect(root(posed({at: {x: 0.5, y: -0.8}, shade: 0, back: 1})).y - root(posed({at: {x: 0.5, y: -0.8}, shade: 0, back: 0})).y, voice).toBeGreaterThan(0.3);
    }
});
