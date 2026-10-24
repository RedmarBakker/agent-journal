// @vitest-environment node
import {readFileSync, readdirSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, heartBeat, pixelTexture, showPixels} from "../src/figure/figure.js";
import {blinkOpenness, BLINK} from "../src/figure/blink.js";
import {VISOR} from "../src/figure/visor.js";
import {COLOURS, EYE_SPOTS, FRAMES, GRID, PICTURES, frameFor, litPixels} from "../src/figure/visorPixels.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// a face with its eyes open and nothing in their place, with `changes`
const face = (changes = {}) => ({eyed: true, eyes: 1, glance: [0, 0], tint: null, hearts: 0, stars: 0, squeezed: 0, sign: null, ...changes});
// the lit pixels as "column,row" names
const names = (lit) => lit.map(({column, row}) => `${column},${row}`).sort();

// the pixels picture `name` lights in each eye's place, unmoved, turned round on the right when `turned`
function pictured(name, turned = false) {
    const rows = PICTURES[name];
    const width = rows[0].length;
    return EYE_SPOTS.flatMap((spot) =>
        rows.flatMap((line, y) =>
            [...line].flatMap((mark, x) => {
                if (mark === ".") return [];
                const column = spot.column - Math.floor(width / 2) + (turned && spot.mirrored ? width - 1 - x : x);
                return [`${column},${spot.row - Math.floor(rows.length / 2) + y}`];
            }),
        ),
    ).sort();
}

// the bounds of the mesh named `name` in a voice's model, from its file
function boundsOf(file, name) {
    const bytes = readFileSync(file);
    const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
    const node = json.nodes.find((each) => each.name === name);
    const {min, max} = json.accessors[json.meshes[node.mesh].primitives[0].attributes.POSITION];
    return {min, max};
}

test("the visor is a screen of exactly the grid's pixels: at least 24 by 8, square on every voice's visor, one texel each, and only the lit ones lit", () => {
    expect(GRID.columns).toBeGreaterThanOrEqual(24);
    expect(GRID.rows).toBeGreaterThanOrEqual(8);
    const figures = new URL("../public/voices/figures/", import.meta.url);
    for (const file of readdirSync(figures).filter((each) => each.endsWith(".glb"))) {
        const {min, max} = boundsOf(new URL(file, figures), "face_screen");
        const [wide, high] = [(max[0] - min[0]) / GRID.columns, (max[1] - min[1]) / GRID.rows];
        expect(Math.abs(wide / high - 1), `${file} square pixels`).toBeLessThan(0.03);
        // each eye's pictures centred within a pixel of where the model's eye was
        for (const [eye, spot] of [["eye_r", EYE_SPOTS[0]], ["eye_l", EYE_SPOTS[1]]]) {
            const was = boundsOf(new URL(file, figures), eye);
            const column = ((was.min[0] + was.max[0]) / 2 - min[0]) / wide - 0.5;
            const row = (max[1] - (was.min[1] + was.max[1]) / 2) / high - 0.5;
            expect(Math.abs(column - spot.column), `${file} ${eye} across`).toBeLessThanOrEqual(1);
            expect(Math.abs(row - spot.row), `${file} ${eye} up`).toBeLessThanOrEqual(1);
        }
    }
    // the screen's texture has a texel for each pixel, and shows the lit ones in their colour and every other one off
    const texture = pixelTexture();
    expect([texture.image.width, texture.image.height]).toEqual([GRID.columns, GRID.rows]);
    expect(texture.magFilter).toBe(THREE.NearestFilter);
    const lit = litPixels(face());
    showPixels(texture, lit);
    const data = texture.image.data;
    const on = [];
    for (let index = 0; index < GRID.columns * GRID.rows; index++) if (data[index * 4 + 3]) on.push(`${index % GRID.columns},${Math.floor(index / GRID.columns)}`);
    expect(on.sort()).toEqual(names(lit));
    const [first] = lit;
    expect([...data.subarray((first.row * GRID.columns + first.column) * 4, (first.row * GRID.columns + first.column) * 4 + 3)]).toEqual(COLOURS.eyes.map((part) => Math.round(part * 255)));
    // every picture fits the grid in each eye's place
    for (const [name, rows] of Object.entries(PICTURES)) {
        expect(rows.every((line) => line.length === rows[0].length), name).toBe(true);
        expect(rows.length, name).toBeLessThanOrEqual(GRID.rows);
        expect(EYE_SPOTS[0].column + rows[0].length / 2 < EYE_SPOTS[1].column - rows[0].length / 2 + 1, `${name} two side by side`).toBe(true);
    }
});

test("the eyes, their blink, the hearts, the stars, the check and the cross are pixel pictures on the grid", () => {
    expect(names(litPixels(face()))).toEqual(pictured("eye_open"));
    expect(names(litPixels(face({eyes: BLINK.shut})))).toEqual(pictured("eye_shut"));
    expect(names(litPixels(face({eyes: 1.5})))).toEqual(pictured("eye_wide"));
    expect(names(litPixels(face({hearts: 1.2})))).toEqual(pictured("heart_big"));
    expect(names(litPixels(face({stars: 1})))).toEqual(pictured("star_big"));
    expect(names(litPixels(face({squeezed: 1})))).toEqual(pictured("squeezed", true));
    // a run's end: the cross and the check in the colour they are given, the eyes gone meanwhile
    for (const [name, tone] of [["cross", "bad"], ["tick", "good"]]) {
        const lit = litPixels(face({sign: {name, strength: 1, colour: VISOR.colours[tone]}}));
        expect(names(lit), name).toEqual(pictured(name));
        expect(lit.every((pixel) => pixel.colour === VISOR.colours[tone]), name).toBe(true);
    }
    // a tint colours the eyes; a glance moves them a pixel; with the eyes out nothing is lit
    expect(litPixels(face({tint: [1, 0.35, 0.3]})).every((pixel) => pixel.colour.join() === "1,0.35,0.3")).toBe(true);
    const glanced = litPixels(face({glance: [0.35, 0.3]}));
    expect(names(glanced)).toEqual(pictured("eye_open").map((name) => name.split(",").map(Number)).map(([column, row]) => `${column + 1},${row - 1}`).sort());
    expect(litPixels(face({eyed: false}))).toEqual([]);
});

test("every change of the eyes steps through the frames of the grid: a blink closes and opens through them, the hearts beat and the stars twinkle", () => {
    const steps = (sizes, family) => sizes.map((size) => frameFor(family, size)).filter((frame, index, all) => frame !== all[index - 1]);
    // a blink, at the screen's frame rate
    const blink = Array.from({length: 1 + (BLINK.close + BLINK.open) / 5}, (_, index) => blinkOpenness(index * 5));
    expect(steps(blink, "eyes")).toEqual(["eye_open", "eye_narrowed", "eye_half", "eye_shut", "eye_half", "eye_narrowed", "eye_open"]);
    // the heart eyes over a beat: a strong swell and a weaker one, each to the big heart and back
    const beat = Array.from({length: 81}, (_, index) => heartBeat(index / 100));
    expect(steps(beat, "hearts")).toEqual(["heart_small", "heart_big", "heart_small", "heart_big", "heart_small"]);
    // the stars of the eager figure grow in and twinkle as they sparkle
    const eager = CLIPS.find((clip) => clip.name === "eager");
    const stars = Array.from({length: eager.frames}, (_, frame) => {
        const pose = new Posing(RIG, "stand", 0);
        eager.pose(pose, stanceOf("butler"), frame / eager.frames);
        return pose.stars;
    });
    const twinkles = steps(stars, "stars").filter(Boolean);
    expect(twinkles[0]).toBe(FRAMES.stars[0][0]);
    expect(twinkles.filter((frame) => frame === "star_twinkle").length).toBeGreaterThan(1);
    expect(twinkles).toContain("star_big");
    // a sign opens up and down from its middle as it comes and closes as it goes
    const rows = (strength) => new Set(litPixels(face({sign: {name: "cross", strength, colour: [1, 0, 0]}})).map((pixel) => pixel.row)).size;
    expect(rows(0.3)).toBeLessThan(rows(0.7));
    expect(rows(0.7)).toBeLessThan(rows(1));
});
