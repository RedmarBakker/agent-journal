import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import CodeParcel from "../src/chat/CodeParcel.vue";
import {VISOR} from "../src/figure/visor.js";

test("a unit's lights shine in amber while the run goes and in the visor's own green and red once it ends", async () => {
    const rgb = (colour) => `rgb(${colour.map((part) => Math.round(part * 255)).join(" ")})`;
    for (const [lights, colour] of [["good", rgb(VISOR.colours.good)], ["bad", rgb(VISOR.colours.bad)], ["amber", "#ffb020"]]) {
        const host = document.createElement("div");
        createApp({render: () => h(CodeParcel, {x: 0, y: 0, lights})}).mount(host);
        await nextTick();
        const box = host.querySelector(".code-parcel-box");
        expect(box.getAttribute("style"), lights).toContain(`--light: ${colour}`);
        expect(box.classList.contains(`lights-${lights}`), lights).toBe(true);
        expect(host.querySelectorAll(".code-parcel-light").length).toBe(4);
        expect(host.querySelectorAll(".code-parcel-vent").length).toBeGreaterThan(2);
    }
});
