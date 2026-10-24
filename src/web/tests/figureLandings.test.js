// @vitest-environment node
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {GRAB, thrownFrame, thrownFrom} = await import("../src/figure/grab.js");
const {POSTURES, boxAt, clickedBody, restOf, spotOf} = await import("../src/figure/places.js");
const {airborneFrame, chuteFrom} = await import("../src/domain/figureMotion.js");
const {SKYWARD} = await import("../src/figure/skyward.js");

const FIGURE = {size: 112, below: 0.05};
// the chat's floor, the compose box's top at 700 under the chat's whole width, and a bubble above it
const HOME = {id: "home", kind: "compose", left: 256, right: 944, top: 700, element: "home"};
const BUBBLE = {id: "bubble", kind: "bubble", left: 300, right: 700, top: 400, bottom: 460, element: "bubble"};
const FLOORS = [HOME, BUBBLE];
const ROOM = {left: 256, right: 944, top: 100};

// the page the figure lives on: the compose box from 300 to 700 across at 600, in a chat `high` pixels high from 100 down
function chat(high) {
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    const thread = {...boxed({left: 200, top: 100, right: 1000, bottom: 100 + high}), querySelector: () => null};
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
}

// a place as the page settles the figure on it (VoiceFigure.vue settle): its posture known, its picture's box and the part of it that
// takes a click drawn from it (places.js boxAt, clickedBody)
function settles(place, label) {
    expect(POSTURES[place.posture], `${label} posture`).toBeDefined();
    expect(Number.isFinite(boxAt(place, FIGURE).top), `${label} box`).toBe(true);
    expect(Number.isFinite(clickedBody(place.posture, FIGURE.below).bottom), `${label} click`).toBe(true);
}

// lifted at its feet and let go at `speed` (VoiceFigure.vue lift, released), flown at 60 frames a second until it lands, or, gone off the
// top, back down from above on its parachute (goneOff, flyOn): the place it comes to rest on
function landing(feet, speed) {
    const held = {...feet, posture: "stand", face: 0, held: true};
    let thrown = thrownFrom(held, speed, 0);
    for (let frame = 1; frame < 60 * 30; frame++) {
        const next = thrownFrame(thrown, FLOORS, ROOM, (frame * 1000) / 60);
        if (next.landed) return next.landed;
        if (next.gone) return comeBack(next.airborne.x);
        thrown = next.airborne;
    }
    throw new Error("never landed");
}

function comeBack(x) {
    let back = chuteFrom(x, ROOM.top - FIGURE.size / 4, SKYWARD.chute * FIGURE.size, 0);
    for (let frame = 1; frame < 60 * 30; frame++) {
        const next = airborneFrame(back, FLOORS, (frame * 1000) / 60);
        if (next.landed) return next.landed.spot;
        back = next.airborne;
    }
    throw new Error("never came back");
}

test("lifted, thrown and dropped, the figure lands on a place with its posture every time, and the place at home it goes on to has one too", () => {
    const releases = [
        ["dropped over the bubble", {x: 500, y: 300}, {x: 0, y: 0}],
        ["dropped past the bubble", {x: 800, y: 300}, {x: 0, y: 0}],
        ["thrown across", {x: 500, y: 300}, {x: 1500, y: -400}],
        ["thrown down", {x: 600, y: 200}, {x: -300, y: 900}],
        ["thrown off the top", {x: 500, y: 300}, {x: 200, y: -GRAB.fastest}],
    ];
    for (const high of [700, 60]) {
        chat(high);
        for (const [name, feet, speed] of releases) {
            const label = `${name}, the chat ${high} high`;
            const landed = landing(feet, speed);
            settles(landed, label);
            // where it may go on to rest at home from there, even while the chat is laid out smaller than the figure
            settles(restOf(FIGURE, landed), `${label}, resting at home`);
            settles(spotOf(null, FIGURE, landed), `${label}, strolling at home`);
        }
    }
});
