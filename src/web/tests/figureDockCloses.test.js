// @vitest-environment node
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {footingOn, groundUnder, readFloors} = await import("../src/figure/floors.js");
const {seatOf} = await import("../src/figure/places.js");
const {GROUNDED, clipFor} = await import("../src/domain/figureState.js");
const {airborneFrame, fallingFrom} = await import("../src/domain/figureMotion.js");

const FIGURE = {size: 112, below: 0.05};
const FRAME_MS = 1000 / 60;
const canDraw = () => true;

// a chat whose compose box has a card docked over it until the test closes it
function chat() {
    let docked = true;
    const bars = boxed({left: 300, right: 700, top: 540, bottom: 600});
    const scroll = {...boxed({left: 200, top: 100, right: 900, bottom: 540}), querySelectorAll: () => []};
    const thread = {
        ...boxed({left: 200, top: 100, right: 900, bottom: 800}),
        querySelector: (selector) => (selector === ".thread-scroll" ? scroll : selector === "[data-figure-docked-bars]" && docked ? bars : null),
    };
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    globalThis.window = {innerWidth: 1280, innerHeight: 800, matchMedia: () => ({matches: false})};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
    return {bars, close: () => (docked = false)};
}

test("a figure sitting on a docked card that closes falls with its seat, lands facing as it sat, and is drawn turned that way after", () => {
    const {bars, close} = chat();
    const seat = seatOf(FIGURE, {x: 700, y: 540});
    expect(seat).toMatchObject({posture: "lounge", on: bars, y: 540});
    const footing = footingOn(seat, readFloors().floors);
    expect(footing.home).toBe(true);
    // the card closes: the ground at home drops from the card to the compose box, and the figure falls from its seat
    close();
    const floors = readFloors().floors;
    expect(groundUnder(footing, seat, FIGURE, floors).motion).toBe("dropping");
    let now = 0;
    let step = {airborne: fallingFrom(seat, null, floors, now, () => 0.9, true), landed: null};
    for (let frame = 0; frame < 300 && !step.landed; frame++) {
        now += FRAME_MS;
        step = airborneFrame(step.airborne, floors, now);
    }
    // it lands on the compose box still seated and turned as it sat, so the clip it plays there is drawn turned a real way, never NaN
    expect(step.landed.spot).toMatchObject({posture: "lounge", y: 600, face: seat.face});
    const place = step.landed.spot;
    const drawn = clipFor({mode: GROUNDED, place, state: "idle", doing: "idle"}, canDraw);
    expect(drawn.facing).toBe(seat.face);
    // and the frames after keep it there, turned the same way
    const kept = footingOn(place, floors);
    for (let frame = 0; frame < 30; frame++) {
        const ground = groundUnder(kept, place, FIGURE, readFloors().floors);
        expect(ground.motion).toBe("carried");
        expect(Number.isFinite(clipFor({mode: GROUNDED, place: {...place, ...ground.spot}, state: "idle", doing: "think"}, canDraw).facing)).toBe(true);
    }
});
