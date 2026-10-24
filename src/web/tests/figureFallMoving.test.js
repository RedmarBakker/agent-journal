// @vitest-environment node
import {describe, expect, it} from "vitest";
import {airborneFrame, fallingFrom} from "../src/domain/figureMotion.js";

const FRAME_MS = 1000 / 60;
// a dock the figure falls onto, its top at `top`, and the window's foot far below it
const dock = (top) => ({id: "floor-7", kind: "dock", left: 100, right: 600, top});
const FOOT = {id: "foot", kind: "foot", left: 0, right: 1200, top: 2000};

// A fall from 100 pixels down the page onto the dock, the dock's top each frame as `topAt(frame)` says, as the chat moves under it:
// the frames of the fall and where it landed
function fallOnto(topAt) {
    let airborne = fallingFrom({x: 300, y: 100, posture: "stand", face: 0}, null, [dock(topAt(0)), FOOT], 0);
    const seen = [];
    for (let frame = 1; frame < 600; frame++) {
        const floors = [dock(topAt(frame)), FOOT];
        const {airborne: next, landed} = airborneFrame(airborne, floors, frame * FRAME_MS);
        if (landed) return {seen, landed, frame, top: topAt(frame)};
        seen.push({y: next.y, top: topAt(frame)});
        airborne = next;
    }
    return {seen, landed: null};
}

describe("a fall onto a floor that moves while the figure falls", () => {
    it("lands exactly on the floor's top where it is now when the chat moves it down during the fall, a new message laid out above", () => {
        const fall = fallOnto((frame) => (frame < 8 ? 400 : 460));
        expect(fall.landed.spot.y, "on the floor's top as it is now").toBe(460);
        expect(fall.landed.spot.on ?? fall.landed.spot, "on that floor").toBeTruthy();
        expect(fall.seen.every(({y, top}) => y <= top), "never below its floor on the way").toBe(true);
        const still = fallOnto(() => 400);
        expect(fall.frame, "met later, as the floor went down").toBeGreaterThan(still.frame);
    });

    it("lands on its top at once when the floor comes up past the falling feet, never falling through it to the foot", () => {
        const fall = fallOnto((frame) => (frame < 12 ? 600 : 140));
        expect(fall.landed.spot.y, "on the floor's top as it is now, not the foot's").toBe(140);
        expect(fall.frame, "the frame the floor came up").toBe(12);
        expect(fall.seen.every(({y, top}) => y <= top)).toBe(true);
    });

    it("lands exactly on the floor's top when the floor keeps moving, down and up, frame by frame", () => {
        for (const topAt of [(frame) => 300 + 6 * frame, (frame) => 520 - 4 * frame, (frame) => 400 + 40 * Math.sin(frame / 3)]) {
            const fall = fallOnto(topAt);
            expect(fall.landed, `${topAt}`).not.toBe(null);
            expect(fall.landed.spot.y, `${topAt}: on the top as it is the frame it lands`).toBe(fall.top);
            expect(fall.seen.every(({y, top}) => y <= top), `${topAt}: never below the floor on the way`).toBe(true);
        }
    });

    it("on a floor that does not move, lands as ever", () => {
        const fall = fallOnto(() => 400);
        expect(fall.landed.spot.y).toBe(400);
    });
});
