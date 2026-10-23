import {readFileSync} from "node:fs";
import {dirname} from "node:path";
import {fileURLToPath} from "node:url";
import * as THREE from "three";
import {createApp, h} from "vue";
import {describe, expect, it} from "vitest";
import {CLIPS, Posing, TORCH, torchOf} from "../src/figure/figure.js";
import {ACTS, torchAim} from "../src/figure/acts.js";
import {FRAMED} from "../src/figure/frame.js";
import FigureAct from "../src/chat/FigureAct.vue";

const {rig, stances} = JSON.parse(readFileSync(`${dirname(fileURLToPath(import.meta.url))}/figureRig.json`));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "flashlight");

// the search posed at `u` for `voice`: the torch as the hand holds it, and the way the hand points and the way to where the beam lands
function searching(u, voice = "butler") {
    const stance = stanceOf(voice);
    const side = stance.busy.has("r") ? "l" : "r";
    const sign = side === "l" ? 1 : -1;
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stance, u);
    const moves = pose.moves(0);
    const wrist = pose.head(`hand_${side}`, moves.get(`hand_${side}`));
    const points = RIG.along.get(`hand_${side}`).clone().transformDirection(moves.get(`hand_${side}`));
    const [across, forward, up] = torchAim(u);
    return {torch: pose.props.get("flashlight"), side, points, toward: new THREE.Vector3(sign * across, forward, up).sub(wrist).normalize()};
}

// FigureAct drawing the search at `u`, the free hand on the viewer's right at `hand` of a 100 pixel picture
function drawn(u, hand = {x: 0.7, y: 0.55}) {
    const root = document.createElement("div");
    createApp({render: () => h(FigureAct, {name: "flashlight", u, hand: {...hand, out: 1, other: {x: 0.3, y: 0.6}}, head: {x: 0.5, y: 0.3}, feet: 0.9, size: 100, room: {left: 0, right: 0}})}).mount(root);
    return root;
}

describe("searching with the torch", () => {
    it("holds the 3D torch in its free hand while the act plays, pointed where its beam lands as it sweeps", () => {
        for (const voice of Object.keys(stances)) {
            for (let step = 0; step < 8; step++) {
                const {torch, side, points, toward} = searching(step / 8, voice);
                expect(torch, `${voice} ${step}`).toMatchObject({bone: `hand_${side}`, frame: `hand_${side}`});
                expect(THREE.MathUtils.radToDeg(points.angleTo(toward)), `${voice} ${step}: pointed at the light`).toBeLessThan(5);
            }
        }
    });

    it("models a metal barrel, a lens rim, a switch and a lens that glows, shaded and outlined as the figure is", () => {
        const root = new THREE.Group();
        root.name = "flashlight";
        torchOf(root);
        for (const part of ["barrel", "cap", "head", "rim", "switch"]) {
            const mesh = root.getObjectByName(`flashlight_${part}`);
            expect(mesh, part).toBeDefined();
            expect(mesh.material.type, `${part} shaded`).toBe("ShaderMaterial");
            expect(mesh.children.some((child) => child.isMesh), `${part} outlined`).toBe(true);
        }
        const lens = root.getObjectByName("flashlight_lens");
        expect(lens.material.color.getHex(), "glowing warm").toBe(TORCH.colours.lens);
        expect(lens.position.x, "at the lens's place from the grip").toBeCloseTo(ACTS.flashlight.lens, 2);
    });

    it("throws its light where the beam lands, a beam from the lens and a pool of light that sweeps across what it falls on", () => {
        const pools = [];
        for (let step = 0; step < 8; step++) {
            const u = step / 8;
            const root = drawn(u);
            const beam = root.querySelector("[data-torch-beam]");
            const pool = root.querySelector("[data-torch-light]");
            expect(beam, `${u}`).not.toBe(null);
            expect(pool, `${u}`).not.toBe(null);
            const [across, , up] = torchAim(u);
            expect(Number(pool.getAttribute("cx")), `${u}: where it lands`).toBeCloseTo(50 + (100 * across) / FRAMED.height, 5);
            expect(Number(pool.getAttribute("cy")), `${u}`).toBeCloseTo(100 * (0.5 - (up - FRAMED.middle) / FRAMED.height), 5);
            pools.push(Number(pool.getAttribute("cx")));
        }
        expect(Math.max(...pools) - Math.min(...pools), "it sweeps").toBeGreaterThan(10);
        expect(drawn(0).querySelectorAll("rect").length, "no flat torch drawn on the page").toBe(0);
    });
});
