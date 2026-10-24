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

test("the visor's face is one plain near-black colour, unshaded, with nothing laid over it: no faint grid of unlit pixels, no glare, no rim and no halo", () => {
    const material = visor();
    const glass = material.uniforms.glass.value.toArray();
    expect(glass).toEqual(SCREEN.glass);
    expect(Math.max(...glass), "near-black").toBeLessThan(0.02);
    expect(Math.max(...glass) - Math.min(...glass), "no colour cast").toBeLessThan(0.01);
    // flat: the screen's colour reads neither the light nor the normal, so no gradient falls across it
    expect(material.fragmentShader).not.toMatch(/dot\(normal|uniform vec3 shade|uniform vec3 light/);
    // the face is the glass alone, and a point of it is that colour wherever no lit pixel is, the eyes the only thing drawn on it
    expect(material.fragmentShader).toMatch(/vec3 screen = glass;/);
    expect(material.fragmentShader).toMatch(/vec3 drawn = mix\(screen, glowing, shown\.a \* pixel\);/);
    // nothing else tints it: no unlit pixels showing as a grid, no glare, no darker rim round its edge, no halo spilled from the eyes
    for (const gone of ["off", "glare", "bezel", "halo"]) {
        expect(material.uniforms[gone], gone).toBeUndefined();
        expect(SCREEN[gone], gone).toBeUndefined();
        expect(material.fragmentShader, gone).not.toMatch(new RegExp(`uniform \\w+ ${gone};`));
    }
    expect(material.fragmentShader).not.toMatch(/spill|rim/);
});

test("each lit pixel glows in its own colour, brighter than it and brightest at its middle, the only thing on the face", () => {
    const material = visor();
    // a lit pixel is drawn brighter than its colour, brightest at its middle
    expect(material.fragmentShader).toMatch(/mix\(screen, glowing, shown\.a \* pixel\)/);
    expect(material.uniforms.shine.value.toArray()).toEqual([SCREEN.shine.lift, SCREEN.shine.core, SCREEN.shine.tightness]);
    expect(SCREEN.shine.lift).toBeGreaterThan(0);
    expect(SCREEN.shine.core).toBeGreaterThan(0);
    // the pixels change six times a second, like a small real screen
    expect(FRAMES_PER_SECOND).toBe(6);
    // the pixels it glows with are the lit pixels of the screen's texture, one texel each, and only those
    const texture = material.uniforms.pixels.value;
    expect([texture.image.width, texture.image.height]).toEqual([GRID.columns, GRID.rows]);
    const lit = litPixels({eyed: true, eyes: 1, glance: [0, 0], tint: null, hearts: 1.2, stars: 0, squeezed: 0, sign: null});
    showPixels(texture, lit);
    const on = [...Array(GRID.columns * GRID.rows).keys()].filter((index) => texture.image.data[index * 4 + 3]);
    expect(on.length).toBe(lit.length);
    // a new screen is all off: the whole face the glass alone
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
