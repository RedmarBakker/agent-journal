import {readFileSync} from "node:fs";
import {dirname} from "node:path";
import {fileURLToPath} from "node:url";
import * as THREE from "three";
import {createApp, h} from "vue";
import {describe, expect, it} from "vitest";
import {CLIPS, Posing, THINKING} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";
import {GROUNDED, HELD, clipFor, clipOf} from "../src/domain/figureState.js";
import {reactionTo, workMoments} from "../src/figure/reactions.js";
import FigureAct from "../src/chat/FigureAct.vue";

const {rig, stances} = JSON.parse(readFileSync(`${dirname(fileURLToPath(import.meta.url))}/figureRig.json`));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const named = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));

// the thinking clip posed at `t` of its loop for the butler, whose free hand is the right
function thinking(t) {
    const pose = new Posing(RIG, "stand", 0);
    named.think.pose(pose, stanceOf("butler"), t);
    const moves = pose.moves(0);
    const tip = new THREE.Vector3(0, 0, 0.3).add(RIG.heads.get("hand_r")).applyMatrix4(moves.get("hand_r"));
    return {pose, hand: pose.head("hand_r", moves.get("hand_r")), tip, rest: pose.head("hand_l", moves.get("hand_l"))};
}

// FigureAct drawing the bulb act at `u`, the eyes at the middle of a 100 pixel picture a third of the way down
function bulbAt(u) {
    const root = document.createElement("div");
    createApp({render: () => h(FigureAct, {name: "bulb", u, hand: {x: 0.7, y: 0.6, out: 1, other: {x: 0.3, y: 0.6}}, head: {x: 0.5, y: 0.3}, feet: 0.9, size: 100, room: {left: 0, right: 0}})}).mount(root);
    return root.querySelector("[data-bulb]");
}

describe("the figure thinking", () => {
    it("plays the thinking clip while the agent thinks", () => {
        expect(HELD.thinking).toBe("think");
        const scene = {mode: GROUNDED, place: {posture: "stand", face: 0}, state: "thinking", doing: clipOf("thinking"), doingFacing: 0};
        expect(clipFor(scene, () => true).clip).toBe("think");
    });

    it("holds its hand at its chin, its eyes turned up, the fingers tapping slowly", () => {
        const {pose, hand, rest} = thinking(0);
        expect(hand.z, "the hand up at the chin").toBeGreaterThan(RIG.heads.get("chest").z);
        expect(hand.y, "before the face").toBeLessThan(-0.5);
        expect(rest.z, "the other hand at rest").toBeLessThan(RIG.heads.get("chest").z);
        expect(pose.eyesUp).toBe(THINKING.eyesUp);
        expect(pose.eyesUp).toBeGreaterThan(0);
        const tips = Array.from({length: named.think.frames}, (_, frame) => thinking(frame / named.think.frames).tip.x);
        expect(Math.max(...tips) - Math.min(...tips), "the fingertips move").toBeGreaterThan(0.05);
        const seconds = named.think.frames / named.think.fps;
        expect(seconds / THINKING.taps, "a tap every second and more").toBeGreaterThanOrEqual(1.5);
    });
});

describe("the bulb at the end of thinking", () => {
    it("is a moment when the thinking ends, and only then", () => {
        expect(workMoments("writing", false, 1, 10, "thinking").moments.map((moment) => moment.beat)).toContain("thought");
        expect(workMoments("thinking", false, 1, 10, "thinking").moments.map((moment) => moment.beat)).not.toContain("thought");
        expect(workMoments("writing", false, 1, 10, "reading").moments.map((moment) => moment.beat)).not.toContain("thought");
    });

    it("lights now and then, not every time, and never again within its cooldown", () => {
        const rolls = Array.from({length: 100}, (_, index) => (index + 0.5) / 100);
        const lit = rolls.filter((roll) => reactionTo("thought", new Map(), 1000, () => roll)?.clip === "bulb").length;
        expect(lit, "about one end in five").toBeGreaterThan(10);
        expect(lit).toBeLessThan(35);
        const memory = new Map();
        expect(reactionTo("thought", memory, 1000, () => 0).clip).toBe("bulb");
        expect(reactionTo("thought", memory, 1060, () => 0), "a minute later").toBe(null);
        expect(reactionTo("thought", memory, 1121, () => 0).clip, "past two minutes").toBe("bulb");
    });

    it("draws the bulb over the head, lit a moment, then faded", () => {
        const act = ACTS.bulb;
        const glowing = bulbAt((act.lights[1] + act.fades[0]) / 2);
        expect(glowing).not.toBe(null);
        const [, y] = glowing.getAttribute("transform").match(/translate\(([-\d.]+) ([-\d.]+)\)/).slice(1).map(Number);
        expect(y, "above the eyes").toBeLessThan(30);
        expect(Number(glowing.getAttribute("opacity"))).toBe(1);
        expect(bulbAt(act.lights[0] / 2), "not yet lit").toBe(null);
        expect(bulbAt(1), "faded out").toBe(null);
        expect(named.bulb.loops).toBe(false);
    });
});
