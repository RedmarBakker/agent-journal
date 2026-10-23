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
    return {top: at("hand_r"), bottom: at("hand_l"), eyes};
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

    it("holds the open parchment before its face, between it and the viewer, the top roller up at the face", () => {
        const {top, bottom, eyes} = posed(open);
        for (const hand of [top, bottom]) {
            expect(hand.y, "in front of the body, toward the viewer").toBeLessThan(-0.5);
            expect(Math.abs(hand.x), "before the middle of the body").toBeLessThan(0.45);
        }
        expect(top.z).toBeGreaterThan(RIG.heads.get("head").z);
        expect(top.z).toBeLessThan(eyes.z);
        expect(clip.ownLook, "the head stays on the scroll, never turned to the viewer").toBe(true);
    });

    it("moves its head along the lines while it reads, and down from line to line", () => {
        const reading = Array.from({length: 24}, (_, index) => posed(act.unrolls[1] + ((index + 0.5) / 24) * (act.rolls[0] - act.unrolls[1])).eyes);
        const across = reading.map((eyes) => eyes.x);
        expect(Math.max(...across) - Math.min(...across)).toBeGreaterThan(0.1);
        expect(reading.at(-1).z).toBeLessThan(reading[0].z);
    });

    it("draws the top roller in the free hand and the bottom one in the other hand, the parchment's back between them to the viewer", () => {
        const opened = drawn(open, {x: 0.5, y: 0.4}, {x: 0.5, y: 0.6});
        expect([opened.top, opened.bottom]).toEqual([40, 60]);
        expect(opened.parchment).not.toBe(null);
        const lines = [...opened.root.querySelectorAll("path:not([data-scroll-parchment])")];
        expect(lines.length).toBeGreaterThan(0);
        expect(lines.every((line) => line.getAttribute("opacity") === "0.15"), "only the writing showing through from the other side").toBe(true);
        const coming = drawn(act.raise[1] / 2, {x: 0.3, y: 0.7}, {x: 0.7, y: 0.7});
        expect(coming.bottom - coming.top, "rolled in the free hand while the hands come up").toBeCloseTo(3.4);
    });
});
