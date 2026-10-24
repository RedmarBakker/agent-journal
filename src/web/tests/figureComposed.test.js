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
        // its knees up and its feet flat on the floor before it, never its legs straight out toward the viewer
        for (const side of ["l", "r"]) {
            const knee = at(`shin_${side}`);
            const foot = at(`foot_${side}`);
            expect(knee.z, `${voice} ${side} knee up`).toBeGreaterThan(at(`thigh_${side}`).z + 0.15);
            expect(knee.z, `${voice} ${side} knee over the foot`).toBeGreaterThan(foot.z + 0.25);
            expect(foot.y - hips.y, `${voice} ${side} foot near`).toBeGreaterThan(-0.9);
        }
    }
});

test("lounging, its legs straight out, the figure is only ever side-on: every lounge spot faces sideways and nothing turns it toward the viewer", async () => {
    const {ledgeSpot} = await import("../src/figure/perches.js");
    const home = chat();
    for (const along of [1 / 3, 1 / 2, 2 / 3]) {
        const spot = ledgeSpot(along, FIGURE, {on: home});
        expect(spot.posture).toBe("lounge");
        expect([90, 270].includes(spot.face), String(along)).toBe(true);
    }
    // whatever it plays there, a look, a beat facing the viewer or a wait turned to the compose box, it keeps its side-on facing
    const place = {...ledgeSpot(1 / 3, FIGURE, {on: home}), on: home};
    for (const scene of [{doing: "idle"}, {beat: {clip: "nod", facing: 0}}, {state: "waiting", composeFacing: 30}, {watching: "watch"}]) {
        expect(clipFor({mode: GROUNDED, place, state: "idle", doing: "idle", ...scene}, () => true).facing, JSON.stringify(scene)).toBe(place.face);
    }
    // and its picture never turns to the viewer for a look or a lit visor, nor its head to look at anything
    expect(turnsToViewer("lounge")).toBe(false);
    expect(turnsToViewer("composed")).toBe(true);
    expect(turnsToViewer("stand")).toBe(true);
});

test("lounging, both hands lie flat on the floor beside the hips or a little behind them, level and never below the floor line, for every voice and clip", () => {
    const lounging = CLIPS.filter((clip) => clip.postures.includes("lounge"));
    expect(lounging.length).toBeGreaterThan(3);
    const posed = (clip, voice, t) => {
        const pose = new Posing(RIG, "lounge", 0);
        LEGS.lounge.under(pose);
        clip.pose(pose, stanceOf(voice), t);
        LEGS.lounge.over(pose);
        const moves = pose.moves(0);
        return {at: (name) => pose.head(name, moves.get(name)), tip: (name) => RIG.heads.get(name).clone().add(RIG.along.get(name)).applyMatrix4(moves.get(name))};
    };
    const seated = posed(CLIPS.find((clip) => clip.name === "idle"), "butler", 0).at("hips").z;
    for (const voice of Object.keys(stances)) {
        for (const clip of lounging) {
            for (const t of [0, 0.5]) {
                const {at, tip} = posed(clip, voice, t);
                const hips = at("hips");
                // the floor line, carried up with the whole body by a clip that lifts it, as a startle does
                const floor = LOUNGE.floor + hips.z - seated;
                for (const [side, sign] of [["l", 1], ["r", -1]]) {
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
                for (const side of hands) {
                    const label = `${posture} ${voice} ${clip.name} ${side}`;
                    const [wrist, fingers] = [at(`hand_${side}`), tip(`hand_${side}`)];
                    for (const point of [wrist, fingers]) {
                        expect(point.z - surface, label).toBeGreaterThan(-0.05);
                        expect(point.z - surface, label).toBeLessThan(0.18);
                    }
                    expect(Math.abs(fingers.z - wrist.z), `${label} level`).toBeLessThan(0.05);
                }
                // seated in any way, the tails hanging behind are sat on, never through the seat
                for (const tail of BUTLER.satOn) expect(pose.stowed.has(tail), `${posture} ${clip.name} ${tail}`).toBe(true);
            }
        }
    }
});
