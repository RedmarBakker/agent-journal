import {createApp, h, nextTick, reactive} from "vue";
import {expect, test} from "vitest";
import PackBox from "../src/chat/act/PackBox.vue";
import VacuumCleaner from "../src/chat/act/VacuumCleaner.vue";
import {ACTS} from "../src/figure/acts.js";

// A rectangle's centre after its SVG transforms. Applying them right to left tests the path actually drawn, including the difference
// between spinning a fragment around itself and accidentally rotating its whole flight path around the burst.
function centreOf(rect) {
    let x = Number(rect.getAttribute("x")) + Number(rect.getAttribute("width")) / 2;
    let y = Number(rect.getAttribute("y")) + Number(rect.getAttribute("height")) / 2;
    const transforms = [...rect.getAttribute("transform").matchAll(/(translate|rotate)\(([^)]*)\)/g)].reverse();
    for (const [, kind, values] of transforms) {
        const [a, b = 0, c = 0] = values.trim().split(/[ ,]+/).map(Number);
        if (kind === "translate") [x, y] = [x + a, y + b];
        else {
            const angle = a * Math.PI / 180;
            [x, y] = [b + (x - b) * Math.cos(angle) - (y - c) * Math.sin(angle), c + (x - b) * Math.sin(angle) + (y - c) * Math.cos(angle)];
        }
    }
    return {x, y};
}

test("the popped box's fragments follow falling arcs while each spins about its own middle", async () => {
    const act = ACTS.pack_box;
    const frames = act.intro + act.hold + act.outro;
    const state = reactive({u: 0});
    const host = document.createElement("div");
    const app = createApp({render: () => h("svg", [h(PackBox, {...state, middle: 56, floor: 108})])});
    app.mount(host);
    try {
        const path = [];
        for (const puff of [0.1, 0.3, 0.5, 0.7, 0.9]) {
            state.u = (act.intro + act.hold + act.outro * (act.pops + 0.4 * puff)) / frames;
            await nextTick();
            const bits = [...host.querySelectorAll("rect[transform]")].map(centreOf);
            expect(bits).toHaveLength(4);
            path.push(bits);
        }
        for (let bit = 0; bit < 4; bit++) {
            const points = path.map((frame) => frame[bit]);
            for (let frame = 2; frame < points.length; frame++) {
                expect(points[frame].x - 2 * points[frame - 1].x + points[frame - 2].x, "horizontal velocity stays steady despite the spin").toBeCloseTo(0);
                expect(points[frame].y - 2 * points[frame - 1].y + points[frame - 2].y, "gravity bends every path down").toBeGreaterThan(0);
            }
            expect(points[1].y).toBeLessThan(points[0].y);
            expect(points.at(-1).y).toBeGreaterThan(points.at(-2).y);
        }
    } finally {
        app.unmount();
    }
});

test("vacuum words disappear into the nozzle before restarting, and the equipment fades at both ends", async () => {
    const act = ACTS.vacuum;
    const frames = act.intro + act.hold + act.outro;
    const state = reactive({u: 0});
    const host = document.createElement("div");
    const app = createApp({render: () => h("svg", [h(VacuumCleaner, {...state, hand: {x: 64, y: 60}, middle: 56, floor: 108, out: 1, size: 112})])});
    app.mount(host);
    try {
        const wordAt = async (frame) => {
            state.u = frame / frames;
            await nextTick();
            const word = host.querySelector("text");
            return {x: Number(word.getAttribute("x")), opacity: Number(word.getAttribute("opacity") ?? 1)};
        };
        const wrap = act.intro + act.hold / 2;
        const before = await wordAt(wrap - 0.0001);
        const after = await wordAt(wrap + 0.0001);
        expect(Math.abs(after.x - before.x), "the next word trip begins at its source").toBeGreaterThan(50);
        expect(before.opacity, "it has vanished into the nozzle before the reset").toBeLessThan(1e-5);
        expect(after.opacity, "it starts invisible at its source").toBeLessThan(1e-5);
        expect((await wordAt(act.intro + act.hold / 4)).opacity).toBe(1);
        for (const frame of [0.01, frames - 0.01]) {
            await wordAt(frame);
            expect(Number(host.querySelector("svg > g").getAttribute("opacity") ?? 1), "no full-opacity equipment pop at an endpoint").toBeLessThan(0.01);
        }
    } finally {
        app.unmount();
    }
});
