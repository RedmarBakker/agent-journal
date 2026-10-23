// @vitest-environment node
import {expect, test} from "vitest";
import * as THREE from "three";
import {BUTLER, dressButler} from "../src/figure/butler.js";

// a stand-in for the butler's glb: each of its parts the dress reads, a small box bound to one bone in the glb's units
function butler() {
    const bone = new THREE.Bone();
    const skeleton = new THREE.Skeleton([bone]);
    const root = new THREE.Group();
    root.add(bone);
    const part = (name, at, colour = [0.02, 0.02, 0.05]) => {
        const geometry = new THREE.BoxGeometry(0.2, 0.2, 0.2);
        const count = geometry.attributes.position.count;
        geometry.setAttribute("skinIndex", new THREE.Uint16BufferAttribute(new Array(count * 4).fill(0), 4));
        geometry.setAttribute("skinWeight", new THREE.Float32BufferAttribute(Array.from({length: count * 4}, (_, i) => (i % 4 ? 0 : 1)), 4));
        const mesh = new THREE.SkinnedMesh(geometry, new THREE.MeshStandardMaterial({color: new THREE.Color(...colour)}));
        mesh.name = name;
        mesh.position.set(...at);
        root.add(mesh);
        root.updateMatrixWorld(true);
        mesh.bind(skeleton, mesh.matrixWorld);
        return mesh;
    };
    const shell = new THREE.MeshStandardMaterial({color: new THREE.Color(0.91, 0.83, 0.72)});
    const meshes = [
        part("butler_bowler_hat__crown", [0, 3.9, 0]),
        part("butler_bowler_hat__brim", [0, 3.55, 0]),
        part("butler_tailcoat__body", [0, 2, 0]),
        part("butler_tailcoat__tail_l", [0.3, 1.3, -0.3]),
        part("butler_tailcoat__tail_r", [-0.3, 1.3, -0.3]),
        part("butler_tailcoat__lapel_l", [0.3, 2.1, 0.4]),
        part("butler_bow_tie__knot", [0, 2.3, 0.43], [0.06, 0.05, 0.31]),
        part("butler_bow_tie__loop_l", [0.14, 2.3, 0.42], [0.17, 0.14, 0.86]),
        part("hand_shell_l", [1.9, 2.1, 0]),
        part("head_shell", [0, 3.2, 0]),
    ];
    for (const name of ["hand_shell_l", "head_shell"]) meshes.find((mesh) => mesh.name === name).material = shell;
    return meshes;
}

// a dressed part's corners in the glb's world as it is bound
function cornersOf(mesh) {
    const position = mesh.geometry.attributes.position;
    return Array.from({length: position.count}, (_, i) => new THREE.Vector3().fromBufferAttribute(position, i).applyMatrix4(mesh.matrixWorld));
}

test("the butler wears a top hat: tall with straight sides, a flat crown, a narrow brim curled up at the sides and a dark satin band, square on the head", () => {
    const dressed = dressButler(butler());
    const names = dressed.map((mesh) => mesh.name);
    // the bowler and the short tails are gone, the top hat, its band, the collar's wing tips and the long tails are in
    expect(names.some((name) => name.startsWith("butler_bowler_hat"))).toBe(false);
    expect(names).toEqual(expect.arrayContaining(["butler_top_hat", "butler_top_hat_band", "butler_wing_collar_l", "butler_wing_collar_r", "butler_tail_l", "butler_tail_r"]));
    const {base, crown, height, brim, thick} = BUTLER.hat;
    const hat = cornersOf(dressed.find((mesh) => mesh.name === "butler_top_hat"));
    const out = (point) => Math.hypot(point.x, point.z);
    // tall, upright and square: its crown flat at the top, every side point the crown's width out from the middle
    expect(Math.max(...hat.map((point) => point.y))).toBeCloseTo(base + height, 5);
    expect(height).toBeGreaterThan(crown);
    for (const point of hat.filter((each) => each.y > base + thick + 0.2)) expect(out(point) <= crown + 1e-6).toBe(true);
    for (const point of hat.filter((each) => each.y > base + thick + 0.2 && each.y < base + height - 1e-6)) expect(out(point)).toBeCloseTo(crown, 5);
    // a narrow brim, a quarter of the crown's width at most, its edge higher at the left and right than at the front and back
    expect(brim).toBeLessThanOrEqual(crown / 4);
    const edge = hat.filter((point) => out(point) > crown + brim - 1e-3 && point.y < base + thick + 0.3);
    const sides = edge.filter((point) => Math.abs(point.x) > crown + brim - 0.01);
    const front = edge.filter((point) => Math.abs(point.z) > crown + brim - 0.01);
    expect(Math.min(...sides.map((point) => point.y))).toBeGreaterThan(Math.max(...front.map((point) => point.y)));
    // its band a satin a shade off the hat's own, and dark
    const band = dressed.find((mesh) => mesh.name === "butler_top_hat_band").material.color.toArray();
    expect(band).toEqual(BUTLER.satin);
    expect(Math.max(...band)).toBeLessThan(0.3);
});

test("the butler's gloves, bow tie and collar are white, its head keeps its own colour, and its tails hang behind it to the knees", () => {
    const dressed = dressButler(butler());
    const colour = (name) => dressed.find((mesh) => mesh.name === name).material.color.toArray();
    for (const name of ["hand_shell_l", "butler_bow_tie__knot", "butler_bow_tie__loop_l", "butler_wing_collar_l"]) expect(colour(name), name).toEqual(BUTLER.white);
    expect(colour("head_shell")).toEqual(new THREE.Color(0.91, 0.83, 0.72).toArray());
    for (const side of ["l", "r"]) {
        const tail = cornersOf(dressed.find((mesh) => mesh.name === `butler_tail_${side}`));
        expect(Math.max(...tail.map((point) => point.z))).toBeLessThan(0);
        expect(Math.min(...tail.map((point) => point.y))).toBeLessThan(0.8);
        expect(tail.every((point) => (side === "l" ? point.x > 0 : point.x < 0))).toBe(true);
    }
});
