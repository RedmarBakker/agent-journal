import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import ComicBubble from "../src/chat/ComicBubble.vue";
import {COMIC_BUBBLE, boilAt, bubbleOutline, bubbleRows, bubbleSize} from "../src/figure/comicBubble.js";

// the bubble drawn on the page for the call's `lines` at the figure's frame `frame`, its tail to a handset below its left end
async function drawn(lines, frame) {
    const host = document.createElement("div");
    createApp({render: () => h(ComicBubble, {rows: bubbleRows(lines), left: 100, top: 100, tip: {x: -12, y: 120}, frame})}).mount(host);
    await nextTick();
    return host;
}

const TITLE = "The phone call's speech bubble is a drawn comic bubble that holds its text whole";
const CALL = ["Worker 57", `task 2767: ${TITLE}`];

test("the call's bubble holds a text of 100 characters whole, wrapped over a few rows, and cuts a longer one at its last row", async () => {
    expect(CALL.join("").length).toBe(100);
    const rows = bubbleRows(CALL);
    expect(rows.length).toBeGreaterThan(2);
    expect(rows.length).toBeLessThanOrEqual(COMIC_BUBBLE.rows);
    for (const row of rows) expect(row.text.length).toBeLessThanOrEqual(COMIC_BUBBLE.columns);
    // every word shown, in order, none cut; the first line strong
    expect(rows.map((row) => row.text).join(" ")).toBe(CALL.join(" "));
    expect(rows.filter((row) => row.strong).map((row) => row.text)).toEqual(["Worker 57"]);
    const shown = [...(await drawn(CALL, 0)).querySelectorAll(".comic-bubble-row")].map((row) => row.textContent);
    expect(shown.join(" ")).toBe(CALL.join(" "));
    // a longer text fills every row and ends cut short
    const longer = bubbleRows(["Worker 57", `task 2767: ${TITLE}, and then a good deal more besides`]);
    expect(longer.length).toBe(COMIC_BUBBLE.rows);
    expect(longer.at(-1).text.endsWith("…")).toBe(true);
    expect(longer.at(-1).text.length).toBeLessThanOrEqual(COMIC_BUBBLE.columns);
});

test("the bubble is drawn with an inked outline and a tail to the handset, the outline boiling: redrawn every few frames, one of a few drawings", async () => {
    const host = await drawn(CALL, 0);
    expect(host.querySelectorAll(".comic-bubble-ink path").length).toBe(2);
    expect(host.querySelectorAll(".comic-bubble-fill path").length).toBe(2);
    const outlineAt = async (frame) => [...(await drawn(CALL, frame)).querySelectorAll(".comic-bubble-ink path")].map((path) => path.getAttribute("d"));
    // the same drawing for `every` frames, another after, and the first again after all of them
    expect(await outlineAt(COMIC_BUBBLE.every - 1)).toEqual(await outlineAt(0));
    expect(await outlineAt(COMIC_BUBBLE.every)).not.toEqual(await outlineAt(0));
    expect(await outlineAt(COMIC_BUBBLE.every * COMIC_BUBBLE.drawings)).toEqual(await outlineAt(0));
    expect(new Set(Array.from({length: COMIC_BUBBLE.drawings}, (_, index) => boilAt(index * COMIC_BUBBLE.every))).size).toBe(COMIC_BUBBLE.drawings);
    // each drawing's outline keeps within a wobble of the bubble's box, and its tail ends just short of the handset
    const {width, height} = bubbleSize(bubbleRows(CALL));
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
