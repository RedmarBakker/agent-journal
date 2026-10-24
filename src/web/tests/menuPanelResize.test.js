import {createApp, h, nextTick} from "vue";
import {afterEach, expect, test, vi} from "vitest";

const callbacks = [];
globalThis.ResizeObserver = class {
    constructor(callback) {
        callbacks.push(callback);
    }

    observe() {}

    disconnect() {}
};

const {default: MenuPanel} = await import("../src/kit/MenuPanel.vue");

afterEach(() => (document.body.innerHTML = ""));

test("the panel measures itself on the next frame, never inside its resize observer's own callback", async () => {
    const root = document.createElement("div");
    document.body.append(root);
    createApp({render: () => h(MenuPanel, {plain: true}, () => "rows")}).mount(root);
    await nextTick();
    const frames = vi.spyOn(window, "requestAnimationFrame").mockImplementation(() => 1);
    callbacks.at(-1)([]);
    expect(frames).toHaveBeenCalledTimes(1);
    frames.mockRestore();
});
