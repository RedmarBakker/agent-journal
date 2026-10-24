// @vitest-environment node
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {footingOn, groundUnder, landingOn, readFloors} = await import("../src/figure/floors.js");
const {CHAT_FOOT, DOCKED_BARS} = await import("../src/figure/places.js");
const {airborneFrame, chuteFrom, fallFloors, fallingFrom} = await import("../src/domain/figureMotion.js");

const FIGURE = {size: 112, below: 0.05};
const FRAME_MS = 1000 / 60;
// the compose box at the foot of the chat
const COMPOSE = {left: 300, right: 700, top: 600, bottom: 720};

// A chat whose foot, the docks and the line of what the agent is doing, stays over the bubbles at the bottom of its view, as the sticky foot
// of the thread does, the docks `docks.top` high while any are docked (`docks.top` null for none), and the bubbles `bubbles`, each a box,
// which the test moves; the foot's top is the docks' top, or the compose box's with none docked
function chat(bubbles, docks) {
    const elements = bubbles.map((box) => ({getBoundingClientRect: () => ({width: box.right - box.left, height: box.bottom - box.top, ...box}), checkVisibility: () => true}));
    const bars = {getBoundingClientRect: () => ({left: COMPOSE.left, right: COMPOSE.right, top: docks.top, bottom: COMPOSE.top, width: COMPOSE.right - COMPOSE.left, height: COMPOSE.top - docks.top})};
    const foot = {getBoundingClientRect: () => ({left: 200, right: 900, top: docks.top ?? COMPOSE.top - 24, bottom: COMPOSE.top})};
    const scroll = {...boxed({left: 200, top: 100, right: 900, bottom: COMPOSE.top}), querySelectorAll: () => elements, querySelector: (selector) => (selector === CHAT_FOOT ? foot : null)};
    const thread = {
        ...boxed({left: 200, top: 100, right: 900, bottom: 800}),
        querySelector: (selector) => (selector === ".thread-scroll" ? scroll : selector === DOCKED_BARS && docks.top !== null ? bars : null),
    };
    const home = {...boxed(COMPOSE), closest: () => thread};
    globalThis.window = {innerWidth: 1280, innerHeight: 800, matchMedia: () => ({matches: false})};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
    return elements;
}

// the frames of a fall from `airborne` over the floors `floorsAt(frame)` reads, until it lands
function fallen(airborne, floorsAt) {
    let step = {airborne, landed: null};
    const path = [];
    for (let frame = 1; frame < 400 && !step.landed; frame++) {
        step = airborneFrame(step.airborne, floorsAt(frame), airborne.at + frame * FRAME_MS);
        path.push(step.airborne?.y ?? step.landed.spot.y);
    }
    return {...step, path};
}

const bubble = (top, id = `bubble-${top}`) => ({id, kind: "bubble", left: 200, right: 900, top, bottom: top + 60, vy: 0});
const floor = (id, kind, top) => ({id, kind, left: 200, right: 900, top, vy: 0});

test("a figure whose dock goes away falls past every chat bubble under it and lands on the next dock or the composer, as does its parachute", () => {
    const bubbles = [bubble(260), bubble(330), bubble(410), bubble(470)];
    // from a high dock: past all four bubbles onto the next dock down, or with none onto the compose box
    const lower = fallen(fallingFrom({x: 500, y: 200, posture: "stand", face: 0}, null, [], 0), () => [...bubbles, floor("floor-9", "dock", 520), floor("foot", "foot", 800)]);
    expect(lower.landed.spot).toMatchObject({y: 520});
    const composer = fallen(fallingFrom({x: 500, y: 200, posture: "stand", face: 0}, null, [], 0), () => [...bubbles, floor("home", "compose", 600), floor("foot", "foot", 800)]);
    expect(composer.landed.spot).toMatchObject({y: 600});
    expect(composer.path.some((y) => y > 470 && y < 600), "it passed the lowest bubble").toBe(true);
    // a parachute comes down past them alike
    const chute = fallen(chuteFrom(500, -30, 300, 0), () => [...bubbles, floor("home", "compose", 600), floor("foot", "foot", 800)]);
    expect(chute.landed.spot.y).toBe(600);
    expect(fallFloors([...bubbles, floor("home", "dock", 540)]).map((each) => each.kind)).toEqual(["dock"]);
    // on the page: seated on a docked card with a bubble under it, the card closes and it drops past the bubble to the compose box
    const docks = {top: 540};
    chat([{left: 250, right: 850, top: 560, bottom: 590}], docks);
    const seat = {x: 500, y: 540, posture: "stand", face: 0, on: readFloors().floors.find((each) => each.id === "home").element};
    const footing = footingOn(seat, readFloors().floors);
    docks.top = null;
    const floors = readFloors().floors;
    expect(floors.some((each) => each.kind === "bubble" && each.top === 560), "the bubble is shown once the docks go").toBe(true);
    expect(groundUnder(footing, seat, FIGURE, floors).motion).toBe("dropping");
    expect(fallen(fallingFrom(seat, null, floors, 0), () => readFloors().floors).landed.spot.y).toBe(COMPOSE.top);
});

test("a figure that chose to jump onto a chat bubble still lands on it, where the bubble is now", () => {
    const box = {left: 250, right: 850, top: 380, bottom: 440};
    chat([box], {top: 540});
    const floors = readFloors().floors;
    const shown = floors.find((each) => each.kind === "bubble");
    expect(shown.top).toBe(380);
    const spot = {x: 500, y: 380, posture: "stand", face: 0, on: shown.element};
    const footing = footingOn(spot, floors);
    // the chat scrolls the bubble a little as the jump goes: the jump lands on its top where it is then
    box.top = 372;
    box.bottom = 432;
    expect(landingOn(spot, footing, FIGURE, readFloors().floors)).toMatchObject({x: 500, y: 372});
});

test("over docks folding and unfolding beside the chat's bubbles, the figure's feet are always on the top edge of what it stands on, never inside it", () => {
    // a bubble near the foot of the chat, its top at 520, the figure standing on it, and docks that unfold up over it and fold away again
    const docks = {top: null};
    const box = {left: 250, right: 850, top: 520, bottom: 580};
    chat([box], docks);
    const shown = readFloors().floors.find((each) => each.kind === "bubble");
    let spot = {x: 500, y: 520, posture: "stand", face: 0, on: shown.element};
    let footing = footingOn(spot, readFloors().floors);
    let airborne = null;
    // the docks rise from the compose box up past the bubble's top to 470, stay, then fold down again and go
    const docksAt = (frame) => (frame < 10 ? null : frame < 40 ? COMPOSE.top - (frame - 9) * 4.4 : frame < 80 ? 468 : frame < 110 ? 468 + (frame - 79) * 4.4 : null);
    const surfaces = [];
    for (let frame = 0; frame < 160; frame++) {
        docks.top = docksAt(frame);
        const floors = readFloors().floors;
        if (airborne) {
            const step = airborneFrame(airborne, floors, frame * FRAME_MS);
            airborne = step.airborne;
            if (step.landed) {
                spot = step.landed.spot;
                footing = footingOn(spot, floors);
            }
        } else {
            const ground = groundUnder(footing, spot, FIGURE, floors);
            if (!ground || ground.motion === "dropping") airborne = fallingFrom(spot, null, floors, frame * FRAME_MS);
            else ({spot, footing} = {spot: ground.spot, footing: ground.footing});
        }
        if (airborne) continue;
        // standing, its feet are on the top of a floor there is, and inside none of the boxes about it: the docks, the compose box, the bubble
        const label = `frame ${frame}, docks at ${docks.top}`;
        expect(floors.some((each) => Math.abs(each.top - spot.y) < 0.5 && each.left <= spot.x && spot.x <= each.right), `${label} on a top edge`).toBe(true);
        const boxes = [COMPOSE, ...(docks.top === null ? [] : [{top: docks.top, bottom: COMPOSE.top}])];
        for (const each of boxes) expect(spot.y > each.top + 0.5 && spot.y < each.bottom, `${label} inside the docks or the compose box`).toBe(false);
        // a bubble's top behind the docks is no floor to stand on
        if (docks.top !== null && box.top > docks.top) expect(Math.abs(spot.y - box.top) < 0.5, `${label} on a bubble hidden behind the docks`).toBe(false);
        surfaces.push(spot.y);
    }
    // it stood on the bubble, then the docks once they rose over it, and the compose box once they went
    expect(surfaces[0]).toBe(520);
    expect(surfaces).toContain(468);
    expect(surfaces.at(-1)).toBe(COMPOSE.top);
});
