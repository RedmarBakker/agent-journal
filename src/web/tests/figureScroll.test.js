import {readFileSync} from "node:fs";
import {dirname} from "node:path";
import {fileURLToPath} from "node:url";
import * as THREE from "three";
import {createApp, h} from "vue";
import {describe, expect, it} from "vitest";
import {holdsHead} from "../src/figure/looks.js";
import {CLIPS, Posing, REPORT_SCROLL, reportScrollOf} from "../src/figure/figure.js";
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

// FigureAct drawing the scroll act at `u`, on a 100 pixel picture
function drawn(u) {
    const root = document.createElement("div");
    createApp({render: () => h(FigureAct, {name: "scroll", u, hand: {x: 0.5, y: 0.4, out: -1, other: {x: 0.5, y: 0.6}}, head: {x: 0.5, y: 0.3}, feet: 0.9, size: 100, room: {left: 0, right: 0}})}).mount(root);
    return root;
}

// the scroll as the pose holds it at `u`, and where each hand grips, in the figure's own axes
function held(u) {
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf("butler"), u);
    const moves = pose.moves(0);
    const grip = (side) => pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`));
    const scroll = pose.props.get("report_scroll");
    const middle = scroll && scroll.at.clone().applyMatrix4(moves.get("root"));
    return {scroll, middle, free: grip("r"), other: grip("l")};
}

// the 3D scroll built and shaped as the pose holds it at `u`, with its parts by name
function modelled(u) {
    const root = new THREE.Group();
    root.name = "report_scroll";
    reportScrollOf(root);
    root.userData.shape(held(u).scroll);
    root.updateMatrixWorld(true);
    const part = (name) => root.getObjectByName(`report_scroll_${name}`) ?? root.getObjectByName(name);
    return {root, part};
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
        expect(holdsHead(clip), "the head stays on the scroll, never turned to the viewer").toBe(true);
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

    it("holds the 3D scroll's top roller at the free hand and its bottom roller at the other, moving with the hands as they open and close it", () => {
        for (const u of [open, act.unrolls[0] + 0.05, act.rolls[0] + 0.05]) {
            const {scroll, middle, free, other} = held(u);
            const top = middle.clone().add(scroll.top);
            const bottom = middle.clone().add(scroll.bottom);
            expect(top.z, `${u} top at the free hand's height`).toBeCloseTo(free.z, 5);
            expect(bottom.z, `${u} bottom at the other's`).toBeCloseTo(other.z, 5);
            expect(Math.abs(top.y - free.y), `${u} in the free hand`).toBeLessThan(0.01);
            expect(Math.abs(top.x - (free.x + other.x) / 2), `${u} centred between the hands`).toBeLessThan(0.01);
            expect(top.distanceTo(free), `${u} the hand on its roller`).toBeLessThan(REPORT_SCROLL.length / 2);
        }
        const coming = held(act.raise[1] / 2);
        expect(coming.scroll.top.z - coming.scroll.bottom.z, "rolled up in the free hand while the hands come up").toBeCloseTo(REPORT_SCROLL.rolled, 5);
        expect(held(0).scroll, "not before it is raised").toBeUndefined();
        expect(held(rolledUp).scroll.open).toBeCloseTo(0, 3);
        expect(held(open).scroll.open).toBe(1);
    });

    it("models two shaded wooden rollers with knobbed ends and a shaded curved parchment, its aged back toward the viewer, rolling round the rollers", () => {
        const {part} = modelled(open);
        for (const which of ["top", "bottom"]) {
            const roller = part(`${which}`);
            for (const name of [`report_scroll_${which}_roller`, `report_scroll_${which}_knob_l`, `report_scroll_${which}_knob_r`, `report_scroll_${which}_wound`]) {
                const mesh = roller.getObjectByName(name);
                expect(mesh, name).toBeDefined();
                expect(mesh.material.type, `${name} shaded as the figure is`).toBe("ShaderMaterial");
                expect(mesh.children.some((child) => child.isMesh), `${name} outlined`).toBe(true);
            }
        }
        const parchment = part("parchment");
        expect(parchment.material.type).toBe("ShaderMaterial");
        expect(new THREE.Color(...parchment.material.uniforms.colour.value.toArray()).getHex(), "aged back").toBe(REPORT_SCROLL.colours.back);
        const position = parchment.geometry.attributes.position;
        const depths = Array.from({length: position.count}, (_, index) => position.getZ(index));
        expect(Math.max(...depths) - Math.min(...depths), "curved, not flat").toBeGreaterThan(REPORT_SCROLL.bow);
        const {columns} = REPORT_SCROLL;
        const edge = position.getZ(Math.floor(REPORT_SCROLL.rows / 2) * (columns + 1));
        const centre = position.getZ(Math.floor(REPORT_SCROLL.rows / 2) * (columns + 1) + columns / 2);
        expect(centre - edge, "its side edges curled back").toBeGreaterThan(REPORT_SCROLL.curl / 2);
        expect(parchment.visible).toBe(true);
        const rolled = modelled(act.raise[1]);
        expect(rolled.part("parchment").visible, "wound up on the rollers while it is rolled").toBe(false);
        const sleeve = (state) => state.part("top").getObjectByName("report_scroll_top_wound").scale.x;
        expect(sleeve(rolled), "the paper wound thick round the roller while rolled").toBeGreaterThan(sleeve(modelled(open)));
        const turned = (state) => state.part("top").getObjectByName("report_scroll_top_roller").rotation.x;
        expect(turned(modelled(open)), "the rollers turn as it unrolls").not.toBeCloseTo(turned(rolled), 2);
        expect(drawn(open).querySelector("svg").children[0].children.length, "never drawn flat on the page").toBe(0);
    });
});
