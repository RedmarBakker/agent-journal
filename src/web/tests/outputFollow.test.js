import {createApp, h, ref} from "vue";
import {afterEach, describe, expect, test} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {default: OutputLines} = await import("../src/kit/OutputLines.vue");

let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

// jsdom lays nothing out, so the box's heights are given by hand: 100 lines of 10px in a box 200px tall
function sized(box, lines) {
    Object.defineProperty(box, "clientHeight", {configurable: true, value: 200});
    Object.defineProperty(box, "scrollHeight", {configurable: true, get: () => lines.value.length * 10});
}

describe("an output opened to read its terminal lines", () => {
    test("follows its newest line, stops following when scrolled up by hand, and follows again from the button", async () => {
        const lines = ref(Array.from({length: 100}, (_, n) => `line ${n}`));
        const root = document.createElement("div");
        document.body.appendChild(root);
        app = createApp({render: () => h(OutputLines, {lines: lines.value})});
        app.mount(root);
        const box = root.querySelector("pre");
        sized(box, lines);
        lines.value = [...lines.value, "line 100"];
        await flush();
        expect(box.scrollTop).toBe(box.scrollHeight - 0, "following, a new line takes the box to its end");
        expect(root.querySelector(".output-follow")).toBe(null);

        box.scrollTop = 300;
        box.dispatchEvent(new Event("scroll"));
        await flush();
        lines.value = [...lines.value, "line 101"];
        await flush();
        expect(box.scrollTop).toBe(300, "scrolled up by hand, the reader stays where they read");
        const follow = root.querySelector(".output-follow");
        expect(follow?.textContent).toBe("Follow");

        follow.click();
        await flush();
        expect(box.scrollTop).toBe(box.scrollHeight, "the button goes to the end");
        expect(root.querySelector(".output-follow")).toBe(null);
        lines.value = [...lines.value, "line 102"];
        await flush();
        expect(box.scrollTop).toBe(box.scrollHeight, "and new lines are followed again");
    });
});
