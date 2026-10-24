import {createApp, h} from "vue";
import {expect, test} from "vitest";
import ChatMark from "../src/kit/ChatMark.vue";

function barBackground(mark) {
    const root = document.createElement("div");
    createApp({render: () => h(ChatMark, {mark})}).mount(root);
    return root.querySelector(".progress").style.background;
}

test("a chat mark's progress bar takes the colour of the mark's tone, and the working colour on a mark with no tone", () => {
    const run = {label: "Running tests", figure: "0 passed, 1 failed", fraction: 1};
    expect(barBackground({...run, tone: "bad"})).toBe("var(--tone-bad)");
    expect(barBackground({...run, tone: "good"})).toBe("var(--tone-good)");
    expect(barBackground({...run, color: "#d4a017"})).toBe("rgb(212, 160, 23)");
    expect(barBackground(run)).toBe("var(--tone-work)");
});

test("a chat mark's progress bar shows while its run is active and is gone once the run has ended", () => {
    const show = (mark) => {
        const root = document.createElement("div");
        createApp({render: () => h(ChatMark, {mark})}).mount(root);
        return root.querySelector(".progress");
    };
    const run = {label: "Running tests", figure: "3 passed", fraction: 0.5};
    expect(show(run)).not.toBeNull();
    expect(show({...run, ending: "finished"})).toBeNull();
    expect(show({...run, ending: "failed", tone: "bad"})).toBeNull();
    expect(show({...run, started: 1, ended: 5, state: "done"})).toBeNull();
});
