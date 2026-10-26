import {readFileSync} from "node:fs";
import * as THREE from "three";
import {createApp, h} from "vue";
import {expect, test} from "vitest";
import FigureAct from "../src/chat/FigureAct.vue";
import {CLIPS, GROUND, Stage, drawnPose} from "../src/figure/figure.js";
import {FRAMED} from "../src/figure/frame.js";

const {rig, stances} = JSON.parse(readFileSync("tests/figureRig.json"));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("both closed palms stay on the rendered pogo handlebar throughout the bounces and spring", () => {
    // Use Stage's actual projection and grip calculation without allocating a WebGL renderer in jsdom.
    const stage = Object.create(Stage.prototype);
    const half = FRAMED.height / 2;
    stage.camera = new THREE.OrthographicCamera(-half, half, half, -half, 5, 11);
    stage.camera.position.set(0, FRAMED.middle, 8);
    stage.camera.lookAt(0, FRAMED.middle, 0);
    stage.camera.updateMatrixWorld(true);
    const clip = CLIPS.find((entry) => entry.name === "pogo");
    for (const size of [112, 224]) for (const u of [0.18, 0.26, 0.4, 0.62, 0.8]) {
        const host = document.createElement("div");
        document.body.append(host);
        const app = createApp({render: () => h(FigureAct, {name: "pogo", u, hand: {x: 0.5, y: 0.5, out: 1, other: {x: 0.5, y: 0.5}}, head: {x: 0.5, y: 0.25}, feet: 1 - GROUND, size, room: {left: 200, right: 200}})});
        app.mount(host);
        try {
            const stick = host.querySelector("[data-pogo-stick]");
            const [, x, y] = stick.getAttribute("transform").match(/translate\(([-\d.]+) ([-\d.]+)\)/).map(Number);
            const bar = stick.querySelectorAll("line")[1];
            const top = y + Number(bar.getAttribute("y1"));
            const left = x + Number(bar.getAttribute("x1"));
            const right = x + Number(bar.getAttribute("x2"));
            for (const voice of Object.keys(stances)) {
                const {pose, turned} = drawnPose(RIG, stanceOf(voice), clip, u * clip.frames, 0);
                const moves = pose.moves(turned);
                for (const side of ["l", "r"]) {
                    const palm = stage.gripAt({rig: RIG}, moves, side);
                    const label = `${voice} ${side} at ${u}, ${size}px`;
                    expect(Math.abs(palm.y * size - top), `${label} palm on the SVG bar`).toBeLessThan(0.5);
                    expect(palm.x * size, label).toBeGreaterThan(left);
                    expect(palm.x * size, label).toBeLessThan(right);
                }
            }
        } finally {
            app.unmount();
            host.remove();
        }
    }
});
