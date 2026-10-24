// @vitest-environment node
import {readFileSync, readdirSync} from "node:fs";
import {expect, test} from "vitest";
import {processEndsAfter, withSystemCards} from "../src/domain/figureState.js";
import {SIGN, VISOR, lightOnce, visorAt, visorFor} from "../src/figure/visor.js";
import {signColour} from "../src/figure/figure.js";
import {GRID, litPixels} from "../src/figure/visorPixels.js";

const at = (seconds) => new Date(seconds * 1000).toISOString();
// a process card as features/shell writes a watched output's: running, then ended with the tone of how it ended
const card = (id, active, tone) => ({table: "messages", id, author: "system", session: null, text: "Running tests", created_at: at(10), data: {card_type: "process", process: "output", icon: "terminal", active, tone, ending: active ? "" : "finished"}});
const ends = (known, ...messages) => processEndsAfter(withSystemCards({session: "s", data: {}}, messages), known);

test("a run that ends bad shows the red crosses on the pixel screen and one that ends good the green ticks, the visor itself never lit, and then the eyes are back", () => {
    for (const [tone, name] of [["bad", "cross"], ["good", "tick"]]) {
        const known = new Map();
        expect(ends(known, card(1, true, ""))).toEqual([]);
        const ended = ends(known, card(1, false, tone));
        expect(ended).toEqual([{tone, time: 10, card: "messages:1"}]);
        // seen once, an end is not shown again
        expect(ends(known, card(1, false, tone))).toEqual([]);
        const waiting = visorFor(ended, null, 100);
        expect(waiting).toEqual({tone, at: null, since: 100, card: "messages:1"});
        // dark while the head turns to the run's mark (figureLookFirst.test.js), shown once it has faced it VISOR.looks seconds
        expect(visorAt(waiting, 100.5, false)).toBe(null);
        expect(lightOnce(waiting, true, 99.5).at, "facing it, not yet a second").toBe(null);
        const lit = lightOnce(lightOnce(waiting, true, 100 - VISOR.looks), true, 100);
        expect(lit.at).toBe(100);
        // all the while: the sign of its tone in the eyes, the visor's band never lit, no flash, no glow
        for (let seconds = 0; seconds < SIGN.seconds - 0.01; seconds += 0.05) {
            const shown = visorAt(lit, 100 + seconds, false);
            expect(shown.sign.name, `${tone} ${seconds}`).toBe(name);
            expect([shown.across, shown.open, shown.flash, shown.glow], `${tone} ${seconds}`).toEqual([0, 0, 0, 0]);
        }
        expect(visorAt(lit, 100 + SIGN.seconds, false)).toBe(null);
    }
    // red is red and green is green
    const [r, g] = VISOR.colours.bad;
    const [r2, g2] = VISOR.colours.good;
    expect([r > 2 * g, g2 > 2 * r2]).toEqual([true, true]);
});

test("the crosses and the ticks are the pixel pictures on the visor's screen in the run's colour, every other pixel of the visor left as it was", () => {
    const face = (sign) => ({eyed: true, eyes: 1, shift: [0, 0], tint: null, hearts: 0, stars: 0, squeezed: 0, sign});
    const names = (pixels) => pixels.map(({column, row}) => `${column},${row}`).sort();
    for (const [tone, name] of [["bad", "cross"], ["good", "tick"]]) {
        const lit = {tone, at: 0, card: "messages:1"};
        for (const seconds of [SIGN.flash[1], (SIGN.flash[1] + SIGN.fade[0]) / 2]) {
            const screen = visorAt(lit, seconds, false);
            const pixels = litPixels(face({name: screen.sign.name, strength: screen.sign.strength, colour: signColour(screen)}));
            expect(names(pixels), `${tone} ${seconds}`).toEqual(names(litPixels(face({name, strength: 1, colour: [1, 1, 1]}))));
            for (const {colour} of pixels) expect(colour.map((part) => part.toFixed(3)), `${tone} ${seconds}`).toEqual(VISOR.colours[tone].map((part) => part.toFixed(3)));
            // only the picture's pixels are lit: the rest of the grid stays off, the visor's own dark screen
            expect(pixels.length).toBeLessThan((GRID.columns * GRID.rows) / 4);
        }
    }
});

test("only a card seen running and then ending lights the visor: one first seen already ended, or one ending with no tone, does not", () => {
    const known = new Map();
    expect(ends(known, card(2, false, "good"))).toEqual([]);
    ends(known, card(3, true, ""));
    expect(ends(known, card(3, false, ""))).toEqual([]);
    expect(visorFor([], null, 5)).toBe(null);
});

test("the visor never lights while the figure sleeps, and goes back to its eyes if it falls asleep while lit", () => {
    const lit = {tone: "bad", at: 100};
    expect(visorAt(lit, 101, true)).toBe(null);
    expect(visorAt(lit, 101, false)).not.toBe(null);
});

test("every voice wears the visor that lights", () => {
    const figures = new URL("../public/voices/figures/", import.meta.url);
    const glbs = readdirSync(figures).filter((file) => file.endsWith(".glb"));
    expect(glbs.map((file) => file.split(".")[0]).sort()).toEqual(["butler", "coach", "colleague", "homie", "squire"]);
    for (const file of glbs) {
        const bytes = readFileSync(new URL(file, figures));
        const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
        expect(json.nodes.filter((node) => "mesh" in node).map((node) => node.name), file).toContain("face_screen");
    }
});

test("the visor's red and green are its own, a glowing screen's: vivid and pure; a dance's screen with a brighter core and a soft halo", () => {
    const [r, g, b] = VISOR.colours.bad;
    const [r2, g2, b2] = VISOR.colours.good;
    expect([r >= 0.95, g <= 0.12, b <= 0.15]).toEqual([true, true, true]);
    expect([g2 >= 0.95, r2 <= 0.12, b2 <= 0.4]).toEqual([true, true, true]);
    expect(VISOR.core).toBeGreaterThan(0.2);
    expect(VISOR.halo).toBeGreaterThan(0.3);
});
