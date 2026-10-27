import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const loading = vi.fn(() => new Promise(() => {}));
vi.mock("../src/figure/assets.js", () => ({loadVoiceFigure: (...args) => loading(...args)}));

const {default: VoiceFigure} = await import("../src/chat/VoiceFigure.vue");
const {figureStatus} = await import("../src/composables/voiceFigure.js");

let app = null;
afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

const show = async () => {
    app = createApp({render: () => h(VoiceFigure, {voice: "lovelace"})});
    app.mount(document.body.appendChild(document.createElement("div")));
    await flush();
};

test("leaving Home takes the figure's shown status with it, and coming back loads the figure and plays its entry again", async () => {
    await show();
    expect(loading).toHaveBeenCalledTimes(1);
    figureStatus.value = "shown";
    app.unmount();
    expect(figureStatus.value).toBe("loading");
    await show();
    expect(loading).toHaveBeenCalledTimes(2);
    expect(figureStatus.value).toBe("loading");
});
