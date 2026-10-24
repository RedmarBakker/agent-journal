// @vitest-environment node
import * as THREE from "three";
import {expect, test} from "vitest";
import {SCREEN, pixelTexture, screenFrame, screenMaterial, showPixels} from "../src/figure/figure.js";
import {FRAMES_PER_SECOND, GRID, litPixels} from "../src/figure/visorPixels.js";

// the visor's material made for a visor the size of every voice's, 1.53 by 0.72 of the figure's units
function visor() {
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1.53, 0.72), new THREE.MeshBasicMaterial({color: 0x030303}));
    mesh.position.set(0, 3.09, 0.8);
    mesh.updateMatrixWorld(true);
    return screenMaterial(mesh);
}

test("the visor's glass is one flat near-black colour, unshaded by the light, with a thin darker bezel round its rounded edge and a faint glare at the top", () => {
    const material = visor();
    const glass = material.uniforms.glass.value.toArray();
    expect(glass).toEqual(SCREEN.glass);
    expect(Math.max(...glass), "near-black").toBeLessThan(0.02);
    expect(Math.max(...glass) - Math.min(...glass), "no colour cast").toBeLessThan(0.01);
    // flat: the screen's colour reads neither the light nor the normal, so no gradient falls across it
    expect(material.fragmentShader).not.toMatch(/dot\(normal|uniform vec3 shade|uniform vec3 light/);
    // the bezel: a few hundredths of a unit wide, a good deal darker than the glass, round the visor's own rounded outline
    const [width, shade, round] = material.uniforms.bezel.value.toArray();
    expect(width).toBeGreaterThan(0.01);
    expect(width).toBeLessThan(0.08);
    expect(shade).toBeGreaterThan(0.5);
    expect(round).toBeCloseTo(SCREEN.bezel.round, 6);
    // the glare: faint, and only across the top of the glass
    const [glare, from] = material.uniforms.glare.value.toArray();
    expect(glare).toBeGreaterThan(0);
    expect(glare).toBeLessThan(Math.max(...glass) * 3);
    expect(from).toBeGreaterThanOrEqual(0.3);
});

test("each lit pixel glows in its own colour with a soft halo on the black about it, and the pixels that are off show only faintly as a grid", () => {
    const material = visor();
    // the halo: as bright as a good share of the pixel, fading over most of a pixel and reaching beyond its neighbours
    const [strength, soft, reach] = material.uniforms.halo.value.toArray();
    expect(strength).toBeGreaterThan(0.2);
    expect(strength).toBeLessThan(1);
    expect(soft).toBeGreaterThan(0.3);
    expect(reach).toBeGreaterThanOrEqual(2);
    // the screen gathers the glow of the lit pixels around each point, fading with their distance, and draws a lit pixel in its own colour
    expect(material.fragmentShader).toMatch(/for \(int dx = -2; dx <= 2; dx\+\+\)/);
    expect(material.fragmentShader).toMatch(/spill \+= near\.rgb \* near\.a \* exp\(/);
    // a lit pixel is drawn brighter than its colour, brightest at its middle
    expect(material.fragmentShader).toMatch(/mix\(screen, glowing, shown\.a \* pixel\)/);
    expect(material.uniforms.shine.value.toArray()).toEqual([SCREEN.shine.lift, SCREEN.shine.core, SCREEN.shine.tightness]);
    expect(SCREEN.shine.lift).toBeGreaterThan(0);
    expect(SCREEN.shine.core).toBeGreaterThan(0);
    // the pixels change six times a second, like a small real screen
    expect(FRAMES_PER_SECOND).toBe(6);
    // an off pixel: a touch brighter than the glass, far fainter than any lit one
    expect(material.uniforms.off.value).toBe(SCREEN.off);
    expect(SCREEN.off).toBeGreaterThan(0);
    expect(SCREEN.off).toBeLessThan(Math.max(...SCREEN.glass));
    // the pixels it glows with are the lit pixels of the screen's texture, one texel each, and only those
    const texture = material.uniforms.pixels.value;
    expect([texture.image.width, texture.image.height]).toEqual([GRID.columns, GRID.rows]);
    const lit = litPixels({eyed: true, eyes: 1, shift: [0, 0], tint: null, hearts: 1.2, stars: 0, squeezed: 0, sign: null});
    showPixels(texture, lit);
    const on = [...Array(GRID.columns * GRID.rows).keys()].filter((index) => texture.image.data[index * 4 + 3]);
    expect(on.length).toBe(lit.length);
    expect(pixelTexture().image.data.every((part) => part === 0), "a new screen is all off").toBe(true);
});

test("the screen shows every picture the face passes through, one per screen frame, so a blink's shut eye is never skipped", () => {
    const material = {uniforms: {pixels: {value: pixelTexture()}}, userData: {}};
    const picture = (row) => [{column: 1, row, colour: [1, 1, 1]}];
    const lit = () => [...Array(GRID.columns * GRID.rows).keys()].filter((index) => material.uniforms.pixels.value.image.data[index * 4 + 3]).map((index) => Math.floor(index / GRID.columns));
    screenFrame(material, picture(1), 0);
    expect(lit()).toEqual([1]);
    // within one screen frame the face goes open, shut and open again: each waits its turn
    screenFrame(material, picture(2), 0);
    screenFrame(material, picture(3), 0);
    expect(lit()).toEqual([1]);
    screenFrame(material, picture(3), 1);
    expect(lit()).toEqual([2]);
    screenFrame(material, picture(3), 2);
    expect(lit()).toEqual([3]);
    screenFrame(material, picture(3), 3);
    expect(lit(), "a still face changes nothing").toEqual([3]);
});
