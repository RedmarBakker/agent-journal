// @vitest-environment node
import {expect, test} from "vitest";
import {boxed} from "./support/figurePage.js";

const {clearOfPile, pileBox, restOf, seatOf, spotOf} = await import("../src/figure/places.js");
const {PARCEL, PILED, pileSlot} = await import("../src/figure/parcels.js");

const FIGURE = {size: 112, below: 0.05};

// a chat whose compose box has `count` boxes piled at its right corner, as chat/CodeParcel.vue marks them
function chat(count) {
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    const thread = {...boxed({left: 200, top: 100, right: 900, bottom: 800}), querySelector: () => null};
    const piled = Array.from({length: count}, (_, index) => {
        const slot = pileSlot(index);
        const middle = 700 + slot.left;
        return boxed({left: middle - PARCEL.width / 2, right: middle + PARCEL.width / 2, top: 600 - slot.up - PARCEL.height, bottom: 601 - slot.up});
    });
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {
        querySelector: (selector) => (selector === "[data-figure-home]" ? home : null),
        querySelectorAll: (selector) => (selector === PILED ? piled : []),
    };
}

test("with boxes piled at the composer's right corner, the figure never rests, sits or strolls in front of the pile, but beside it", () => {
    for (const count of [1, 3, 5]) {
        chat(count);
        const pile = pileBox();
        expect(pile.right, String(count)).toBeLessThanOrEqual(700);
        // from either end, and walking along the edge from end to end, every spot keeps clear of the pile
        const spots = [];
        for (const x of [320, 500, 690]) {
            spots.push(restOf(FIGURE, {x, y: 600}), seatOf(FIGURE, {x, y: 600}));
            for (const along of [0, 0.25, 0.5, 0.75, 1]) spots.push(spotOf(null, FIGURE, {x: 300 + 400 * along, y: 0}));
        }
        for (const spot of spots.filter(Boolean)) expect(clearOfPile(spot, FIGURE), `${count}: ${spot.posture} at ${spot.x}`).toBe(true);
        // the corner nearest the pile is the free part's, beside it
        const right = restOf(FIGURE, {x: 690, y: 600});
        expect(right.x).toBeLessThan(pile.left);
        expect(right.x).toBeGreaterThan(pile.left - FIGURE.size * 0.6);
    }
    // with no pile, the corner is the composer's own
    chat(0);
    expect(pileBox()).toBe(null);
    expect(restOf(FIGURE, {x: 690, y: 600}).x).toBeGreaterThan(650);
});
