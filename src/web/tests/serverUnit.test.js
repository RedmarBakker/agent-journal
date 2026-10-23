import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import CodeParcel from "../src/chat/CodeParcel.vue";
import {BLINK, LAYER, LIGHT_COLOURS, phasesOf} from "../src/figure/parcels.js";
import {VISOR} from "../src/figure/visor.js";

test("a unit's lights shine in amber while the run goes and in the visor's own green and red once it ends", () => {
    expect(LIGHT_COLOURS.good).toBe(VISOR.colours.good);
    expect(LIGHT_COLOURS.bad).toBe(VISOR.colours.bad);
    expect(LIGHT_COLOURS.amber).toEqual([1, 0.69, 0.125]);
});

test("a block is drawn from its pictures, one for each step of its lights' blink shown in turn, standing on the floor", async () => {
    for (const lights of ["amber", "good", "bad"]) {
        const pictures = Array.from({length: phasesOf(lights)}, (_, index) => `data:image/png;base64,${index}`);
        const host = document.createElement("div");
        createApp({render: () => h(CodeParcel, {x: 0, y: 0, block: {pictures, width: 27, height: 30, below: 1.5}})}).mount(host);
        await nextTick();
        const box = host.querySelector(".code-parcel-box");
        expect(box.style.width, lights).toBe("27px");
        expect(box.style.height, lights).toBe("30px");
        expect(box.style.bottom, lights).toBe("-1.5px");
        const steps = [...host.querySelectorAll(".code-parcel-step")];
        expect(steps.map((step) => step.getAttribute("src")), lights).toEqual(pictures);
        // amber blinks through its four pictures, a step apart; green and red stay on in one
        expect(steps.every((step) => step.classList.contains("blinks")), lights).toBe(lights === "amber");
        if (lights === "amber") expect(steps.map((step) => step.style.animationDelay)).toEqual([4, 3, 2, 1].map((step) => `${-step * BLINK.ms}ms`));
    }
});

test("the box the figure pushes is drawn over the figure leaning into it, the others behind it, and a box on the pile is marked as the pile's", async () => {
    const drawn = async (props) => {
        const host = document.createElement("div");
        createApp({render: () => h(CodeParcel, {x: 0, y: 0, block: {pictures: ["data:,"], width: 27, height: 30, below: 1}, ...props})}).mount(host);
        await nextTick();
        return host;
    };
    const layer = async (props) => Number((await drawn(props)).querySelector(".code-parcel").style.zIndex);
    expect(await layer({ahead: true})).toBeGreaterThan(LAYER.figure);
    expect(await layer({})).toBeLessThan(LAYER.figure);
    expect((await drawn({piled: true})).querySelector("[data-figure-pile]")).not.toBe(null);
    expect((await drawn({})).querySelector("[data-figure-pile]")).toBe(null);
});
