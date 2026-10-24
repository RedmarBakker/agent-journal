import {readFileSync} from "node:fs";
import * as THREE from "three";
import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import FigureAct from "../src/chat/FigureAct.vue";

const {CLIPS, GROUND, LEGS, Posing} = await import("../src/figure/figure.js");
const {ACTS, heldPhases, offSwing} = await import("../src/figure/acts.js");
const {POSTURES} = await import("../src/figure/places.js");
const {FRAMED} = await import("../src/figure/frame.js");

const {rig, stances} = JSON.parse(readFileSync("tests/figureRig.json"));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "rope_swing");
const act = ACTS.rope_swing;

// The figure's body as every voice's model has it (public/voices/figures, the meshes' bounds): its legs 0.28 thick about their bones and
// 0.75 out from the middle, its coat 0.6, and its sleeves 0.27 thick about the arm at the wrist, in the figure's units
const BODY = {leg: 0.28, legs: 0.75, coat: 0.6, sleeve: 0.27};
// the figure's picture's two sizes: the chat's, and twice it
const SIZES = [112, 224];

// the swing drawn at `u` of the act over a picture `size` pixels square
async function drawn(u, size) {
    const host = document.createElement("div");
    createApp({render: () => h(FigureAct, {name: "rope_swing", u, hand: {x: 0.3, y: 0.3, out: 1}, head: {x: 0.5, y: 0.3}, feet: 1 - GROUND, size, room: {left: 0, right: 0}})}).mount(host);
    await nextTick();
    return host;
}

// the figure seated on the swing `u` of the way through the act for `voice`, posed as the page draws it seated (figure.js Stage.draw)
function seated(u, voice) {
    const pose = new Posing(RIG, "sit", 0);
    LEGS.sit.under(pose);
    clip.pose(pose, stanceOf(voice), u);
    LEGS.sit.over(pose);
    const moves = pose.moves(0);
    return (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone));
}

// a height in the figure's units as a share of its picture from the top
const shareOf = (z) => 0.5 - (z - FRAMED.middle) / FRAMED.height;

test("the swing is drawn whole in the act's first frame, before the figure has sat down on it, and the figure sits down onto it", async () => {
    for (const size of SIZES) {
        const first = await drawn(0, size);
        expect(first.querySelector("[data-swing-seat]"), `${size} seat`).not.toBe(null);
        expect(first.querySelectorAll("[data-swing-rope]").length, `${size} ropes`).toBe(2);
        // and every frame after, to the last
        for (const u of [0.05, 0.5, 0.99]) expect((await drawn(u, size)).querySelector("[data-swing-seat]"), `${size} at ${u}`).not.toBe(null);
    }
    // the figure above the seat as the act begins, sat on it by the end of the intro, and rising off it at the end
    expect(offSwing(0)).toBe(1);
    const held = (act.intro + act.hold / 2) / (act.intro + act.hold + act.outro);
    expect(heldPhases(act, held).held).not.toBe(null);
    expect(offSwing(held)).toBe(0);
    expect(offSwing(0.999)).toBeGreaterThan(0.9);
    for (const voice of Object.keys(stances)) expect(seated(0, voice)("hips").z, voice).toBeGreaterThan(seated(held, voice)("hips").z + 0.2);
});

test("seated on it, the seat's top is at the figure's seat, under its thighs, a little wider than its body, its ropes outside its arms, at both sizes", async () => {
    const frames = act.intro + act.hold + act.outro;
    for (const size of SIZES) {
        const seat = (await drawn(0.5, size)).querySelector("[data-swing-seat]");
        const ropes = [...(await drawn(0.5, size)).querySelectorAll("[data-swing-rope]")].map((rope) => Number(rope.getAttribute("x1")) - size / 2);
        const top = Number(seat.getAttribute("y"));
        const wide = Number(seat.getAttribute("width"));
        for (const voice of Object.keys(stances)) {
            for (let frame = act.intro; frame < act.intro + act.hold; frame += 6) {
                const at = seated(frame / frames, voice);
                const label = `${voice} ${size} frame ${frame}`;
                // the thighs out over the seat, their underside on its top, within a pixel
                const under = Math.min(at("thigh_l").z, at("shin_l").z, at("thigh_r").z, at("shin_r").z) - BODY.leg;
                expect(Math.abs(top - shareOf(under) * size), `${label} seat at the thighs`).toBeLessThan(1);
                // the body across, its arms out to the ropes, its legs and its coat, in the picture's pixels
                const across = Math.max(Math.abs(at("hand_l").x), Math.abs(at("hand_r").x)) + BODY.sleeve;
                const body = (Math.max(across, BODY.legs, BODY.coat) / FRAMED.height) * size;
                expect(wide / 2, `${label} seat wider than the body`).toBeGreaterThan(body);
                expect(wide / 2, `${label} a little wider`).toBeLessThan(body * 1.3);
                for (const x of ropes) expect(Math.abs(x), `${label} rope outside the arms`).toBeGreaterThan(body);
                expect(wide / 2, `${label} the ropes at the seat's ends`).toBeGreaterThanOrEqual(Math.max(...ropes.map(Math.abs)));
            }
        }
        // the ropes from the knots on the bubble above down to the seat
        const rope = (await drawn(0.5, size)).querySelector("[data-swing-rope]");
        expect(Number(rope.getAttribute("y2"))).toBe(top);
        expect(Number(rope.getAttribute("y1"))).toBeCloseTo((1 - GROUND - POSTURES.sit.drop - act.rope) * size, 6);
    }
});
