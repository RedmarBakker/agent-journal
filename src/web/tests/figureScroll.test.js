import {readFileSync} from "node:fs";
import {dirname} from "node:path";
import {fileURLToPath} from "node:url";
import * as THREE from "three";
import {createApp, h} from "vue";
import {describe, expect, it} from "vitest";
import {CLIPS, Posing} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";
import FigureAct from "../src/chat/FigureAct.vue";

const {rig, stances} = JSON.parse(readFileSync(`${dirname(fileURLToPath(import.meta.url))}/figureRig.json`));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "scroll");
const act = ACTS.scroll;

// the scroll posed at `u` of its way through for the butler, whose free hand is the right: where each hand is, and where the eyes look
function posed(u) {
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf("butler"), u);
    const moves = pose.moves(0);
    const at = (name) => pose.head(name, moves.get(name));
    const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(RIG.eyes.length).applyMatrix4(moves.get("head"));
    const looks = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("head"));
    const turn = THREE.MathUtils.radToDeg(Math.atan2(looks.x, -looks.y));
    return {top: at("hand_r"), bottom: at("hand_l"), eyes, looks, turn};
}

// FigureAct drawing the scroll at `u` with the free hand's grip at `hand` and the other's at `other`, in shares of a 100 pixel picture
function drawn(u, hand, other) {
    const root = document.createElement("div");
    createApp({render: () => h(FigureAct, {name: "scroll", u, hand: {...hand, out: -1, other}, head: {x: 0.5, y: 0.3}, feet: 0.9, size: 100, room: {left: 0, right: 0}})}).mount(root);
    const roller = (which) => Number(root.querySelector(`[data-scroll-roller="${which}"]`).getAttribute("y")) + 1.7;
    return {root, top: roller("top"), bottom: roller("bottom"), parchment: root.querySelector("[data-scroll-parchment]")};
}

describe("the report scroll, read by the figure itself", () => {
    const rolledUp = act.unrolls[0];
    const open = (act.unrolls[1] + act.rolls[0]) / 2;
    const rolledAgain = act.rolls[1] - 0.01;

    it("holds a roller in each hand, the free hand's on top, and pulls them apart to open it and together to roll it closed", () => {
        const gap = (u) => posed(u).top.z - posed(u).bottom.z;
        expect(gap(rolledUp)).toBeLessThan(0.15);
        expect(gap(open)).toBeGreaterThan(0.6);
        expect(gap(rolledAgain)).toBeLessThan(0.15);
        const opening = [0, 0.25, 0.5, 0.75, 1].map((k) => gap(act.unrolls[0] + k * (act.unrolls[1] - act.unrolls[0])));
        opening.slice(1).forEach((each, index) => expect(each).toBeGreaterThan(opening[index]));
        const closing = [0, 0.25, 0.5, 0.75, 1].map((k) => gap(act.rolls[0] + k * (act.rolls[1] - act.rolls[0])));
        closing.slice(1).forEach((each, index) => expect(each).toBeLessThan(closing[index]));
    });

    it("holds the open parchment at its chest, between it and the viewer, the eyes over its top edge looking down into it", () => {
        const {top, bottom, eyes, looks} = posed(open);
        for (const hand of [top, bottom]) {
            expect(hand.y, "in front of the body, toward the viewer").toBeLessThan(-0.5);
            expect(Math.abs(hand.x), "before the middle of the body").toBeLessThan(0.45);
        }
        expect(top.z, "the top edge at the chin, below the face").toBeLessThan(RIG.heads.get("head").z);
        expect(Math.abs((top.z + bottom.z) / 2 - RIG.heads.get("chest").z), "the parchment's middle at the chest").toBeLessThan(0.15);
        expect(eyes.z - top.z, "the eyes over the top edge").toBeGreaterThan(0.3);
        expect(looks.z, "looking down into it").toBeLessThan(-0.2);
        expect(clip.ownLook, "the head stays on the scroll, never turned to the viewer").toBe(true);
    });

    it("turns its head slowly from its left to its right along the lines a few times while it reads, and down from line to line", () => {
        const [from, to] = [Math.ceil(act.unrolls[1] * clip.frames), Math.floor(act.rolls[0] * clip.frames)];
        const reading = Array.from({length: to - from + 1}, (_, index) => posed((from + index) / clip.frames));
        const turns = reading.map((each) => each.turn);
        expect(Math.max(...turns) - Math.min(...turns), "the head's turn changes across the lines").toBeGreaterThan(20);
        const steps = turns.slice(1).map((turn, index) => turn - turns[index]);
        expect(Math.max(...steps.map(Math.abs)), "slowly: a few degrees a frame at most").toBeLessThan(5);
        const sweeps = steps.filter((step, index) => index && Math.sign(step) !== Math.sign(steps[index - 1]) && Math.abs(step) > 0.01).length;
        expect(sweeps, "along the lines a few times").toBeGreaterThanOrEqual(act.lines * 2 - 1);
        expect(turns[0], "each line read from its own left").toBeGreaterThan(5);
        expect(turns[Math.floor(turns.length / act.lines / 2)], "toward its right").toBeLessThan(turns[0]);
        expect(reading.at(-1).eyes.z).toBeLessThan(reading[0].eyes.z);
    });

    it("draws the top roller in the free hand and the bottom one in the other, the parchment's plain aged back between them to the viewer", () => {
        const opened = drawn(open, {x: 0.5, y: 0.4}, {x: 0.5, y: 0.6});
        expect([opened.top, opened.bottom]).toEqual([40, 60]);
        expect(opened.root.querySelectorAll("path").length, "the parchment alone, no lines on the face toward the viewer").toBe(1);
        expect(opened.root.querySelectorAll("text").length).toBe(0);
        expect(opened.parchment.getAttribute("fill"), "aged darker than fresh paper").toBe("#dcc79c");
        const coming = drawn(act.raise[1] / 2, {x: 0.3, y: 0.7}, {x: 0.7, y: 0.7});
        expect(coming.bottom - coming.top, "rolled in the free hand while the hands come up").toBeCloseTo(3.4);
    });
});
