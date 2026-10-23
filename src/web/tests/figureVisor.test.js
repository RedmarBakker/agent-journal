// @vitest-environment node
import {readFileSync, readdirSync} from "node:fs";
import {expect, test} from "vitest";
import {processEndsAfter, withSystemCards} from "../src/domain/figureState.js";
import {VISOR, crtAt, visorAt, visorFor} from "../src/figure/visor.js";
import {SCREEN} from "../src/figure/figure.js";

const at = (seconds) => new Date(seconds * 1000).toISOString();
// a process card as features/shell writes a watched output's: running, then ended with the tone of how it ended
const card = (id, active, tone) => ({table: "messages", id, author: "system", session: null, text: "Running tests", created_at: at(10), data: {card_type: "process", process: "output", icon: "terminal", active, tone, ending: active ? "" : "finished"}});
const ends = (known, ...messages) => processEndsAfter(withSystemCards({session: "s", data: {}}, messages), known);

test("a process card that ends bad lights the visor red for about two seconds and one that ends good lights it green, and then the eyes are back", () => {
    for (const [tone, colour] of [["bad", VISOR.colours.bad], ["good", VISOR.colours.good]]) {
        const known = new Map();
        expect(ends(known, card(1, true, ""))).toEqual([]);
        const ended = ends(known, card(1, false, tone));
        expect(ended).toEqual([{tone, time: 10, card: "messages:1"}]);
        // seen once, an end is not lit again
        expect(ends(known, card(1, false, tone))).toEqual([]);
        const lit = visorFor(ended, null, 100);
        expect(lit).toEqual({tone, at: 100});
        expect(visorAt(lit, 101, false)).toEqual({colour, eyes: 0, across: 1, open: 1, flash: 0, glow: 1});
        expect(visorAt(lit, 100 + VISOR.seconds - 0.05, false).eyes).toBeGreaterThan(0);
        expect(visorAt(lit, 100 + VISOR.seconds, false)).toBe(null);
    }
    expect(VISOR.seconds).toBeGreaterThanOrEqual(1.5);
    expect(VISOR.seconds).toBeLessThanOrEqual(2.5);
    // red is red and green is green
    const [r, g] = VISOR.colours.bad;
    const [r2, g2] = VISOR.colours.good;
    expect([r > 2 * g, g2 > 2 * r2]).toEqual([true, true]);
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

test("every voice wears the visor that lights, and its pixels are big enough to see at the chat's 112-pixel figure", () => {
    const figures = new URL("../public/voices/figures/", import.meta.url);
    const glbs = readdirSync(figures).filter((file) => file.endsWith(".glb"));
    expect(glbs.map((file) => file.split(".")[0]).sort()).toEqual(["butler", "coach", "colleague", "homie", "squire"]);
    for (const file of glbs) {
        const bytes = readFileSync(new URL(file, figures));
        const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
        expect(json.nodes.filter((node) => "mesh" in node).map((node) => node.name), file).toContain("face_screen");
    }
    // the picture is 5.4 of the figure's units high; at 112 pixels a pixel of the visor is two of the page's, its gap a half
    const pagePixels = (SCREEN.pitch * 112) / 5.4;
    expect(pagePixels).toBeGreaterThanOrEqual(1.8);
    expect(pagePixels * SCREEN.gap).toBeGreaterThanOrEqual(0.4);
});

test("the visor comes on as an old CRT powers up: the eyes go out first, a bright line comes on across the middle and widens, it opens out to fill the visor, the white flash turns to the colour, and the eyes come back", () => {
    const at = (seconds) => crtAt(seconds);
    // the eyes go out before anything lights
    expect(at(0)).toEqual({eyes: 1, across: 0, open: VISOR.thin, flash: 1, glow: 0});
    expect(at(VISOR.eyesOut).eyes).toBe(0);
    expect(at(VISOR.eyesOut / 2).across).toBe(0);
    // a thin bright line across the middle, widening out from its centre
    const line = at((VISOR.line[0] + VISOR.line[1]) / 2);
    expect(line.across).toBeGreaterThan(0.2);
    expect(line.across).toBeLessThan(0.8);
    expect(line.open).toBe(VISOR.thin);
    expect(line.flash).toBe(1);
    // the line opens out top and bottom to fill the visor, the white going to the colour
    const opening = at((VISOR.open[0] + VISOR.open[1]) / 2);
    expect([opening.across, opening.open > VISOR.thin, opening.open < 1, opening.flash < 1, opening.flash > 0]).toEqual([1, true, true, true, true]);
    expect(at(VISOR.flash[1])).toMatchObject({across: 1, open: 1, flash: 0, glow: 1, eyes: 0});
    // the glow fades and then the eyes come back, and the visor is the eyes' again
    const off = VISOR.seconds - VISOR.eyesBack;
    expect(at(off - VISOR.fade / 2).glow).toBeGreaterThan(0);
    expect(at(off).glow).toBe(0);
    expect(at(VISOR.seconds - 0.01).eyes).toBeGreaterThan(0.8);
    expect(at(VISOR.seconds)).toBe(null);
    // in step order the eyes go out, then the band widens, then it opens
    let last = at(0);
    for (let seconds = 0.01; seconds < VISOR.flash[1]; seconds += 0.01) {
        const now = at(seconds);
        expect(now.across, `${seconds}`).toBeGreaterThanOrEqual(last.across);
        expect(now.open, `${seconds}`).toBeGreaterThanOrEqual(last.open);
        if (now.across > 0) expect(now.eyes, `${seconds}`).toBe(0);
        if (now.open > VISOR.thin) expect(now.across, `${seconds}`).toBe(1);
        last = now;
    }
});

test("the visor's red and green are its own, a glowing screen's: vivid and pure, with a brighter core and a soft halo", () => {
    const [r, g, b] = VISOR.colours.bad;
    const [r2, g2, b2] = VISOR.colours.good;
    expect([r >= 0.95, g <= 0.12, b <= 0.15]).toEqual([true, true, true]);
    expect([g2 >= 0.95, r2 <= 0.12, b2 <= 0.4]).toEqual([true, true, true]);
    expect(VISOR.core).toBeGreaterThan(0.2);
    expect(VISOR.halo).toBeGreaterThan(0.3);
});
