import {readFileSync} from "node:fs";
import {dirname} from "node:path";
import {fileURLToPath} from "node:url";
import * as THREE from "three";
import {createApp, h} from "vue";
import {describe, expect, it} from "vitest";
import {CLIPS, PONDERING, Posing, THINKING} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";
import {GROUNDED, HELD, clipFor, clipOf} from "../src/domain/figureState.js";
import {reactionTo, workMoments} from "../src/figure/reactions.js";
import FigureAct from "../src/chat/FigureAct.vue";

const {rig, stances} = JSON.parse(readFileSync(`${dirname(fileURLToPath(import.meta.url))}/figureRig.json`));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const named = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));

// the thinking clip posed at `t` of its loop for the butler, whose free hand is the right: where its knuckles grip, where the chin is
// as the head carries it, where the elbow of that arm is and where the other hand grips
function thinking(t) {
    const pose = new Posing(RIG, "stand", 0);
    named.think.pose(pose, stanceOf("butler"), t);
    const moves = pose.moves(0);
    return {
        pose,
        knuckles: pose.grip("r", [0, 0, 0]).applyMatrix4(moves.get("hand_r")),
        chin: new THREE.Vector3(...THINKING.chin).applyMatrix4(moves.get("head")),
        elbow: pose.head("forearm_r", moves.get("forearm_r")),
        folded: pose.grip("l", [0, 0, 0]).applyMatrix4(moves.get("hand_l")),
    };
}

// the thinking act posed at `u` of its way through for the butler: its pose, and where the eyes are as the head carries them
function pondering(u) {
    const pose = new Posing(RIG, "stand", 0);
    named.ponder.pose(pose, stanceOf("butler"), u);
    const moves = pose.moves(0);
    return {pose, at: (name) => pose.head(name, moves.get(name)), head: moves.get("head")};
}

// FigureAct drawing the thinking act at `u`, the eyes at the middle of a 100 pixel picture a third of the way down
function drawnAt(u) {
    const root = document.createElement("div");
    createApp({render: () => h(FigureAct, {name: "ponder", u, hand: {x: 0.3, y: 0.4, out: -1, other: {x: 0.7, y: 0.6}}, head: {x: 0.5, y: 0.3}, feet: 0.9, size: 100, room: {left: 0, right: 0}})}).mount(root);
    return root;
}

describe("the figure thinking", () => {
    it("plays the thinking clip while the agent thinks", () => {
        expect(HELD.thinking).toBe("think");
        const scene = {mode: GROUNDED, place: {posture: "stand", face: 0}, state: "thinking", doing: clipOf("thinking"), doingFacing: 0};
        expect(clipFor(scene, () => true).clip).toBe("think");
    });

    it("rests its knuckles on the bottom of its head where a chin would be, tapping it slowly, the elbow on the other arm folded across it", () => {
        const loop = Array.from({length: named.think.frames}, (_, frame) => thinking(frame / named.think.frames));
        const gaps = loop.map(({knuckles, chin}) => knuckles.distanceTo(chin));
        expect(Math.min(...gaps), "the knuckles touch the chin").toBeLessThan(0.03);
        expect(Math.max(...gaps), "and lift only a little off it to tap").toBeLessThan(THINKING.tap + 0.03);
        expect(Math.max(...gaps) - Math.min(...gaps), "a tap").toBeGreaterThan(THINKING.tap / 2);
        expect(THINKING.chin[2], "the chin is the bottom of the head, above the neck").toBeGreaterThan(RIG.heads.get("head").z);
        expect(named.think.frames / named.think.fps / THINKING.taps, "slowly: a tap every second and a half or more").toBeGreaterThanOrEqual(1.5);
        const {elbow, folded} = loop[0];
        expect(folded.z, "the other hand under the elbow").toBeLessThan(elbow.z);
        expect(folded.distanceTo(elbow), "close under it").toBeLessThan(0.45);
        expect(folded.x, "folded across the body toward the thinking side").toBeLessThan(0);
    });

    it("glances up and aside with its eyes in their usual soft shape, never bare round dots", () => {
        const {pose} = thinking(0);
        expect(pose.eyeShape, "the usual shape").toBe(null);
        const [aside, up] = pose.eyeShift;
        expect(up, "up").toBeGreaterThan(0.2);
        expect(Math.abs(aside), "to one side").toBeGreaterThan(0.2);
        const idle = new Posing(RIG, "stand", 0);
        named.idle.pose(idle, stanceOf("butler"), 0);
        expect(idle.eyeShift, "straight ahead otherwise").toEqual([0, 0]);
    });
});

describe("the thinking act", () => {
    const act = ACTS.ponder;
    const middle = (act.cloud[0] + act.cloud[1]) / 2;

    it("plays while the agent thinks, at most once a minute, and the held thinking shows between plays", () => {
        expect(workMoments("thinking", false, 0, 1).moments.map((moment) => moment.beat)).toContain("pondering");
        expect(workMoments("running", false, 0, 1).moments.map((moment) => moment.beat)).not.toContain("pondering");
        const memory = new Map();
        expect(reactionTo("pondering", memory, 1000, () => 0.99).clip, "every time it is free to").toBe("ponder");
        expect(reactionTo("pondering", memory, 1030, () => 0), "half a minute later").toBe(null);
        expect(reactionTo("pondering", memory, 1059, () => 0), "just under a minute").toBe(null);
        expect(reactionTo("pondering", memory, 1061, () => 0).clip, "a minute on").toBe("ponder");
        expect(named.ponder.loops, "played once, then the held clip again").toBe(false);
        expect(HELD.thinking).toBe("think");
    });

    it("tilts its head up and to one side, its finger along its cheek, swaying a little, its eyes glancing up in their usual shape", () => {
        const {pose, at, head} = pondering(middle);
        const tilted = new THREE.Vector3(0, 0, 1).transformDirection(head);
        expect(Math.abs(tilted.x), "tilted to one side").toBeGreaterThan(0.15);
        const looks = new THREE.Vector3(0, -1, 0).transformDirection(head);
        expect(looks.z, "and up").toBeGreaterThan(0.1);
        const cheek = new THREE.Vector3(-PONDERING.cheek[0], PONDERING.cheek[1], PONDERING.cheek[2]).applyMatrix4(head);
        const grip = pose.grip("r", [0, 0, 0]).applyMatrix4(pose.moves(0).get("hand_r"));
        expect(grip.distanceTo(cheek), "the finger at the cheek").toBeLessThan(0.05);
        expect(at("hand_r").z, "the hand up by the head").toBeGreaterThan(RIG.heads.get("chest").z);
        expect(pose.eyeShape).toBe(null);
        expect(pose.eyeShift[1]).toBeGreaterThan(0.2);
        const sways = Array.from({length: 20}, (_, index) => pondering(act.cloud[0] + 0.05 + (index / 20) * (act.cloud[1] - act.cloud[0] - 0.1)).head.elements[0]);
        expect(Math.max(...sways) - Math.min(...sways), "it sways").toBeGreaterThan(0.01);
    });

    it("draws a thought cloud over the head rising from three puffs, its three dots pulsing one after another", () => {
        const drawn = drawnAt(middle);
        const cloud = drawn.querySelector("[data-thought-cloud]");
        expect(cloud).not.toBe(null);
        const dots = [...drawn.querySelectorAll("[data-thought-dot]")];
        expect(dots.length).toBe(3);
        const seconds = act.frames / act.fps;
        const brightest = Array.from({length: 12}, (_, step) => {
            const u = middle + ((step / 12) * act.pulse) / seconds;
            const lit = [...drawnAt(u).querySelectorAll("[data-thought-dot]")].map((dot) => Number(dot.getAttribute("opacity")));
            return lit.indexOf(Math.max(...lit));
        });
        expect(new Set(brightest), "each dot has its turn").toEqual(new Set([0, 1, 2]));
        const order = brightest.filter((dot, index) => index === 0 || dot !== brightest[index - 1]);
        order.slice(1).forEach((dot, index) => expect(dot, "one after another").toBe((order[index] + 1) % 3));
        expect(drawnAt(act.cloud[0] / 2).querySelector("[data-thought-cloud]"), "none before it begins").toBe(null);
        expect(drawnAt(act.lights[1]).querySelector("[data-thought-dot]"), "gone once the bulb lights").toBe(null);
    });

    it("ends with the bulb every time it plays, the finger raised, 'got it'", () => {
        const lit = drawnAt((act.lights[1] + act.fades[0]) / 2).querySelector("[data-bulb]");
        expect(lit).not.toBe(null);
        expect(Number(lit.getAttribute("opacity"))).toBe(1);
        expect(drawnAt(middle).querySelector("[data-bulb]"), "not while it thinks").toBe(null);
        expect(drawnAt(1).querySelector("[data-bulb]"), "faded at the end").toBe(null);
        const {at} = pondering((act.lights[1] + act.fades[0]) / 2);
        expect(at("hand_r").z, "the hand raised").toBeGreaterThan(RIG.heads.get("upper_arm_r").z + 0.4);
        expect(CLIPS.some((clip) => clip.name === "bulb"), "the bulb is the act's own end, never a clip apart").toBe(false);
    });
});
