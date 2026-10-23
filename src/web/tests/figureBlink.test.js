// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {BLINK, blinkOpenness, nextBlinkMs} from "../src/figure/blink.js";
import {CLIPS, Posing} from "../src/figure/figure.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

test("a blink is a quick close and open, about 150 milliseconds, timed on the page's own clock apart from any clip's frame rate", () => {
    expect(BLINK.close + BLINK.open).toBe(150);
    expect([blinkOpenness(-1), blinkOpenness(150), blinkOpenness(400)]).toEqual([1, 1, 1]);
    expect(blinkOpenness(BLINK.close)).toBeCloseTo(BLINK.shut, 6);
    // drawn on every display frame: a 60 Hz screen draws it in nine steps, closing in the first four, where the clips run at 6 to 20
    // frames a second and would draw it in one to three
    const frames = Array.from({length: 9}, (_, index) => blinkOpenness(index * (1000 / 60)));
    expect(new Set(frames.map((open) => open.toFixed(3))).size).toBeGreaterThanOrEqual(7);
    expect(frames.slice(1, 4).every((open, index) => open < frames[index])).toBe(true);
    expect(frames.slice(5).every((open, index) => open > frames[index + 4])).toBe(true);
    expect(Math.max(...CLIPS.map((clip) => clip.fps))).toBeLessThanOrEqual(20);
    expect(nextBlinkMs(() => 0)).toBe(BLINK.every[0]);
    expect(nextBlinkMs(() => 0.999999)).toBeCloseTo(BLINK.every[1], 0);
});

test("no clip blinks by itself any more: idle's eyes stay open on every frame for every voice, and there is no blink clip", () => {
    expect(CLIPS.some((clip) => clip.name === "blink")).toBe(false);
    const idle = CLIPS.find((clip) => clip.name === "idle");
    for (const voice of Object.keys(stances)) {
        for (let frame = 0; frame < idle.frames * 4; frame++) {
            const pose = new Posing(RIG, "stand", 0);
            idle.pose(pose, stanceOf(voice), frame / (idle.frames * 4));
            expect(pose.eyes, `${voice} ${frame}`).toBe(1);
        }
    }
});
