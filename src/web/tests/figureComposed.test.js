// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {CLIPS, COMPOSED, LEGS, LOUNGE, Posing, turnsToViewer} = await import("../src/figure/figure.js");
const {SEATED, turnStep} = await import("../src/figure/places.js");
const {choicesFor} = await import("../src/figure/pile.js");
const {COMPOSED_ALONG, composedSpot} = await import("../src/figure/perches.js");
const {GROUNDED, clipFor} = await import("../src/domain/figureState.js");
const {write} = await import("./figurePage.js");

const FIGURE = {size: 112, below: 0.05};
const CONTACT_HANDS = new Set(["phone_call", "yawn", "sleep", "whistle", "sip", "enter", "salute", "wipe_brow"]);
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// a chat with its compose box, the floor the figure stands on
function chat() {
    const thread = {...boxed({left: 200, top: 100, right: 900, bottom: 800}), querySelector: () => null};
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
    return home;
}

test("now and then, with nothing to do, the figure sits composed near the middle of the floor it stands on, facing the viewer", () => {
    // one of the idle stays, for the figure with nothing to do
    expect(choicesFor({moment: "roam", free: true}).some((entry) => entry.name === "composed")).toBe(true);
    expect(choicesFor({moment: "roam", free: false}).some((entry) => entry.name === "composed")).toBe(false);
    // on the compose box: at its middle, on its top, facing the viewer
    const home = chat();
    const spot = composedSpot(FIGURE, {x: 360, y: 600, on: home});
    expect(spot).toMatchObject({x: 500, y: 600, face: 0, posture: "composed", on: home});
    expect(clipFor({mode: GROUNDED, place: spot, state: "idle", doing: "idle"}, () => true).facing).toBe(0);
    // where it would hide words at the middle, a little to one side, never far from it
    write([{left: 492, right: 508, top: 520, bottom: 590}]);
    const aside = composedSpot(FIGURE, {x: 360, y: 600, on: home});
    expect([300 + 400 * COMPOSED_ALONG[1], 300 + 400 * COMPOSED_ALONG[2]].includes(aside.x)).toBe(true);
    // on no floor it stands on, no composed sit
    expect(composedSpot(FIGURE, {x: 360, y: 600, on: {}})).toBe(null);
});

test("sitting composed, both hands lie flat on the floor at its sides, beside the hips and not behind them, for every voice", () => {
    const idle = CLIPS.find((clip) => clip.name === "idle");
    expect(idle.postures.includes("composed")).toBe(true);
    for (const voice of Object.keys(stances)) {
        const pose = new Posing(RIG, "composed", 0);
        LEGS.composed.under(pose);
        idle.pose(pose, stanceOf(voice), 0);
        LEGS.composed.over(pose);
        const moves = pose.moves(0);
        const at = (name) => pose.head(name, moves.get(name));
        const hips = at("hips");
        for (const [side, sign] of [["l", 1], ["r", -1]]) {
            const hand = at(`hand_${side}`);
            expect(Math.abs(hand.z - COMPOSED.floor), `${voice} ${side} on the floor line`).toBeLessThan(0.2);
            expect(sign * (hand.x - hips.x), `${voice} ${side} at its side`).toBeGreaterThan(0.45);
            expect(Math.abs(hand.y - hips.y), `${voice} ${side} not behind`).toBeLessThan(0.3);
        }
        // upright, not leaning back as it does lounging
        const back = at("neck").sub(hips).normalize();
        expect(back.z, voice).toBeGreaterThan(Math.cos(THREE.MathUtils.degToRad(15)));
        // its knees up and its feet flat on the floor before it, their soles on the floor line, never sunk into it nor its legs straight
        // out toward the viewer
        for (const side of ["l", "r"]) {
            const knee = at(`shin_${side}`);
            const foot = at(`foot_${side}`);
            expect(knee.z, `${voice} ${side} knee up`).toBeGreaterThan(at(`thigh_${side}`).z + 0.15);
            expect(knee.z, `${voice} ${side} knee well over the floor`).toBeGreaterThan(COMPOSED.floor + 0.45);
            expect(knee.z, `${voice} ${side} knee over the foot`).toBeGreaterThan(foot.z + 0.15);
            expect(foot.y - hips.y, `${voice} ${side} foot near`).toBeGreaterThan(-0.9);
            // the ankle as high over the floor line as it stands over the ground, so the sole rests on the floor
            expect(foot.z - COMPOSED.floor, `${voice} ${side} sole on the floor`).toBeCloseTo(RIG.heads.get(`foot_${side}`).z, 2);
        }
    }
});

// the figure sitting composed for `voice` playing `name` at `t`, turned `facing` degrees and leaning on the arm `leans` names (figure.js SIDES,
// 0 for none), posed as the page draws it (figure.js Stage.draw), in its own axes
function composed(voice, name, t, facing, leans) {
    const pose = new Posing(RIG, "composed", 0);
    Object.assign(pose, {facing, leanWay: leans});
    LEGS.composed.under(pose);
    CLIPS.find((clip) => clip.name === name).pose(pose, stanceOf(voice), t);
    LEGS.composed.over(pose);
    const moves = pose.moves(0);
    return {at: (bone) => pose.head(bone, moves.get(bone)), tip: (bone) => RIG.heads.get(bone).clone().add(RIG.along.get(bone)).applyMatrix4(moves.get(bone))};
}

// whether the hand on `side` lies flat on the floor line, wrist and fingers on it and level
const flatOnFloor = ({at, tip}, side) => [at(`hand_${side}`), tip(`hand_${side}`)].every((point) => Math.abs(point.z - COMPOSED.floor) < 0.12) && Math.abs(tip(`hand_${side}`).z - at(`hand_${side}`).z) < 0.05;

test("sitting composed it now and then sits turned a little to the left or right, the hand on the side turned away flat on the floor and the other arm free to move", async () => {
    const {draw} = await import("../src/figure/pile.js");
    // the ways it sits, drawn once a stay: facing the viewer most often, turned either way, and leaning on either arm
    const ways = choicesFor({moment: "composed_as"});
    expect(ways.map((way) => way.name)).toEqual(["facing", "turned_left", "turned_right", "leaning_on_left_arm", "leaning_on_right_arm"]);
    expect(ways[0].weight).toBeGreaterThan(Math.max(...ways.slice(1).map((way) => way.weight)));
    expect(draw({moment: "composed_as"}, () => 0)).toMatchObject({turn: 0, leans: 0});
    // the spot it sits on carries the way, turned and leaning as drawn
    const home = chat();
    expect(composedSpot(FIGURE, {x: 360, y: 600, on: home}, {turn: 25, leans: 0})).toMatchObject({face: 25, leans: 0, posture: "composed"});
    for (const voice of Object.keys(stances)) {
        const free = stanceOf(voice).busy.has("r") ? "l" : "r";
        const SIDE = {l: 1, r: -1};
        // turned so its waving hand is the one toward the viewer: that arm free, still up waving, and the other hand flat on the floor
        const turn = -SIDE[free] * 25;
        const planted = free === "l" ? "r" : "l";
        const turned = composed(voice, "wave", 0.5, (turn + 360) % 360, 0);
        expect(flatOnFloor(turned, planted), `${voice} turned ${turn}: the hand turned away flat`).toBe(true);
        expect(turned.at(`hand_${free}`).z, `${voice} turned ${turn}: the other arm free, waving`).toBeGreaterThan(COMPOSED.floor + 0.8);
        // facing the viewer the same wave is set down, both hands flat
        const facing = composed(voice, "wave", 0.5, 0, 0);
        for (const side of ["l", "r"]) expect(flatOnFloor(facing, side), `${voice} facing: ${side} flat`).toBe(true);
        // turned and at rest, the free hand lies over its knee, never hanging down through the floor
        const resting = composed(voice, "idle", 0, (turn + 360) % 360, 0);
        expect(flatOnFloor(resting, planted), `${voice} turned at rest: the hand turned away flat`).toBe(true);
        const knee = resting.at(`shin_${free}`).add(new THREE.Vector3(...COMPOSED.lean.knee));
        expect(resting.at(`hand_${free}`).distanceTo(knee), `${voice} turned at rest: the free hand over its knee`).toBeLessThan(0.15);
        for (const point of [resting.at(`hand_${free}`), resting.tip(`hand_${free}`)]) expect(point.z, `${voice} turned at rest`).toBeGreaterThan(COMPOSED.floor);
    }
});

test("sitting composed it sometimes leans over on one arm, that hand flat on the floor further out and the other resting over its knee", () => {
    for (const voice of Object.keys(stances)) {
        for (const [leans, side, other] of [[1, "l", "r"], [-1, "r", "l"]]) {
            const label = `${voice} leaning on ${side}`;
            const seat = composed(voice, "idle", 0, 0, leans);
            const upright = composed(voice, "idle", 0, 0, 0);
            // the body bent over toward the arm it leans on
            expect(leans * (seat.at("neck").x - upright.at("neck").x), label).toBeGreaterThan(0.1);
            // that hand flat on the floor, further out than when it sits upright
            expect(flatOnFloor(seat, side), label).toBe(true);
            expect(leans * seat.at(`hand_${side}`).x, label).toBeGreaterThan(leans * upright.at(`hand_${side}`).x + 0.1);
            // the other over the front of its knee
            const knee = seat.at(`shin_${other}`).add(new THREE.Vector3(...COMPOSED.lean.knee));
            expect(seat.at(`hand_${other}`).distanceTo(knee), label).toBeLessThan(0.15);
        }
    }
});

test("on the composer the figure sits on the edge with its legs over it, never lounging on the floor with its legs straight out; a lounge is only ever side-on", async () => {
    const {ledgeSpot} = await import("../src/figure/perches.js");
    const home = chat();
    for (const along of [1 / 3, 1 / 2, 2 / 3]) expect(ledgeSpot(along, FIGURE, {on: home}).posture, String(along)).toBe("sit");
    // a lounging picture never turns to the viewer for a look or a lit visor, nor its head to look at anything
    expect(turnsToViewer("lounge")).toBe(false);
    expect(turnsToViewer("composed")).toBe(true);
    expect(turnsToViewer("stand")).toBe(true);
});

test("lounging, each support hand lies flat beside the hips while at most one hand performs its contact gesture", () => {
    const lounging = CLIPS.filter((clip) => clip.postures.includes("lounge"));
    expect(lounging.length).toBeGreaterThan(3);
    const posed = (clip, voice, t) => {
        const pose = new Posing(RIG, "lounge", 0);
        LEGS.lounge.under(pose);
        clip.pose(pose, stanceOf(voice), t);
        LEGS.lounge.over(pose);
        const moves = pose.moves(0);
        return {inUse: pose.inUse, at: (name) => pose.head(name, moves.get(name)), tip: (name) => RIG.heads.get(name).clone().add(RIG.along.get(name)).applyMatrix4(moves.get(name))};
    };
    const seated = posed(CLIPS.find((clip) => clip.name === "idle"), "butler", 0).at("hips").z;
    for (const voice of Object.keys(stances)) {
        for (const clip of lounging) {
            for (const t of [0, 0.5]) {
                const {at, tip, inUse} = posed(clip, voice, t);
                const hips = at("hips");
                // the floor line, carried up with the whole body by a clip that lifts it, as a startle does
                const floor = LOUNGE.floor + hips.z - seated;
                expect(inUse.size, `${voice} ${clip.name} keeps a support hand`).toBeLessThanOrEqual(CONTACT_HANDS.has(clip.name) ? 1 : 0);
                for (const [side, sign] of [["l", 1], ["r", -1]].filter(([side]) => !inUse.has(side))) {
                    const label = `${voice} ${clip.name} ${t} ${side}`;
                    const [wrist, fingers] = [at(`hand_${side}`), tip(`hand_${side}`)];
                    // the wrist and the fingers both at the floor line, the hand level on it, never through it
                    for (const point of [wrist, fingers]) expect(point.z - floor, label).toBeGreaterThan(-0.05);
                    for (const point of [wrist, fingers]) expect(point.z - floor, label).toBeLessThan(0.15);
                    expect(Math.abs(fingers.z - wrist.z), `${label} level`).toBeLessThan(0.05);
                    // beside the hips or a little behind them, on its own side
                    expect(sign * (wrist.x - hips.x), label).toBeGreaterThan(0.45);
                    expect(wrist.y - hips.y, label).toBeGreaterThan(-0.1);
                    expect(wrist.y - hips.y, label).toBeLessThan(0.7);
                }
            }
        }
    }
});

test("a seated figure never turns where it sits: every change of facing from a seat or to one stands it up first, turns it standing, then sits it", () => {
    const postures = ["stand", "walk", "sit", "lounge", "composed"];
    const facings = [0, 90, 270];
    for (const from of postures.flatMap((posture) => facings.map((facing) => ({posture, facing})))) {
        for (const to of postures.flatMap((posture) => facings.map((facing) => ({posture, facing})))) {
            const label = `${from.posture}@${from.facing} to ${to.posture}@${to.facing}`;
            const steps = [from];
            while (steps.length < 6 && (steps.at(-1).posture !== to.posture || steps.at(-1).facing !== to.facing)) steps.push(turnStep(steps.at(-1), to));
            expect(steps.at(-1), label).toEqual(to);
            // no step turns the figure while it sits, before or after
            for (const [index, pose] of steps.entries()) {
                if (!index || pose.facing === steps[index - 1].facing) continue;
                expect(SEATED.has(pose.posture) || SEATED.has(steps[index - 1].posture), label).toBe(false);
            }
            // from a seat with a turn to make, it first stands up facing as it sat
            if (SEATED.has(from.posture) && from.facing !== to.facing) expect(steps[1], label).toEqual({posture: "stand", facing: from.facing});
        }
    }
});

test("wherever it sits and leans on a hand, on an edge, lounging or sitting composed, the hand lies flat and level at the seat's surface, and the butler sits on his tails", async () => {
    const {BUTLER} = await import("../src/figure/butler.js");
    // the hands each seated posture leans on, as each clip drawn in it has them: on an edge the free hands at idle's lean back, lounging
    // and composed both hands in every clip
    const leaning = {sit: [CLIPS.find((clip) => clip.name === "ledge_sit")], lounge: CLIPS.filter((clip) => clip.postures.includes("lounge")), composed: CLIPS.filter((clip) => clip.postures.includes("composed"))};
    for (const [posture, clips] of Object.entries(leaning)) {
        for (const voice of Object.keys(stances)) {
            const stance = stanceOf(voice);
            const hands = posture === "sit" ? [...stance.free] : ["l", "r"];
            for (const clip of clips) {
                const pose = new Posing(RIG, posture, 0);
                LEGS[posture].under(pose);
                clip.pose(pose, stance, 0.25);
                LEGS[posture].over(pose);
                const moves = pose.moves(0);
                const at = (name) => pose.head(name, moves.get(name));
                const tip = (name) => RIG.heads.get(name).clone().add(RIG.along.get(name)).applyMatrix4(moves.get(name));
                // the surface, carried up with the whole body by a clip that lifts it, as a startle does
                const surface = LOUNGE.floor + at("hips").z - 1.55;
                // a hand the act holds in use, as the one taking a call made seated, is the act's; every other lies flat
                for (const side of hands.filter((each) => !pose.inUse.has(each))) {
                    const label = `${posture} ${voice} ${clip.name} ${side}`;
                    const [wrist, fingers] = [at(`hand_${side}`), tip(`hand_${side}`)];
                    for (const point of [wrist, fingers]) {
                        expect(point.z - surface, label).toBeGreaterThan(-0.05);
                        expect(point.z - surface, label).toBeLessThan(0.18);
                    }
                    expect(Math.abs(fingers.z - wrist.z), `${label} level`).toBeLessThan(0.05);
                }
                expect(pose.inUse.size, `${posture} ${voice} ${clip.name}: at most one hand in use, the other left flat`).toBeLessThanOrEqual(CONTACT_HANDS.has(clip.name) ? 1 : 0);
                // seated in any way, the tails hanging behind are sat on, never through the seat
                for (const tail of BUTLER.satOn) expect(pose.stowed.has(tail), `${posture} ${clip.name} ${tail}`).toBe(true);
            }
        }
    }
});
