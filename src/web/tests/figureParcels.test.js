// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, HEAD_TURN, Posing, lookToward} from "../src/figure/figure.js";
import {CRANE, DIGITS, HAMMER, PARCEL, PILE, PUSH, UFO, behind, blowsLanded, craneAt, craneMs, digitsOf, flightMs, hammerMs, lightsAfter, pileSlot, pushStand, pushedTo, stacksOf, stopsOf, ufoAt} from "../src/figure/parcels.js";
import {clipFor} from "../src/domain/figureState.js";
import {CARRIERS, carrierOf} from "../src/figure/reactions.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("finished parcels pile up at the floor's right end, stacked three high, each new one on top or starting the next column leftward", () => {
    const slots = Array.from({length: 7}, (_, index) => pileSlot(index));
    expect(slots[0].left).toBe(-(PARCEL.inside + PARCEL.width / 2));
    expect(slots.slice(0, PILE.high).map((slot) => slot.left)).toEqual(Array(PILE.high).fill(slots[0].left));
    expect(slots.slice(0, PILE.high).map((slot) => slot.up)).toEqual([0, 11, 22]);
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
    expect(clipFor({place, state: "running", doing: "work", watching: "watch"}, () => true).clip).toBe("watch");
    expect(clipFor({place, state: "running", doing: "work", watching: "wave_up"}, () => true).clip).toBe("wave_up");
    expect(clipFor({place, state: "running", doing: "work", watching: ""}, () => true).clip).toBe("work");
    for (const voice of Object.keys(stances)) {
        const posed = ({at, ...sky}) => {
            const pose = new Posing(RIG, "stand", 0);
            pose.sky = sky;
            watch.pose(pose, stanceOf(voice), 0);
            lookToward(pose, at);
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

test("pushing a parcel far lower than its hands, the figure bends its knees and its back until both hands are on the parcel, feet on the floor", () => {
    const push = CLIPS.find((clip) => clip.name === "push");
    // the parcel's near side, from the figure's feet, in the figure's units: PUSH.reach pixels ahead of the feet less half a parcel, up to
    // its height, at the chat's 112-pixel figure, whose picture is 5.4 units high
    const unit = 112 / 5.4;
    const near = (PUSH.reach - PARCEL.width / 2) / unit;
    const top = PARCEL.height / unit;
    for (const voice of Object.keys(stances)) {
        for (const [posture, steps] of [["walk", 12], ["stand", 1]]) {
            for (let step = 0; step < steps; step++) {
                const pose = new Posing(RIG, posture, step / steps);
                push.pose(pose, stanceOf(voice), 0);
                const moves = pose.moves(0);
                const at = (name) => pose.head(name, moves.get(name));
                const label = `${voice} ${posture} ${step}`;
                for (const side of ["l", "r"]) {
                    const grip = pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`));
                    expect(grip.z, label).toBeLessThan(top);
                    expect(grip.z, label).toBeGreaterThan(0);
                    expect(-grip.y, label).toBeGreaterThan(near - 0.25);
                    expect(-grip.y, label).toBeLessThan(near + 0.35);
                }
                // the back bent well forward, and no foot under the floor
                const back = at("neck").sub(at("hips")).normalize();
                expect(back.z, label).toBeLessThan(Math.cos(THREE.MathUtils.degToRad(45)));
                for (const side of ["l", "r"]) expect(at(`foot_${side}`).z, label).toBeGreaterThan(-0.05);
            }
        }
    }
});

test("each parcel is hammered a random three to eight seconds, and every blow that lands on it is counted, once", () => {
    expect([HAMMER.least, HAMMER.most]).toEqual([3000, 8000]);
    expect(hammerMs(() => 0)).toBe(3000);
    expect(hammerMs(() => 0.5)).toBe(5500);
    expect(hammerMs(() => 0.999999)).toBeCloseTo(8000, 0);
    // a blow of 8 frames lands at 0.3 of its way: none before the first lands, then one a blow
    const landed = [0, 2, 2.4, 3, 10, 10.4, 11, 26.4].map((frames) => blowsLanded(frames, 8, 0.3));
    expect(landed).toEqual([0, 0, 1, 1, 1, 2, 2, 4]);
});

test("the head never turns further than HEAD_TURN from the way the body faces; a look further round turns the body the rest, after the head", () => {
    const watch = CLIPS.find((clip) => clip.name === "watch");
    const yawOf = (moves) => {
        const ahead = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("head"));
        return THREE.MathUtils.radToDeg(Math.atan2(ahead.x, -ahead.y));
    };
    for (const voice of Object.keys(stances)) {
        for (const [facing, at] of [[90, {x: 0.02, y: 0.4}], [270, {x: 0.98, y: 0.4}], [0, {x: 0.5, y: 0.3}], [90, {x: 0.9, y: 0.3}]]) {
            for (const amount of [0.3, 0.7, 1]) {
                const pose = new Posing(RIG, "stand", 0);
                watch.pose(pose, stanceOf(voice), 0);
                const body = lookToward(pose, {...at, amount}, facing);
                const label = `${voice} ${facing} ${at.x} ${amount}`;
                expect(Math.abs(yawOf(pose.moves(0))), label).toBeLessThanOrEqual(HEAD_TURN + 0.5);
                // a look behind a figure turned sideways turns its body, less than the head while the look eases in
                if (Math.abs(at.x - 0.5) > 0.4) expect(Math.abs(body), label).toBeGreaterThan(0);
                else expect(body, label).toBe(0);
            }
            // looked fully round, the head and the body turned together face the point
            const pose = new Posing(RIG, "stand", 0);
            watch.pose(pose, stanceOf(voice), 0);
            const body = lookToward(pose, {...at, amount: 1}, facing);
            const full = yawOf(pose.moves(0)) + body;
            const want = THREE.MathUtils.radToDeg(Math.atan2((at.x - 0.5) * 5.4, 1.2 + 0.0)) - facing;
            expect(Math.abs(((full - want + 540) % 360) - 180), `${voice} ${facing}`).toBeLessThan(25);
        }
    }
});

test("the parcels are flat 1U server units of the boxes' square footprint, stacked three high a unit's height apart", () => {
    expect(PARCEL.width).toBe(24);
    expect(PARCEL.height).toBeLessThan(PARCEL.width / 1.5);
    expect(pileSlot(1).up - pileSlot(0).up).toBe(PARCEL.height - 2);
});

test("a unit's lights blink amber from the moment a run starts, all turn green or red with the visor when it ends, and stay so until the next", () => {
    expect(lightsAfter("good", true, "")).toBe("amber");
    expect(lightsAfter("amber", false, "")).toBe("amber");
    expect(lightsAfter("amber", false, "good")).toBe("good");
    expect(lightsAfter("amber", true, "bad")).toBe("bad");
    // the state lingers on the run a moment after it ends, which is no new run
    expect(lightsAfter("good", false, "")).toBe("good");
});

test("each blow lets a few 0 and 1 digits out of the dust, starting about the unit and drifting in to it", () => {
    let seed = 0.13;
    const random = () => (seed = (seed * 9301 + 0.49297) % 1);
    for (let blow = 0; blow < 40; blow++) {
        const digits = digitsOf(random);
        expect(digits.length).toBeGreaterThanOrEqual(DIGITS.least);
        expect(digits.length).toBeLessThanOrEqual(DIGITS.most);
        for (const digit of digits) {
            expect(["0", "1"]).toContain(digit.text);
            expect(Math.hypot(digit.x, digit.y)).toBeGreaterThan(PARCEL.height / 2);
            expect(digit.y).toBeLessThan(0);
        }
    }
});


test("the UFO takes the work away three times in four and the claw crane the fourth, picked by weight from one list", () => {
    expect(CARRIERS).toEqual([{clip: "ufo", weight: 3}, {clip: "crane", weight: 1}]);
    const rolls = Array.from({length: 1000}, (_, index) => carrierOf(() => (index + 0.5) / 1000));
    expect(rolls.filter((by) => by === "ufo").length).toBe(750);
    expect(rolls.filter((by) => by === "crane").length).toBe(250);
    expect([carrierOf(() => 0), carrierOf(() => 0.7499), carrierOf(() => 0.75), carrierOf(() => 0.9999)]).toEqual(["ufo", "ufo", "crane", "crane"]);
});

test("the claw crane rolls in along the window's top, lowers its claw onto the stack, shuts it, lifts the stack out of the window and rolls away", () => {
    const top = 100;
    const floor = 700;
    const stops = stacksOf([0, 1, 2].map((index) => ({id: index + 1, x: 600, up: pileSlot(index).up})));
    expect(stops).toHaveLength(1);
    expect(stops[0].high).toBe(pileSlot(2).up + PARCEL.height);
    const visit = (ms) => craneAt(stops, ms, floor, top, -40, 1300);
    // rolling in from the left along the rail, the claw wound up and open
    expect(visit(0)).toMatchObject({x: -40, chain: CRANE.wound, open: 1, coming: true, lifted: 0});
    expect(visit(CRANE.enter / 2).x).toBeGreaterThan(-40);
    // over the stack the claw goes down on its chain until it meets the stack's top, then shuts
    const lowered = visit(CRANE.enter + CRANE.lower);
    expect(lowered.x).toBe(600);
    expect(top + lowered.chain).toBeCloseTo(floor - stops[0].high, 6);
    expect(lowered.open).toBe(1);
    expect(visit(CRANE.enter + CRANE.lower + CRANE.grab).open).toBe(0);
    // it lifts the stack, ever higher, until the stack is out past the window's top
    let previous = 0;
    for (let ms = CRANE.enter + CRANE.lower + CRANE.grab + 50; ms < CRANE.enter + CRANE.lower + CRANE.grab + CRANE.lift; ms += 50) {
        const now = visit(ms);
        expect(now.lifted).toBeGreaterThanOrEqual(previous);
        expect(now.x).toBe(600);
        previous = now.lifted;
    }
    expect(floor - previous - stops[0].high).toBeLessThan(top);
    // and it rolls on out at the far side, gone once its visit is over
    expect(visit(craneMs(1))).toMatchObject({x: 1300, taken: 1, gone: true});
});
