// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, HEAD_TURN, Posing, SHOVE, leanOf, lookToward} from "../src/figure/figure.js";
import {BLINK, CLAW, CRANE, DIGITS, HAMMER, LAYER, PARCEL, PILE, PUSH, UFO, behind, blowsLanded, brightness, craneAt, craneMs, digitsOf, flightMs, hammerMs, litAfter, phasesOf, pileSlot, prongsOf, pushStand, pushedTo, stacksOf, stopsOf, ufoAt} from "../src/figure/parcels.js";
import {GROUNDED, clipFor} from "../src/domain/figureState.js";
import {CHANGE_SECONDS} from "../src/figure/places.js";
import {carrierOf} from "../src/figure/reactions.js";
import {PILE as ANIMATIONS} from "../src/figure/pile.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("finished parcels pile up at the floor's right end, stacked three high, each new one on top or starting the next column leftward", () => {
    const slots = Array.from({length: 7}, (_, index) => pileSlot(index));
    expect(slots[0].left).toBe(-(PARCEL.inside + PARCEL.width / 2));
    expect(slots.slice(0, PILE.high).map((slot) => slot.left)).toEqual(Array(PILE.high).fill(slots[0].left));
    expect(slots.slice(0, PILE.high).map((slot) => slot.up)).toEqual([0, 24, 48]);
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

test("pushing a parcel the figure leans into it, its back angled well forward, both hands out against the parcel's near side about half way up, its feet stepping behind its hips, on the floor", () => {
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
                push.pose(pose, stanceOf(voice), (SHOVE.intro + 1) / push.frames);
                const moves = pose.moves(0);
                const at = (name) => pose.head(name, moves.get(name));
                const label = `${voice} ${posture} ${step}`;
                for (const side of ["l", "r"]) {
                    const grip = pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`));
                    expect(grip.z, label).toBeLessThan(top * 0.8);
                    expect(grip.z, label).toBeGreaterThan(top * 0.25);
                    // flat on the parcel's near side, as the parcel is drawn ahead of the figure, over its hands' backs
                    expect(Math.abs(-grip.y - near), label).toBeLessThan(0.12);
                }
                // the back bent well forward, and no foot under the floor
                const back = at("neck").sub(at("hips")).normalize();
                expect(back.z, label).toBeLessThan(Math.cos(THREE.MathUtils.degToRad(45)));
                for (const side of ["l", "r"]) expect(at(`foot_${side}`).z, label).toBeGreaterThan(-0.05);
                // the feet behind the hips, as one leaning into a push: forward is less y
                const feet = (at("foot_l").y + at("foot_r").y) / 2;
                expect(feet - at("hips").y, label).toBeGreaterThan(0.1);
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

test("each parcel is a square block of two 1U server units, a strip of its top showing, and the blocks stack each on the top of the one under it", () => {
    expect(PARCEL.width).toBe(24);
    expect(PARCEL.units).toBe(2);
    // its front is as high as it is wide, and a little of its top shows above it
    expect(PARCEL.height - PARCEL.top).toBe(PARCEL.width);
    expect(PARCEL.top).toBeGreaterThan(0);
    expect(PARCEL.top).toBeLessThan(PARCEL.width / 4);
    expect(pileSlot(1).up - pileSlot(0).up).toBe(PARCEL.height - PARCEL.top);
    // amber lights blink each a step out of the next, on for half the blink; green and red stay on
    const steps = (lit) => Array.from({length: phasesOf(lit)}, (_, phase) => [0, 1, 2, 3].map((index) => brightness(lit, phase, index)));
    expect(steps("amber")).toEqual([[1, 1, BLINK.dim, BLINK.dim], [1, BLINK.dim, BLINK.dim, 1], [BLINK.dim, BLINK.dim, 1, 1], [BLINK.dim, 1, 1, BLINK.dim]]);
    expect(steps("good")).toEqual([[1, 1, 1, 1]]);
    expect(steps("bad")).toEqual([[1, 1, 1, 1]]);
});

test("each unit keeps the lights of its own run: amber while that run goes, then green or red as it ended, for good", () => {
    const first = {lit: "amber", run: "messages:1"};
    const second = {lit: "amber", run: "messages:2"};
    // the first run passes: its unit turns green, the second's blinks on
    const passed = [{card: "messages:1", tone: "good"}];
    const [a, b] = [first, second].map((unit) => ({...unit, lit: litAfter(unit, passed)}));
    expect([a.lit, b.lit]).toEqual(["good", "amber"]);
    // the second fails: its unit turns red and the first stays green
    const failed = [{card: "messages:2", tone: "bad"}];
    const [c, d] = [a, b].map((unit) => ({...unit, lit: litAfter(unit, failed)}));
    expect([c.lit, d.lit]).toEqual(["good", "bad"]);
    // a third run ends either way: neither ended unit changes again
    for (const tone of ["good", "bad"]) expect([c, d].map((unit) => litAfter(unit, [{card: "messages:3", tone}]))).toEqual(["good", "bad"]);
    // a unit made with no run going takes the next run's end
    expect(litAfter({lit: "amber", run: ""}, [{card: "messages:4", tone: "bad"}])).toBe("bad");
    expect(litAfter({lit: "amber", run: "messages:5"}, [])).toBe("amber");
});

test("each blow sprays many 0 and 1 digits out of the dust, each its own way, flying out at its own pace and fading at its own", () => {
    let seed = 0.13;
    const random = () => (seed = (seed * 9301 + 0.49297) % 1);
    const all = [];
    for (let blow = 0; blow < 40; blow++) {
        const digits = digitsOf(random);
        expect(digits.length).toBeGreaterThanOrEqual(DIGITS.least);
        expect(digits.length).toBeLessThanOrEqual(DIGITS.most);
        all.push(...digits);
    }
    expect(DIGITS.least).toBeGreaterThanOrEqual(12);
    for (const digit of all) {
        expect(["0", "1"]).toContain(digit.text);
        // it flies away from the cloud's middle, never down through the floor
        const out = Math.hypot(digit.x + digit.dx, digit.y + digit.dy - DIGITS.middle);
        expect(out).toBeGreaterThan(Math.hypot(digit.x, digit.y - DIGITS.middle));
        expect(digit.y + digit.dy).toBeLessThan(0);
    }
    // the ways spread to both sides, and the reach, the move and the fade differ from digit to digit
    const spread = (values) => Math.max(...values) - Math.min(...values);
    expect(all.some((digit) => digit.dx < -10) && all.some((digit) => digit.dx > 10)).toBe(true);
    expect(spread(all.map((digit) => Math.hypot(digit.dx, digit.dy)))).toBeGreaterThan(20);
    expect(spread(all.map((digit) => digit.moveMs))).toBeGreaterThan(500);
    expect(spread(all.map((digit) => digit.fadeMs))).toBeGreaterThan(500);
    // a digit's fade is drawn apart from its move, so most of them fade well before or after they stop
    expect(all.filter((digit) => Math.abs(digit.moveMs - digit.fadeMs) > 100).length).toBeGreaterThan(all.length * 0.7);
});

test("the UFO takes the work away three times in four and the claw crane the fourth, picked by weight from one list", () => {
    expect(ANIMATIONS.filter((entry) => entry.when.moment === "carrier").map((entry) => [entry.name, entry.weight])).toEqual([["ufo", 3], ["crane", 1]]);
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

test("about to push, the figure first turns to face the parcel, upright, and only then leans in", () => {
    // upright through the frames the turn takes, which last at least as long as the change of facing eases, then leaning in to the full
    const push = CLIPS.find((clip) => clip.name === "push");
    expect(push.intro).toBe(SHOVE.intro);
    expect(SHOVE.turn / SHOVE.fps).toBeGreaterThanOrEqual(CHANGE_SECONDS);
    for (let frame = 0; frame <= SHOVE.turn; frame++) expect(leanOf(frame / push.frames), String(frame)).toBe(0);
    expect(leanOf((SHOVE.intro - 1) / push.frames)).toBeGreaterThan(0);
    expect(leanOf(SHOVE.intro / push.frames)).toBe(1);
    // standing behind the parcel it pushes, the figure faces it, never the viewer
    const scene = {mode: GROUNDED, place: {posture: "stand"}, state: "idle", doing: "push"};
    expect(clipFor({...scene, doingFacing: 90}, () => true)).toMatchObject({clip: "push", facing: 90});
    expect(clipFor({...scene, doingFacing: 270}, () => true)).toMatchObject({clip: "push", facing: 270});
});

test("the crane's claw comes down around the box, its hub on the stack's top, and shuts its prongs on the box's sides, the box hanging from it as it lifts", () => {
    const half = PARCEL.width / 2;
    // wide open, the tips stand clear outside the box's sides; shut, they lie on them, a pixel or two out, down past half the box's front
    for (const prong of prongsOf(1)) expect(Math.abs(prong.tip) - half).toBeGreaterThan(5);
    for (const prong of prongsOf(0)) {
        expect(Math.abs(prong.tip) - half).toBeGreaterThan(0);
        expect(Math.abs(prong.tip) - half).toBeLessThanOrEqual(2);
        expect(Math.abs(prong.top)).toBe(Math.abs(prong.tip));
        expect(prong.reach).toBeGreaterThan((PARCEL.height - PARCEL.top) / 2);
    }
    expect(prongsOf(0).map((prong) => prong.way)).toEqual([-1, 1]);
    // at the stop the chain lowers the hub onto the stack's top, the claw shuts there, and the stack lifts with the chain
    const stops = [{x: 600, high: 2 * (PARCEL.height - PARCEL.top) + PARCEL.top, ids: [1, 2]}];
    const floor = 700;
    const top = 100;
    const shut = craneAt(stops, CRANE.enter + CRANE.lower + CRANE.grab, floor, top, 300, 900);
    expect(shut.open).toBe(0);
    expect(top + shut.chain).toBeCloseTo(floor - stops[0].high, 5);
    const lifting = craneAt(stops, CRANE.enter + CRANE.lower + CRANE.grab + CRANE.lift / 2, floor, top, 300, 900);
    expect(lifting.open).toBe(0);
    expect(lifting.lifted).toBeCloseTo(shut.chain - lifting.chain, 5);
    expect(CLAW.reach).toBeLessThan(PARCEL.height);
});
