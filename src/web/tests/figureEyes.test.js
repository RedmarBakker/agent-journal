import {readFileSync} from "node:fs";
import {dirname} from "node:path";
import {fileURLToPath} from "node:url";
import * as THREE from "three";
import {describe, expect, it} from "vitest";
import {CLIPS, EYES, LOOK_EASE, Posing, lookStrength} from "../src/figure/figure.js";
import {FRAMES, PICTURES} from "../src/figure/visorPixels.js";
import {PILE} from "../src/figure/pile.js";
import {LOOK_SECONDS} from "../src/figure/reactions.js";

const {rig, stances} = JSON.parse(readFileSync(`${dirname(fileURLToPath(import.meta.url))}/figureRig.json`));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// the pictures approved in place of the eyes' arcs on the visor: the hearts, the stars, the squeezed eyes, and the crosses and the ticks at
// a run's end (visor.js SIGN)
const APPROVED = ["cross", "heart_big", "heart_small", "heart_tiny", "squeezed", "star_big", "star_small", "star_twinkle", "tick"];
const FRAMES = 12;

describe("the eyes keep their arcs", () => {
    it("walks every act of every voice and finds no filled, oval or round eye shape drawn", () => {
        for (const voice of Object.keys(stances)) {
            for (const clip of CLIPS.filter((each) => !each.voices || each.voices.includes(voice))) {
                for (let frame = 0; frame < FRAMES; frame++) {
                    const pose = new Posing(RIG, clip.postures[0], 0);
                    clip.pose(pose, stanceOf(voice), frame / FRAMES);
                    expect(pose.eyeShape, `${voice} ${clip.name} ${frame}`).toBe(null);
                }
            }
        }
    });

    it("draws no picture in place of the eyes but the approved ones, and no look takes on a shape", () => {
        expect(Object.keys(PICTURES).filter((name) => !FRAMES.eyes.some(([frame]) => frame === name)).sort()).toEqual(APPROVED);
        for (const [mood, look] of Object.entries(EYES)) expect(look.shape, mood).toBeUndefined();
        const looks = PILE.filter((entry) => entry.kind === "look").map((entry) => entry.name);
        for (const mood of looks) expect(EYES[mood]?.shape, mood).toBeUndefined();
        for (const gone of ["focused", "narrowed", "bright", "calm", "eyeing", "pondering"]) {
            expect(EYES[gone], gone).toBeUndefined();
            expect(PICTURES[gone], gone).toBeUndefined();
            expect(looks, gone).not.toContain(gone);
        }
    });

    it("eases a look in and back to the usual eyes", () => {
        const at = (seconds) => lookStrength({seconds, lasts: LOOK_SECONDS});
        expect(at(0)).toBe(0);
        expect(at(LOOK_EASE.into / 2)).toBeGreaterThan(0);
        expect(at(LOOK_EASE.into / 2)).toBeLessThan(1);
        expect(at(LOOK_SECONDS / 2)).toBe(1);
        expect(at(LOOK_SECONDS - LOOK_EASE.out / 2)).toBeGreaterThan(0);
        expect(at(LOOK_SECONDS - LOOK_EASE.out / 2)).toBeLessThan(1);
        expect(at(LOOK_SECONDS)).toBe(0);
    });
});
