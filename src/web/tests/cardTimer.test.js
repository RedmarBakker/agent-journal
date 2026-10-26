import {createApp, h} from "vue";
import {afterEach, describe, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {default: ChatMark} = await import("../src/kit/ChatMark.vue");

let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.useRealTimers();
});

async function shown(mark) {
    const root = document.createElement("div");
    document.body.appendChild(root);
    app = createApp({render: () => h(ChatMark, {mark})});
    app.mount(root);
    await flush();
    return root.querySelector(".ran-for")?.textContent || "";
}

describe("a run's card in the chat", () => {
    test("shows how long the run has gone when its reader counts no progress, as a release watch's does", async () => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date(200_000 * 1000));
        expect(await shown({label: "Watching the release", began_at: 200_000 - 185, counting: false, figure: ""})).toBe("3m 05s");
    });

    test("shows its bar and no timer when the reader counts progress, and nothing once the run has ended", async () => {
        expect(await shown({label: "Running tests", began_at: 1, counting: true, figure: "12/40"})).toBe("");
        app.unmount();
        expect(await shown({label: "Watching the release", began_at: 1, counting: false, figure: "", ending: "finished"})).toBe("");
    });
});
