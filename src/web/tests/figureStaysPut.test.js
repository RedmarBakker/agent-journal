// @vitest-environment node
import {beforeEach, expect, test} from "vitest";

const {CLIPS} = await import("../src/figure/figure.js");
const {AGENT_TURN, ASIDE_STEP, agentWordsAt, asideOf, boxAt} = await import("../src/figure/places.js");
const {SEAT_STAY, mayLeave, playsSeated, seatStay} = await import("../src/figure/perches.js");
const {seeded} = await import("./support/seeded.js");
const {write} = await import("./figurePage.js");

const FIGURE = {size: 112, below: 0.05};
// the figure standing on the compose box's top edge, which runs from 200 to 1000 across the page
const STANDING = {x: 600, y: 600, face: 0, posture: "stand"};
const EDGE = {left: 200, right: 1000};

beforeEach(() => {
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.document = {querySelector: () => null, querySelectorAll: () => []};
});

// a message's words laid over the figure's body where it stands, inside the turn `within` names
const over = (within) => {
    const body = boxAt(STANDING, FIGURE);
    return {left: STANDING.x - 25, right: STANDING.x + 25, top: body.top + 20, bottom: STANDING.y - 10, within};
};

test("a message the user sends never moves the figure, whatever it covers: neither its words nor the buttons on its bubble count", () => {
    const words = over(".thread-turn.mine");
    write([words], [{box: words, shown: true}]);
    // what VoiceFigure steps aside for: an agent's words under its body that were not there when it came to rest
    expect(agentWordsAt(STANDING, FIGURE)).toBe(0);
    // the same words in an agent's message are ones it steps aside from
    write([over(AGENT_TURN)]);
    expect(agentWordsAt(STANDING, FIGURE)).toBeGreaterThan(0);
});

test("an agent's message over the figure sends it aside by the least needed: the nearest place along its edge that covers none of the words", () => {
    const words = over(AGENT_TURN);
    write([words]);
    const aside = asideOf(FIGURE, STANDING, EDGE);
    expect(aside).toMatchObject({y: STANDING.y, posture: "stand"});
    expect(agentWordsAt(aside, FIGURE)).toBe(0);
    const moved = Math.abs(aside.x - STANDING.x);
    // a step less, either way, still covers the words: none nearer is clear
    for (const x of [STANDING.x - (moved - ASIDE_STEP), STANDING.x + (moved - ASIDE_STEP)]) expect(agentWordsAt({...STANDING, x}, FIGURE), `${x}`).toBeGreaterThan(0);
    // far less than the corner of the edge it used to go to, under a figure's width
    expect(moved).toBeLessThan(FIGURE.size);
    // with words along the whole edge there is nowhere to step to along it
    write([{...words, left: EDGE.left, right: EDGE.right}]);
    expect(asideOf(FIGURE, STANDING, EDGE)).toBe(null);
});

test("seated, the figure keeps its seat at least half a minute, longer by roll, and no act or trip but an urgent one stands it up before, over many rolls", () => {
    const random = seeded(2888);
    const standing = CLIPS.filter((clip) => !clip.postures.includes("sit"));
    const seated = CLIPS.filter((clip) => clip.postures.includes("sit"));
    expect(standing.length).toBeGreaterThan(5);
    expect(SEAT_STAY.least).toBeGreaterThanOrEqual(30);
    const stays = [];
    for (let roll = 0; roll < 200; roll++) {
        const now = 1000 + roll;
        const perched = seatStay(null, true, false, now, random);
        stays.push(perched.until - now);
        for (const later of [now + 0.5, now + 1, now + 10, now + SEAT_STAY.least - 0.01]) {
            expect(mayLeave(perched, later, false), `${roll} ${later - now}`).toBe(false);
            expect(mayLeave(perched, later, true), "an urgent trip may").toBe(true);
            for (const clip of standing) expect(playsSeated(clip, "sit", perched, later), `${clip.name} at ${later - now}`).toBe(false);
            for (const clip of seated) expect(playsSeated(clip, "sit", perched, later), clip.name).toBe(true);
        }
        // kept while it stays seated, over once it is
        expect(seatStay(perched, true, true, now + 5, random)).toBe(perched);
        expect(mayLeave(perched, perched.until, false)).toBe(true);
        expect(playsSeated(standing[0], "sit", perched, perched.until)).toBe(true);
        expect(seatStay(perched, false, true, perched.until, random), "standing up, the seat is given up").toBe(null);
    }
    expect(Math.min(...stays)).toBeGreaterThanOrEqual(SEAT_STAY.least);
    expect(Math.max(...stays), "longer by roll").toBeGreaterThan(SEAT_STAY.least + SEAT_STAY.more / 2);
    expect(Math.max(...stays)).toBeLessThanOrEqual(SEAT_STAY.least + SEAT_STAY.more);
    // a stay on a bubble it climbed onto standing is kept as it was while it stands there
    const climbed = {until: 2000};
    expect(seatStay(climbed, false, false, 1990, random)).toBe(climbed);
});
