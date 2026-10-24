import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import ComicBubble from "../src/chat/ComicBubble.vue";
import {ACTS} from "../src/figure/acts.js";
import {COMIC_BUBBLE, boilAt, bubbleOutline, bubbleSize, phraseAt, phrasesOf, phrasesSeconds} from "../src/figure/comicBubble.js";
import {callSays, callStretch} from "../src/figure/places.js";
import {stretchedFrame} from "../src/figure/timeline.js";

// the bubble drawn on the page for the call's `lines`, `seconds` after it began saying them, at the figure's frame `frame`, its tail to a
// handset below its left end
async function drawn(lines, seconds, frame = 0) {
    const host = document.createElement("div");
    createApp({render: () => h(ComicBubble, {phrases: phrasesOf(lines), seconds, left: 100, top: 100, tip: {x: -12, y: 120}, frame})}).mount(host);
    await nextTick();
    return host;
}

const said = (host) => [...host.querySelectorAll(".comic-bubble-row")].map((row) => row.textContent).join(" ");

const TITLE = "The phone call's speech bubble is a drawn comic bubble that holds its text whole";
const CALL = ["Worker 57", `task 2767: ${TITLE}`];

// how long the bubble is up on a call that says `lines`, in seconds, and the whole call's length, its talk held as the page holds it
function callFor(lines) {
    const act = ACTS.phone_call;
    const stretch = callStretch(phrasesSeconds(phrasesOf(lines)));
    const frames = act.frames + stretch.extra;
    const steps = Math.ceil(frames * 10);
    const up = Array.from({length: steps}, (_, step) => callSays(stretchedFrame(step / 10, stretch) / act.frames)).filter(Boolean).length;
    return {up: up / 10 / act.fps, length: frames / act.fps};
}

test("the bubble says the call a phrase at a time, three or four words or a short sentence, every word in order, each fading in and out", async () => {
    expect(CALL.join("").length).toBe(100);
    const phrases = phrasesOf(CALL);
    expect(phrases[0].rows.map((row) => row.text)).toEqual(["Worker 57"]);
    for (const phrase of phrases.slice(1)) {
        const words = phrase.rows.map((row) => row.text).join(" ").split(" ");
        expect(words.length, words.join(" ")).toBeLessThanOrEqual(COMIC_BUBBLE.words + 1);
        expect(words.length, words.join(" ")).toBeGreaterThanOrEqual(2);
        for (const row of phrase.rows) expect(row.text.length).toBeLessThanOrEqual(COMIC_BUBBLE.columns);
    }
    // a sentence's end closes its phrase
    expect(phrasesOf(["task 2767: The call"]).map((phrase) => phrase.rows.map((row) => row.text).join(" "))).toEqual(["task 2767:", "The call"]);
    // read through, the phrases say every word of the call, in order, none cut
    const shown = [];
    let begun = 0;
    for (const phrase of phrases) {
        const host = await drawn(CALL, begun + phrase.seconds / 2);
        shown.push(said(host));
        // up full in its middle, faded at its ends, the next not yet shown
        expect(Number(host.querySelector(".comic-bubble-words").style.opacity), said(host)).toBe(1);
        if (begun) expect(phraseAt(phrases, begun + 0.01).shows).toBeLessThan(0.1);
        begun += phrase.seconds;
    }
    expect(shown.join(" ")).toBe(CALL.join(" "));
    // the last stays up once said
    expect(said(await drawn(CALL, begun + 5))).toBe(shown.at(-1));
    // one bubble the same size for every phrase, round the largest
    const {width, height} = bubbleSize(phrases);
    expect(width).toBeLessThanOrEqual(COMIC_BUBBLE.columns * COMIC_BUBBLE.glyph + 2 * COMIC_BUBBLE.pad);
    expect(height).toBeLessThanOrEqual(3 * COMIC_BUBBLE.line + 2 * COMIC_BUBBLE.pad);
});

test("the call lasts until its last phrase has been read: its length grows with its text, its bubble up at least the reading time, never under several seconds", () => {
    const texts = [["Worker 57"], ["Worker 57", "task 12: Fix it"], CALL, [...CALL, "and then a good deal more besides, said slowly over the telephone"]];
    const calls = texts.map(callFor);
    for (const [index, text] of texts.entries()) {
        const reading = phrasesSeconds(phrasesOf(text));
        expect(calls[index].up, text.join(" ")).toBeGreaterThanOrEqual(reading);
        expect(calls[index].up, text.join(" ")).toBeGreaterThanOrEqual(3);
    }
    for (let index = 1; index < calls.length; index++) expect(calls[index].length).toBeGreaterThanOrEqual(calls[index - 1].length);
    expect(calls.at(-1).length).toBeGreaterThan(calls[0].length + 5);
    // the 100-character call: about two seconds a phrase
    expect(phrasesSeconds(phrasesOf(CALL))).toBeGreaterThan(8);
    // the talk held longer plays its own frames round again, so the figure goes on talking: the frame after the hold follows on
    const stretch = callStretch(20);
    expect(stretch.extra).toBeGreaterThan(0);
    expect(stretchedFrame(stretch.to + stretch.extra + 1, stretch)).toBeCloseTo(stretch.to + 1, 6);
    for (const index of [stretch.to + 0.5, stretch.to + stretch.extra - 0.5]) {
        const frame = stretchedFrame(index, stretch);
        expect(frame).toBeGreaterThanOrEqual(stretch.from);
        expect(frame).toBeLessThan(stretch.to);
    }
});

test("the bubble's words are written by hand: in the comic hand, each letter a little off the line, askew and sized, never set straight", async () => {
    const host = await drawn(CALL, phrasesOf(CALL)[0].seconds + 1);
    expect(host.querySelector(".comic-bubble").style.fontFamily).toContain("Kalam");
    const letters = [...host.querySelectorAll(".comic-bubble-letter")].map((letter) => letter.style.transform);
    expect(letters.length).toBeGreaterThan(8);
    const lifts = letters.map((transform) => Number(transform.match(/translateY\((-?[\d.]+)px\)/)[1]));
    const tilts = letters.map((transform) => Number(transform.match(/rotate\((-?[\d.]+)deg\)/)[1]));
    expect(new Set(lifts).size).toBeGreaterThan(letters.length / 2);
    expect(new Set(tilts).size).toBeGreaterThan(letters.length / 2);
    for (const lift of lifts) expect(Math.abs(lift)).toBeLessThanOrEqual(COMIC_BUBBLE.lift);
    for (const tilt of tilts) expect(Math.abs(tilt)).toBeLessThanOrEqual(COMIC_BUBBLE.tilt);
    // the same hand each time it is drawn, so the letters never jitter
    expect([...(await drawn(CALL, phrasesOf(CALL)[0].seconds + 1.1)).querySelectorAll(".comic-bubble-letter")].map((letter) => letter.style.transform)).toEqual(letters);
});

test("the bubble is drawn with an inked outline and a tail to the handset, the outline boiling: redrawn every few frames, one of a few drawings", async () => {
    const host = await drawn(CALL, 1);
    expect(host.querySelectorAll(".comic-bubble-ink path").length).toBe(2);
    expect(host.querySelectorAll(".comic-bubble-fill path").length).toBe(2);
    const outlineAt = async (frame) => [...(await drawn(CALL, 1, frame)).querySelectorAll(".comic-bubble-ink path")].map((path) => path.getAttribute("d"));
    // the same drawing for `every` frames, another after, and the first again after all of them
    expect(await outlineAt(COMIC_BUBBLE.every - 1)).toEqual(await outlineAt(0));
    expect(await outlineAt(COMIC_BUBBLE.every)).not.toEqual(await outlineAt(0));
    expect(await outlineAt(COMIC_BUBBLE.every * COMIC_BUBBLE.drawings)).toEqual(await outlineAt(0));
    expect(new Set(Array.from({length: COMIC_BUBBLE.drawings}, (_, index) => boilAt(index * COMIC_BUBBLE.every))).size).toBe(COMIC_BUBBLE.drawings);
    // each drawing's outline keeps within a wobble of the bubble's box, and its tail ends just short of the handset
    const {width, height} = bubbleSize(phrasesOf(CALL));
    for (let drawing = 0; drawing < COMIC_BUBBLE.drawings; drawing++) {
        const {body, tail} = bubbleOutline(width, height, {x: -12, y: 120}, drawing);
        const numbers = body.match(/-?\d+(\.\d+)?/g).map(Number);
        const [xs, ys] = [numbers.filter((_, index) => index % 2 === 0), numbers.filter((_, index) => index % 2 === 1)];
        expect(Math.min(...xs), `${drawing}`).toBeGreaterThan(-2 * COMIC_BUBBLE.wobble);
        expect(Math.max(...xs), `${drawing}`).toBeLessThan(width + 2 * COMIC_BUBBLE.wobble);
        expect(Math.min(...ys), `${drawing}`).toBeGreaterThan(-2 * COMIC_BUBBLE.wobble);
        expect(Math.max(...ys), `${drawing}`).toBeLessThan(height + 2 * COMIC_BUBBLE.wobble);
        const [x, y] = tail.match(/Q\S+ \S+ (\S+) (\S+)/).slice(1).map(Number);
        expect(Math.hypot(x + 12, y - 120), `${drawing}`).toBeLessThan(COMIC_BUBBLE.gap + 2 * COMIC_BUBBLE.wobble);
    }
});
