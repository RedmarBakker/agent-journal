// @vitest-environment node
import {readFileSync, readdirSync} from "node:fs";
import {expect, test} from "vitest";
import {processEndsAfter, withSystemCards} from "../src/domain/figureState.js";
import {VISOR, visorAt, visorFor} from "../src/figure/visor.js";
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
        expect(visorAt(lit, 100, false)).toBe(null);
        expect(visorAt(lit, 101, false)).toEqual({colour, amount: 1});
        expect(visorAt(lit, 100 + VISOR.seconds - 0.1, false).amount).toBeGreaterThan(0);
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
