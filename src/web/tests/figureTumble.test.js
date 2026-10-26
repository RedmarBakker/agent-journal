// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, TUMBLE} from "../src/figure/figure.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "tumble");
const index = JSON.parse(readFileSync(new URL("../public/voices/figures/figures.json", import.meta.url)));

// The real GLBs publish each mesh's position bounds even though their vertices are Draco compressed. Bound every part attached to a
// foot, including collars, laces and soles; convert their GLB axes to the posing axes before applying the foot's movement.
const shoesOf = (voice) => {
    const bytes = readFileSync(new URL(`../public/voices/figures/${index[voice]}`, import.meta.url));
    const gltf = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString("utf8"));
    return gltf.nodes.flatMap((node) => {
        if (node.mesh === undefined || !node.extras?.attachment?.startsWith("foot_")) return [];
        const bone = node.extras.attachment.replace(/_root$/, "");
        return gltf.meshes[node.mesh].primitives.flatMap((primitive) => {
            const {min, max} = gltf.accessors[primitive.attributes.POSITION];
            return [min[0], max[0]].flatMap((x) => [min[1], max[1]].flatMap((y) => [min[2], max[2]].map((z) => ({bone, point: new THREE.Vector3(x, -z, y)}))));
        });
    });
};

const posed = (voice, u) => {
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf(voice), (u * (clip.frames - 1)) / clip.frames);
    return pose.moves(0);
};

test("tumbling rolls the complete boots onto their tops without putting toes, soles or laces through the floor", () => {
    for (const voice of Object.keys(stances)) {
        const shoes = shoesOf(voice);
        expect(shoes.length, `${voice}: actual foot geometry is covered`).toBeGreaterThan(0);
        for (let sample = 0; sample <= 240; sample++) {
            const moves = posed(voice, sample / 240);
            const bottom = Math.min(...shoes.map(({bone, point}) => point.clone().applyMatrix4(moves.get(bone)).z));
            expect(bottom, `${voice}: boot bounds at ${sample}/240`).toBeGreaterThanOrEqual(-1e-5);
        }
        const kneeling = posed(voice, 0.4);
        const bottom = Math.min(...shoes.map(({bone, point}) => point.clone().applyMatrix4(kneeling.get(bone)).z));
        expect(bottom, `${voice}: boots settle at the floor`).toBeLessThan(0.06);
        for (const side of ["l", "r"]) {
            const toes = new THREE.Vector3(0, -1, 0).transformDirection(kneeling.get(`foot_${side}`));
            expect(toes.y, `${voice} ${side}: toes point back along the floor`).toBeGreaterThan(0.999);
            expect(Math.abs(toes.z), `${voice} ${side}: toes never point down while kneeling`).toBeLessThan(1e-5);
        }
    }
});

test("the tumble's feet enter and leave the kneeling pose continuously and finish where they started", () => {
    for (const voice of Object.keys(stances)) {
        for (const u of [...TUMBLE.down, ...TUMBLE.up, TUMBLE.down[0] + (TUMBLE.down[1] - TUMBLE.down[0]) / 2]) {
            const [before, after] = [posed(voice, u - 1e-6), posed(voice, u + 1e-6)];
            for (const side of ["l", "r"]) {
                const bone = `foot_${side}`;
                const jump = Math.max(...before.get(bone).elements.map((value, index) => Math.abs(value - after.get(bone).elements[index])));
                expect(jump, `${voice} ${side}: continuous feet at ${u}`).toBeLessThan(0.001);
            }
        }
        const [start, end] = [posed(voice, 0), posed(voice, 1)];
        for (const side of ["l", "r"]) {
            const bone = `foot_${side}`;
            for (let index = 0; index < 16; index++) expect(end.get(bone).elements[index]).toBeCloseTo(start.get(bone).elements[index], 12);
        }
    }
});
