// @vitest-environment node
import * as THREE from "three";
import {beforeEach, expect, test} from "vitest";
import {ACTS} from "../src/figure/acts.js";
import {FRAMED} from "../src/figure/frame.js";
import {phoneSide} from "../src/figure/perches.js";
import {phoneFootprint} from "../src/figure/phonePlacement.js";
import {phonePose, phoneProps} from "./support/phoneGeometry.js";

const figure = {size: 112, below: 0.05}, unit = figure.size / FRAMED.height;
const props = phoneProps();

beforeEach(() => {
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.document = {querySelector: () => null, querySelectorAll: () => []};
});

// Actual rendered vertices, with the shader's outline displacement, after the telephone's pose and landing squash.
function renderedBounds(facing, way, u, posture = "sit") {
    phonePose(u, "butler", {posture, facing, phoneWay: way}, props);
    let left = Infinity, right = -Infinity;
    for (const name of ["telephone", "telephone_handset"]) {
        props.propByName.get(name).traverse((mesh) => {
            if (!mesh.name || !mesh.geometry) return;
            const {position, hullNormal} = mesh.geometry.attributes;
            const push = mesh.children.find((child) => child.material?.uniforms?.push)?.material.uniforms.push.value ?? 0;
            for (let index = 0; index < position.count; index++) {
                const point = new THREE.Vector3().fromBufferAttribute(position, index);
                if (push) point.addScaledVector(new THREE.Vector3().fromBufferAttribute(hullNormal, index), push);
                point.applyMatrix4(mesh.matrixWorld);
                left = Math.min(left, point.x); right = Math.max(right, point.x);
            }
        });
    }
    return {left, right};
}

test.each([0, 25, 70, 90, 110, 160, 180, 200, 250, 270, 290, 335])("the floor reservation contains the real outlined phone and cradle ends at %s degrees", (facing) => {
    const act = ACTS.phone_call;
    const samples = [0, ...Array.from({length: 9}, (_, index) => act.settle[0] + (act.settle[1] - act.settle[0]) * index / 8), act.reach[0], act.hang[1]];
    for (const way of [-1, 1]) {
        const footprint = phoneFootprint(facing, way, act);
        for (const u of samples) {
            const actual = renderedBounds(facing, way, u);
            expect(actual.left, `${facing} ${way} ${u}: left`).toBeGreaterThanOrEqual(footprint.left - 1e-6);
            expect(actual.right, `${facing} ${way} ${u}: right`).toBeLessThanOrEqual(footprint.right + 1e-6);
        }
    }
});

test.each([
    {face: 70, x: 347, left: 311, right: 380, way: 1},
    {face: 290, x: 333, left: 300, right: 369, way: -1},
])("an angled seat uses the supported hand when both phone positions project the same way ($face degrees)", ({face, x, left, right, way}) => {
    const floor = {element: {}, left, right};
    const spot = {x, y: 600, face, posture: "sit", on: floor.element};
    const original = {...spot};
    expect(phoneSide(spot, figure, [floor])).toBe(way);
    expect(spot).toEqual(original);
    const actual = renderedBounds(face, way, ACTS.phone_call.reach[0]);
    expect(x + actual.left * unit).toBeGreaterThanOrEqual(left);
    expect(x + actual.right * unit).toBeLessThanOrEqual(right);
    const other = renderedBounds(face, -way, ACTS.phone_call.reach[0]);
    expect(x + other.left * unit < left || x + other.right * unit > right).toBe(true);
});

test.each([0, 25, 70, 90, 180, 250, 270, 290])("corners and window edges keep the entire phone supported whenever either placement fits at %s degrees", (face) => {
    window.innerWidth = 900;
    for (const [left, right] of [[300, 700], [300, 940], [-40, 300]]) {
        const floor = {element: {}, left, right};
        const supported = {left: Math.max(left, 0), right: Math.min(right, window.innerWidth)};
        for (const x of [supported.left + 11.2, supported.left + 36, (supported.left + supported.right) / 2, supported.right - 36, supported.right - 11.2]) {
            const spot = {x, y: 600, face, posture: "sit", on: floor.element};
            const fits = (way) => {
                const bounds = phoneFootprint(face, way, ACTS.phone_call);
                return x + bounds.left * unit >= supported.left && x + bounds.right * unit <= supported.right;
            };
            if ([-1, 1].some(fits)) expect(fits(phoneSide(spot, figure, [floor])), `${face} ${x} ${left}..${right}`).toBe(true);
        }
    }
});

test("a seat too short for either telephone placement chooses the smallest overhang without moving the figure", () => {
    const floor = {element: {}, left: 490, right: 516};
    const spot = {x: 505, y: 600, face: 70, posture: "sit", on: floor.element};
    const spill = (way) => {
        const bounds = phoneFootprint(spot.face, way, ACTS.phone_call);
        return Math.max(0, floor.left - spot.x - bounds.left * unit) + Math.max(0, spot.x + bounds.right * unit - floor.right);
    };
    const way = phoneSide(spot, figure, [floor]);
    expect(spill(way)).toBeLessThanOrEqual(spill(-way));
    expect(spot.x).toBe(505);
    expect(spot.face).toBe(70);
});
