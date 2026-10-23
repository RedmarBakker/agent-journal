import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import FigureAct from "../src/chat/FigureAct.vue";
import {ACTS} from "../src/figure/acts.js";

// the act drawn over the figure's picture at `u` of the way through the hand rub, its hands at the picture's middle, a little low
async function drawn(u) {
    const host = document.createElement("div");
    createApp({render: () => h(FigureAct, {name: "hand_rub", u, hand: {x: 0.5, y: 0.56, out: 1}, head: {x: 0.5, y: 0.25}, feet: 0.95, size: 112, room: {left: 200, right: 200}})}).mount(host);
    await nextTick();
    return host;
}

test("a small cloud of puffs and sparkles rises from the rubbing hands while they rub, and none before or after", async () => {
    const {puff} = ACTS.hand_rub;
    const rubbing = await drawn((puff[0] + puff[1]) / 2);
    const cloud = rubbing.querySelector(".figure-act-rub");
    expect(cloud).not.toBe(null);
    // at the hands, 0.5 and 0.56 of the 112-pixel picture
    expect(cloud.getAttribute("transform")).toBe(`translate(${0.5 * 112} ${0.56 * 112})`);
    expect(cloud.querySelectorAll("circle").length).toBeGreaterThanOrEqual(4);
    expect(cloud.querySelectorAll("path").length).toBeGreaterThanOrEqual(2);
    // every puff rises above the hands
    for (const circle of cloud.querySelectorAll("circle")) expect(Number(circle.getAttribute("cy"))).toBeLessThan(0);
    for (const u of [puff[0] / 2, (puff[1] + 1) / 2]) expect((await drawn(u)).querySelector(".figure-act-rub"), `${u}`).toBe(null);
});
