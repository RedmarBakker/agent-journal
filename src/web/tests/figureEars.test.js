// @vitest-environment node
import {createHash} from "node:crypto";
import * as THREE from "three";
import {GLTFLoader} from "three/addons/loaders/GLTFLoader.js";
import {beforeAll, expect, test} from "vitest";
import {CLIPS, drawnPose, figureOf} from "../src/figure/figure.js";
import {withoutEars} from "../src/figure/ears.js";
import {HEADPHONES, headphonesAt, moveHeadphones} from "../src/figure/homie.js";
import {decodedFigure} from "./support/figureModel.js";

const voices = ["butler", "coach", "colleague", "homie", "squire"];
const figures = new Map();
const partsOf = (scene) => {
    const parts = [];
    scene.traverse((part) => { if (part.isSkinnedMesh) parts.push(part); });
    return parts;
};
const bytesOf = (array) => Buffer.from(array.buffer, array.byteOffset, array.byteLength);
const geometryHash = (geometry) => {
    const hash = createHash("sha256");
    for (const [name, attribute] of Object.entries(geometry.attributes)) hash.update(name).update(bytesOf(attribute.array));
    if (geometry.index) hash.update(bytesOf(geometry.index.array));
    return hash.digest("hex");
};

beforeAll(async () => {
    for (const voice of voices) figures.set(voice, await figureOf((await decodedFigure(voice)).buffer, voice, ""));
}, 60000);

test.each(voices)("the actual %s model loads without any fixed ear mesh or ear outline", (voice) => {
    const figure = figures.get(voice), names = [];
    figure.scene.traverse((part) => {
        names.push(part.name);
        expect(part.userData.part_id?.startsWith("ear_") ?? false, `${voice} ${part.name}`).toBe(false);
    });
    expect(names.some((name) => name.startsWith("ear_"))).toBe(false);
    expect(names).toContain("head_shell");
    expect(figure.headphones?.cups.length ?? 0).toBe(voice === "homie" ? 2 : 0);
    if (voice !== "homie") expect(names.some((name) => name.startsWith("homie_headphones"))).toBe(false);
});

test.each(voices)("removing %s's source ears preserves every other mesh, its geometry, skin and placement", async (voice) => {
    const {scene} = await new GLTFLoader().parseAsync((await decodedFigure(voice)).buffer, "");
    scene.updateMatrixWorld(true);
    const original = partsOf(scene), ears = original.filter((part) => part.name.startsWith("ear_"));
    expect(ears.map((part) => part.name).sort()).toEqual(["casing", "disc", "mount", "ring"].flatMap((name) => [`ear_${name}_l`, `ear_${name}_r`]));
    const kept = original.filter((part) => !ears.includes(part));
    const before = kept.map((part) => ({part, parent: part.parent, skeleton: part.skeleton, geometry: geometryHash(part.geometry), transform: part.matrixWorld.toArray(), material: part.material, data: JSON.stringify(part.userData)}));
    expect(withoutEars(original)).toEqual(kept);
    expect(partsOf(scene)).toEqual(kept);
    expect(ears.every((part) => part.parent === null)).toBe(true);
    for (const saved of before) {
        expect(saved.part.parent, saved.part.name).toBe(saved.parent);
        expect(saved.part.skeleton, saved.part.name).toBe(saved.skeleton);
        expect(saved.part.material, saved.part.name).toBe(saved.material);
        expect(geometryHash(saved.part.geometry), saved.part.name).toBe(saved.geometry);
        expect(saved.part.matrixWorld.toArray(), saved.part.name).toEqual(saved.transform);
        expect(JSON.stringify(saved.part.userData), saved.part.name).toBe(saved.data);
    }
});

test("Homie's only ear cups belong to the headset and leave the head with it", () => {
    const figure = figures.get("homie"), headset = figure.headphones;
    const groove = CLIPS.find(({name}) => name === "groove");
    expect(partsOf(figure.scene).some((part) => part.name.startsWith("homie_headphones__"))).toBe(false);
    expect(headset.colliders.colliders.every(({data}) => !data.mesh.name.startsWith("ear_"))).toBe(true);
    expect(headset.colliders.colliders.some(({data}) => data.mesh.name === "head_shell")).toBe(true);
    expect(headset.colliders.colliders.some(({data}) => data.mesh.name.startsWith("homie_backwards_cap__"))).toBe(true);
    const geometry = headset.cups.map((cup) => cup.children.map((part) => geometryHash(part.geometry)));
    const positions = [];
    for (const u of [0, 0.5, 1]) {
        const {pose, turned} = drawnPose(figure.rig, figure.stance, groove, u * (groove.frames - 1), 0, {posture: "stand"});
        moveHeadphones(headset, {u}, pose.moves(turned));
        positions.push(headset.cups.map((cup) => cup.position.clone()));
        for (const [index, cup] of headset.cups.entries()) {
            expect(cup.parent).toBe(headset.root);
            expect(cup.scale.toArray()).toEqual([1, 1, 1]);
            expect(cup.children.map((part) => geometryHash(part.geometry))).toEqual(geometry[index]);
        }
    }
    for (const index of [0, 1]) {
        expect(positions[1][index].y - positions[0][index].y).toBeGreaterThan(0.7);
        expect(positions[0][index].distanceTo(positions[2][index])).toBeLessThan(1e-7);
    }
    headset.root.removeFromParent();
    const remaining = [];
    figure.scene.traverse((part) => { if (/^ear_|^homie_headphones/.test(part.name)) remaining.push(part.name); });
    expect(remaining).toEqual([]);
    figure.scene.add(headset.root);
});

test("the worn pads fit the bare head without changing the wide cap approach or the neck pose", () => {
    const figure = figures.get("homie"), head = figure.scene.getObjectByName("head_shell");
    head.skeleton.update();
    const rest = new Map(["head", "chest"].map((bone) => [bone, new THREE.Matrix4()]));
    const worn = headphonesAt(0.5, rest);
    for (const {at, turn} of worn.cups) {
        const pad = new THREE.Vector3(0, 0, -(HEADPHONES.cup.depth / 2 + HEADPHONES.cup.pad)).applyQuaternion(turn).add(at);
        const surface = new THREE.Raycaster(pad, new THREE.Vector3(-Math.sign(at.x), 0, 0)).intersectObject(head, false)[0];
        expect(surface).toBeTruthy();
        expect(surface.distance).toBeGreaterThan(0.06);
        expect(surface.distance).toBeLessThan(0.1);
    }
    for (const u of [0, 1]) expect(headphonesAt(u, rest).cups[0].at.toArray()).toEqual([0.4, 1.96, 0.75]);
    for (const u of [0.2, 0.8]) expect(headphonesAt(u, rest).cups[0].at.x).toBeCloseTo(1.42, 10);
});
