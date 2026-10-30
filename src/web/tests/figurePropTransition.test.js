// @vitest-environment node
import * as THREE from "three";
import {expect, test} from "vitest";
import {PROP_FADE_SECONDS, fadeProp, restorePropOpacity, transitionProps} from "../src/figure/propTransition.js";

const empty = () => new Map();
const held = (value = {bone: "hand_l", at: new THREE.Vector3(0, 0, 0), turn: {}, open: 0.7}) => new Map([["book", value]]);

test("an appearing prop fades in by time and retains its descriptor until its exit has faded completely", () => {
    let state = transitionProps(null, empty(), 0);
    state = transitionProps(state, held(), 1);
    expect(state.entries.get("book").alpha).toBe(0);
    expect(state.active).toBe(true);
    state = transitionProps(state, held(), 1 + PROP_FADE_SECONDS / 2);
    expect(state.entries.get("book").alpha).toBeCloseTo(0.5, 9);
    state = transitionProps(state, held(), 1 + PROP_FADE_SECONDS);
    expect(state.entries.get("book").alpha).toBe(1);
    expect(state.active).toBe(false);
    state = transitionProps(state, empty(), 2);
    expect(state.entries.get("book")).toMatchObject({alpha: 1, to: 0, value: {open: 0.7}});
    expect(state.present).toBe(true);
    state = transitionProps(state, empty(), 2 + PROP_FADE_SECONDS / 2);
    expect(state.entries.get("book").alpha).toBeCloseTo(0.5, 9);
    state = transitionProps(state, empty(), 2 + PROP_FADE_SECONDS);
    expect(state.entries.size).toBe(0);
    expect(state.present).toBe(false);
    expect(state.active).toBe(false);
});

test("interrupting and reversing a prop transition preserves the opacity already on screen", () => {
    let state = transitionProps(null, empty(), 0);
    state = transitionProps(state, held(), 1);
    state = transitionProps(state, held(), 1.04);
    const rising = state.entries.get("book").alpha;
    state = transitionProps(state, empty(), 1.04);
    expect(state.entries.get("book").alpha).toBe(rising);
    state = transitionProps(state, empty(), 1.08);
    const falling = state.entries.get("book").alpha;
    expect(falling).toBeLessThan(rising);
    state = transitionProps(state, held(), 1.08);
    expect(state.entries.get("book").alpha).toBe(falling);
    state = transitionProps(state, held(), 1.24);
    expect(state.entries.get("book").alpha).toBe(1);
});

test("a stalled or repeated frame does not advance a fade, and a clock rewind does not reverse it", () => {
    let state = transitionProps(null, held(), 10);
    state = transitionProps(state, held(), 10.08);
    const alpha = state.entries.get("book").alpha;
    for (let frame = 0; frame < 20; frame++) state = transitionProps(state, held(), 10.08);
    expect(state.entries.get("book").alpha).toBe(alpha);
    state = transitionProps(state, held(), 9);
    expect(state.entries.get("book").alpha).toBe(alpha);
});

test("static samples snap to their own target and a later live interruption fades from that exact sample", () => {
    let state = transitionProps(null, held(), 0);
    state = transitionProps(state, held());
    expect(state.entries.get("book").alpha).toBe(1);
    expect(state.active).toBe(false);
    state = transitionProps(state, empty(), 5);
    expect(state.entries.get("book").alpha).toBe(1);
    state = transitionProps(state, empty());
    expect(state.entries.size).toBe(0);
});

test("retained descriptors keep their authored vectors and shape when the next pose changes its input", () => {
    const source = {bone: "hand_l", at: new THREE.Vector3(1, 2, 3), turn: {x: 30}, size: 1.5};
    let state = transitionProps(null, held(source));
    source.at.x = 99;
    source.turn.x = -80;
    state = transitionProps(state, empty(), 2);
    expect(state.entries.get("book").value.at.toArray()).toEqual([1, 2, 3]);
    expect(state.entries.get("book").value.turn).toEqual({x: 30});
    expect(state.entries.get("book").value.size).toBe(1.5);
});

test("a faded prop restores shader, fill, outline and authored transparent material state without accumulating opacity", () => {
    const root = new THREE.Group();
    const fill = new THREE.MeshBasicMaterial({opacity: 1});
    const lens = new THREE.MeshBasicMaterial({transparent: true, opacity: 0.18, depthWrite: false});
    const shader = new THREE.ShaderMaterial({uniforms: {alpha: {value: 1}}});
    for (const material of [fill, lens, shader]) root.add(new THREE.Mesh(new THREE.PlaneGeometry(), material));
    fadeProp(root, 0.5);
    const compiled = fill.version;
    expect(compiled).toBeGreaterThan(0);
    expect([fill.opacity, lens.opacity, shader.uniforms.alpha.value]).toEqual([0.5, 0.09, 0.5]);
    expect([fill, lens, shader].every((material) => material.transparent && !material.depthWrite)).toBe(true);
    restorePropOpacity(root);
    fadeProp(root, 0.5);
    expect(fill.version, "a fade does not recompile the same transparent variant every frame").toBe(compiled);
    expect([fill.opacity, lens.opacity, shader.uniforms.alpha.value]).toEqual([0.5, 0.09, 0.5]);
    restorePropOpacity(root);
    fadeProp(root, 1);
    expect(fill.version, "the opaque fragment variant is restored at the end").toBeGreaterThan(compiled);
    expect(fill).toMatchObject({opacity: 1, transparent: false, depthWrite: true});
    expect(lens).toMatchObject({opacity: 0.18, transparent: true, depthWrite: false});
    expect(shader.uniforms.alpha.value).toBe(1);
    fadeProp(root, 0);
    expect(root.visible).toBe(false);
});
