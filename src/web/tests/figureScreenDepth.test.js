// @vitest-environment node
import * as THREE from "three";
import {expect, test} from "vitest";
import {Stage} from "../src/figure/figure.js";

function screenPass(failOn = 0) {
    const scene = new THREE.Scene();
    const screen = new THREE.MeshBasicMaterial();
    const prop = new THREE.MeshBasicMaterial();
    const hidden = new THREE.MeshBasicMaterial({visible: false, colorWrite: false});
    const hull = new THREE.Mesh(new THREE.PlaneGeometry(), new THREE.MeshBasicMaterial());
    scene.add(new THREE.Mesh(new THREE.PlaneGeometry(), screen), new THREE.Mesh(new THREE.PlaneGeometry(), [prop, hidden]), hull);
    const figure = {scene, screens: [screen], visorHulls: [hull]};
    const calls = [];
    const renderer = {
        autoClear: true,
        domElement: {width: 896, height: 896},
        clear: (...args) => calls.push({clear: args}),
        render: () => {
            const pass = calls.filter((call) => call.draw).length + 1;
            calls.push({draw: pass, screen: screen.colorWrite, prop: prop.colorWrite, hidden: hidden.visible, hull: hull.visible, autoClear: renderer.autoClear});
            if (pass === failOn) throw new Error("render interrupted");
        },
    };
    const target = {width: 224, height: 224, getContext: () => ({drawImage: () => calls.push({composite: true})})};
    const stage = {screenRenderer: renderer, screenCanvas: {}, camera: {}, halvedOnto: () => calls.push({halved: true})};
    return {draw: () => Stage.prototype.drawScreen.call(stage, figure, target), screen, prop, hidden, hull, renderer, calls};
}

test("the visor fills depth before it writes colour, so props drawn later still cover its eyes", () => {
    const pass = screenPass();
    pass.draw();
    expect(pass.calls).toEqual([
        {clear: [true, true, true]},
        {draw: 1, screen: false, prop: false, hidden: false, hull: false, autoClear: false},
        {draw: 2, screen: true, prop: false, hidden: false, hull: false, autoClear: false},
        {halved: true},
        {composite: true},
    ]);
    expect(pass.screen.colorWrite).toBe(true);
    expect(pass.prop.colorWrite).toBe(true);
    expect(pass.hidden.colorWrite).toBe(false);
    expect(pass.hidden.visible).toBe(false);
    expect(pass.hull.visible).toBe(true);
    expect(pass.renderer.autoClear).toBe(true);
});

test.each([1, 2])("an interrupted visor pass %s restores the body, outlines and renderer for the next frame", (failOn) => {
    const pass = screenPass(failOn);
    expect(pass.draw).toThrow("render interrupted");
    expect(pass.screen.colorWrite).toBe(true);
    expect(pass.prop.colorWrite).toBe(true);
    expect(pass.hidden.colorWrite).toBe(false);
    expect(pass.hidden.visible).toBe(false);
    expect(pass.hull.visible).toBe(true);
    expect(pass.renderer.autoClear).toBe(true);
    expect(pass.calls.some((call) => call.composite)).toBe(false);
});
