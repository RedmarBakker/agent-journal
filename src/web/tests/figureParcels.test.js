// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, HEAD_TURN, Posing, SHOVE, blowsLandAt, leanOf, lookToward} from "../src/figure/figure.js";
import {BLINK, BUILD, CLAW, CLAW_CLEARANCE, CRANE, DIGITS, HAMMER, IDLE_CLIPS, LAYER, PARCEL, PILE, answeredWith, pushWaits, PUSH, UFO, behind, blowsLanded, brightness, craneAt, craneMs, digitsOf, flightMs, hammerMs, litAfter, phasesOf, pileSlot, prongsOf, pushStand, pushedTo, stacksOf, stopsOf, testRuns, ufoAt, unitsAfter, buildRunAt} from "../src/figure/parcels.js";
import {GROUNDED, clipFor} from "../src/domain/figureState.js";
import {CHANGE_SECONDS, tripTo} from "../src/figure/places.js";
import {carrierOf} from "../src/figure/reactions.js";
import {PILE as ANIMATIONS, SEQUENCES} from "../src/figure/pile.js";
import {headYaw} from "./support/headYaw.js";

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

test("pushing a box is a normal push: leaning in 20 to 30 degrees, both hands flat on the box's near side part way up it, the head behind the box and never over its top, the feet stepping behind the hips, on the floor", () => {
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
                // the body leaning in from the hips to the neck 20 to 30 degrees from upright, forward, which is less y
                const back = at("neck").sub(at("hips"));
                const lean = THREE.MathUtils.radToDeg(Math.atan2(-back.y, back.z));
                expect(lean, label).toBeGreaterThanOrEqual(20);
                expect(lean, label).toBeLessThanOrEqual(30);
                for (const side of ["l", "r"]) {
                    const grip = pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`));
                    // on the box's side, part way up it, never on its top or down at the floor
                    expect(grip.z, label).toBeLessThan(top * 0.85);
                    expect(grip.z, label).toBeGreaterThan(top * 0.4);
                    // flat on its near side, as the parcel is drawn ahead of the figure, over its hands' backs
                    expect(Math.abs(-grip.y - near), label).toBeLessThan(0.12);
                }
                // the head behind the box: its face, the front of the visor, no further forward than the box's near side and a little, and
                // all of the head well above the box's top, so it never hangs over it
                const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye.clone().applyMatrix4(moves.get("head"))), new THREE.Vector3()).multiplyScalar(1 / RIG.eyes.length);
                expect(-eyes.y, label).toBeLessThan(near + 0.15);
                expect(at("neck").z, label).toBeGreaterThan(top + 0.3);
                // the feet on the floor and behind the hips, as one leaning into a push
                for (const side of ["l", "r"]) expect(at(`foot_${side}`).z, label).toBeGreaterThan(-0.05);
                const feet = (at("foot_l").y + at("foot_r").y) / 2;
                expect(feet - at("hips").y, label).toBeGreaterThan(0.05);
            }
        }
    }
});

test("each parcel is hammered a random four to ten seconds a stretch, and every blow that lands on it is counted, once", () => {
    expect([HAMMER.least, HAMMER.most]).toEqual([4000, 10000]);
    expect(hammerMs(() => 0)).toBe(4000);
    expect(hammerMs(() => 0.5)).toBe(7000);
    expect(hammerMs(() => 0.999999)).toBeCloseTo(10000, 0);
    // a blow of 8 frames lands at 0.3 of its way: none before the first lands, then one a blow
    const landed = [0, 2, 2.4, 3, 10, 10.4, 11, 26.4].map((frames) => blowsLanded(frames, 8, 0.3));
    expect(landed).toEqual([0, 0, 1, 1, 1, 2, 2, 4]);
});

test("the head never turns further than HEAD_TURN from the way the body faces; a look further round turns the body the rest, after the head", () => {
    const watch = CLIPS.find((clip) => clip.name === "watch");
    for (const voice of Object.keys(stances)) {
        for (const [facing, at] of [[90, {x: 0.02, y: 0.4}], [270, {x: 0.98, y: 0.4}], [0, {x: 0.5, y: 0.3}], [90, {x: 0.9, y: 0.3}]]) {
            for (const amount of [0.3, 0.7, 1]) {
                const pose = new Posing(RIG, "stand", 0);
                watch.pose(pose, stanceOf(voice), 0);
                const body = lookToward(pose, {...at, amount}, facing);
                const label = `${voice} ${facing} ${at.x} ${amount}`;
                expect(Math.abs(headYaw(pose.moves(0))), label).toBeLessThanOrEqual(HEAD_TURN + 0.5);
                // a look behind a figure turned sideways turns its body, less than the head while the look eases in
                if (Math.abs(at.x - 0.5) > 0.4) expect(Math.abs(body), label).toBeGreaterThan(0);
                else expect(body, label).toBe(0);
            }
            // looked fully round, the head and the body turned together face the point
            const pose = new Posing(RIG, "stand", 0);
            watch.pose(pose, stanceOf(voice), 0);
            const body = lookToward(pose, {...at, amount: 1}, facing);
            const full = headYaw(pose.moves(0)) + body;
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
    expect(top + lowered.chain).toBeCloseTo(floor - stops[0].high - CLAW_CLEARANCE, 6);
    expect(lowered.open).toBe(1);
    expect(visit(CRANE.enter + CRANE.lower + CRANE.hover + CRANE.grab).open).toBe(0);
    // it lifts the stack, ever higher, until the stack is out past the window's top
    let previous = 0;
    for (let ms = CRANE.enter + CRANE.lower + CRANE.hover + CRANE.grab + 50; ms < CRANE.enter + CRANE.lower + CRANE.hover + CRANE.grab + CRANE.lift; ms += 50) {
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
    const shut = craneAt(stops, CRANE.enter + CRANE.lower + CRANE.hover + CRANE.grab, floor, top, 300, 900);
    expect(shut.open).toBe(0);
    expect(top + shut.chain).toBeCloseTo(floor - stops[0].high - CLAW_CLEARANCE, 5);
    const lifting = craneAt(stops, CRANE.enter + CRANE.lower + CRANE.hover + CRANE.grab + CRANE.lift / 2, floor, top, 300, 900);
    expect(lifting.open).toBe(0);
    expect(lifting.lifted).toBeCloseTo(shut.chain - lifting.chain, 5);
    expect(CLAW.reach).toBeLessThan(PARCEL.height);
});

test("a box built, the figure goes straight round behind it and pushes, in one move: no look about, no act of its own and no standing still between", () => {
    const built = [{id: 1, state: "built"}];
    // the moments it answers meanwhile: none of its idle ones, the looks about and the breaks from the work, but the journal's as ever
    const moments = [{beat: "standing", time: 1}, {beat: "building", time: 1}, {beat: "work_done", time: 1}, {beat: "tests_passed", time: 1}];
    expect(pushWaits(built)).toBe(true);
    expect(answeredWith(moments, built).map((moment) => moment.beat)).toEqual(["tests_passed"]);
    expect(answeredWith(moments, [{id: 1, state: "piled"}])).toEqual(moments);
    // and none of their clips waits to play: the looks about are idle clips, a celebration is not
    for (const name of ["look_left", "look_right", "look_up", "wipe_brow"]) expect(IDLE_CLIPS.has(name), name).toBe(true);
    expect(IDLE_CLIPS.has("joy")).toBe(false);
    // from where it hammered, either side of the box, it walks straight round behind it, one stroll on the floor, and from there pushes it
    // along to the pile
    const figure = {size: 112, below: 0.05};
    const parcel = 400;
    const pile = 600;
    // where it hammers from, the box's middle as far from its feet as its blows land, at the chat's 112-pixel figure
    const hammers = Math.abs(blowsLandAt(stanceOf("butler"))) * figure.size;
    const feet = parcel + hammers;
    const stand = pushStand(parcel, pile, feet);
    expect(behind(parcel, stand)).toBe(true);
    const legs = tripTo({x: feet, y: 700, posture: "stand"}, {x: stand, y: 700, posture: "stand"}, figure).legs;
    expect(legs.filter((leg) => leg.hopping && leg.ms > 0)).toEqual([]);
    expect(pushStand(parcel, pile, stand)).toBe(pile - PUSH.reach);
    // hammering on the box's near side already, it pushes from where it stands
    expect(pushStand(parcel, pile, parcel - hammers)).toBe(pile - PUSH.reach);
});

test("a running chat mark titled with the word test builds boxes one after another from 5 seconds in, and the wait for the next is counted from its end", () => {
    // a mark as the server writes it, its guesses made from its title
    const mark = (key, label, time, active = true) => ({key, label, time, active, process: true, watch: null, guesses: {test: label.toLowerCase().includes("test")}});
    // a look every second from `from` to `to` with the marks `cardsAt(now)` gives, a box taking ten seconds from its start to the pile; the
    // seconds each box was begun at
    const run = (memory, cardsAt, from, to, units = null) => {
        const begun = [];
        for (let now = from; now <= to; now++) {
            units = unitsAfter(units, buildRunAt(cardsAt(now), null, now), memory, now, () => 0);
            if (units?.granted && (!begun.length || now - begun.at(-1) >= 10)) begun.push(now);
        }
        return {begun, units};
    };
    // a run of a few seconds builds nothing and starts no wait
    const short = new Map();
    expect(run(short, (now) => [mark("a", "Running tests: pytest", 0, now < 4)], 0, 30).begun).toEqual([]);
    expect(short.has("unit")).toBe(false);
    // one titled with the word test, in any case, whatever the tool, builds from 5 seconds in, one box after another while it goes
    for (const label of ["Running tests: journal suite", "npm test", "go test ./...", "TEST run"]) {
        const {begun} = run(new Map(), (now) => [mark("a", label, 0, now < 60)], 0, 120);
        expect(begun[0], label).toBe(BUILD.after);
        expect(begun.length, label).toBeGreaterThanOrEqual(5);
        expect(Math.max(...begun), label).toBeLessThan(60);
    }
    // one without the word, or one that has ended, builds nothing
    expect(testRuns([mark("a", "npm run build", 0), mark("b", "Running tests", 0, false), {...mark("c", "go test", 0), process: false}])).toEqual([]);
    expect(testRuns([{...mark("d", "watch tests", 0), process: false, watch: {figure: "", ending: ""}}]).map((card) => card.key)).toEqual(["d"]);
    expect(run(new Map(), () => [mark("a", "Running lint: ruff", 0)], 0, 60).begun).toEqual([]);
    // the wait between boxes starts once the run has ended: a run begun just after waits until three minutes past the first one's end
    const memory = new Map();
    const first = run(memory, (now) => [mark("a", "npm test", 0, now < 60)], 0, 61);
    expect(memory.get("unit")).toBe(60);
    const second = run(memory, (now) => [mark("b", "npm test", 62)], 62, 300, first.units);
    expect(second.begun[0]).toBe(60 + SEQUENCES.build.cooldown);
});

test("pushing, the head looks ahead past the box, raised against the lean: never nodded down over the box, turned or tilted by itself, and no look turns it", () => {
    const clip = CLIPS.find((each) => each.name === "push");
    // it keeps its own look: the page's looks and the turn toward the viewer leave its head alone
    expect(clip.ownLook).toBe(true);
    const degrees = (a, b) => THREE.MathUtils.radToDeg(a.angleTo(b));
    for (const voice of Object.keys(stances)) {
        for (const posture of clip.postures) {
            for (let frame = 0; frame < clip.frames; frame++) {
                const label = `${voice} ${posture} ${frame}`;
                const pose = new Posing(RIG, posture, frame / clip.frames);
                clip.pose(pose, stanceOf(voice), frame / clip.frames);
                const moves = pose.moves(0);
                const way = (name, axis) => new THREE.Vector3(...axis).transformDirection(moves.get(name)).normalize();
                // its face no further round or over than the chest's: the same way across, the same roll
                const [face, chest] = [way("head", [0, -1, 0]), way("chest", [0, -1, 0])];
                expect(Math.abs(face.x - chest.x), label).toBeLessThan(0.05);
                expect(Math.abs(way("head", [1, 0, 0]).z - way("chest", [1, 0, 0]).z), label).toBeLessThan(0.05);
                // and leaning in, it looks ahead, about level, never down over the box nor up at the sky
                if (leanOf(frame / clip.frames) > 0.5) expect(Math.abs(face.z), label).toBeLessThan(0.2);
            }
        }
    }
});

test("each stretch of hammering takes four to ten seconds, the pause before the next varies with now and then a wait of two seconds or more, and each is begun at a new spot", async () => {
    const {HAMMER, hammerMs, boxGapSeconds, buildAim, BUILD_SPREAD} = await import("../src/figure/parcels.js");
    let seed = 7;
    const random = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const hammers = Array.from({length: 40}, () => hammerMs(random));
    expect(Math.min(...hammers)).toBeGreaterThanOrEqual(4000);
    expect(Math.max(...hammers)).toBeLessThanOrEqual(10000);
    expect([HAMMER.least, HAMMER.most]).toEqual([4000, 10000]);
    const gaps = Array.from({length: 40}, () => boxGapSeconds(random));
    expect(new Set(gaps.map((gap) => gap.toFixed(2))).size).toBeGreaterThan(20);
    expect(gaps.some((gap) => gap >= 2)).toBe(true);
    let last = null;
    for (let box = 0; box < 30; box++) {
        const aim = buildAim(100, 900, last, random);
        expect(aim).toBeGreaterThanOrEqual(100);
        expect(aim).toBeLessThanOrEqual(900);
        if (last !== null) expect(Math.abs(aim - last)).toBeGreaterThanOrEqual(BUILD_SPREAD);
        last = aim;
    }
});

test("a pile is taken away a minute after its run ended with no commit, never sooner and never while a run builds", async () => {
    const {isPileLeft, LEFT_PILE_SECONDS} = await import("../src/figure/parcels.js");
    const pile = [{state: "piled"}, {state: "piled"}];
    expect(LEFT_PILE_SECONDS).toBe(60);
    expect(isPileLeft(pile, false, 100, 159)).toBe(false);
    expect(isPileLeft(pile, false, 100, 160)).toBe(true);
    expect(isPileLeft(pile, true, null, 500), "a run still building keeps it").toBe(false);
    expect(isPileLeft([...pile, {state: "building"}], false, 100, 500), "a box still in hand keeps it").toBe(false);
    expect(isPileLeft([], false, 100, 500)).toBe(false);
});

test("a build command is timed from its own start, so one that ends within five seconds is never hammered for", async () => {
    const {figureStateOf} = await import("../src/domain/figureState.js");
    const {buildRunAt} = await import("../src/figure/parcels.js");
    const agent = {status: "working", tool_running: true, tool: "Bash", doing: "npm run build", heard_at: new Date(1000 * 1000).toISOString(), part_started_at: 1060};
    const held = figureStateOf(agent, 0, 1063);
    expect(held.since, "the build's own start, not the chain's first hook").toBe(1060);
    expect(buildRunAt([], {card: "", since: held.since}, 1063)).toBe(null);
    expect(buildRunAt([], {card: "", since: held.since}, 1066)).not.toBe(null);
});

test("the claw slows to a stop just over the stack with no overshoot, hovers, grips only then, and lifts after a tug", async () => {
    const {craneAt} = await import("../src/figure/parcels.js");
    const stops = [{x: 300, high: 20, ids: [1]}];
    const floor = 600;
    const top = 0;
    const reach = floor - top - stops[0].high - CLAW_CLEARANCE;
    expect(CLAW_CLEARANCE, "the hub stops clear of the box's top").toBeGreaterThan(8);
    const at = (ms) => craneAt(stops, CRANE.enter + ms, floor, top, 0, 900);
    const lowering = Array.from({length: 23}, (_, step) => at((CRANE.lower * step) / 22).chain);
    expect(Math.max(...lowering)).toBeLessThanOrEqual(reach + 1e-9);
    const lastSteps = lowering.slice(-3);
    expect(lastSteps[2] - lastSteps[1], "slowing as it nears the stop").toBeLessThan(lastSteps[1] - lastSteps[0] + 1e-9);
    const hovering = [at(CRANE.lower + 10), at(CRANE.lower + CRANE.hover - 10)];
    expect(hovering.map((frame) => frame.chain)).toEqual([reach, reach]);
    expect(hovering.map((frame) => frame.open), "the prongs stay open while it hovers").toEqual([1, 1]);
    const gripped = at(CRANE.lower + CRANE.hover + CRANE.grab);
    expect(gripped.open).toBe(0);
    const tugged = at(CRANE.lower + CRANE.hover + CRANE.grab + CRANE.lift * CRANE.tugShare * 0.9);
    expect(tugged.chain).toBeCloseTo(reach - CRANE.tug);
    expect(at(CRANE.lower + CRANE.hover + CRANE.grab + CRANE.lift * 0.8).chain).toBeLessThan(tugged.chain);
});

test("the UFO draws the boxes up one by one, the top box first, each faster as it nears, swaying on its own path", async () => {
    const {boxRisen, boxSway, BEAM_SWAY} = await import("../src/figure/parcels.js");
    const at = (risen) => [0, 1, 2].map((rank) => boxRisen(risen, rank, 3));
    expect(at(0.1)[0]).toBeGreaterThan(0);
    expect(at(0.1)[2], "the lowest box waits its turn").toBe(0);
    for (const risen of [0.2, 0.5, 0.8]) expect(at(risen)[0]).toBeGreaterThanOrEqual(at(risen)[1]);
    const climb = [0.6, 0.7, 0.8, 0.9, 1].map((risen) => boxRisen(risen, 0, 3));
    const steps = climb.slice(1).map((value, index) => value - climb[index]);
    for (let index = 1; index < steps.length; index++) expect(steps[index], "drawn faster as it nears").toBeGreaterThan(steps[index - 1]);
    expect(at(1)).toEqual([1, 1, 1]);
    expect(boxSway(0.3, 1)).not.toBe(boxSway(0.3, 2));
    expect(Math.abs(boxSway(0.3, 1))).toBeLessThanOrEqual(BEAM_SWAY);
    expect(boxSway(1, 1)).toBe(0);
});
