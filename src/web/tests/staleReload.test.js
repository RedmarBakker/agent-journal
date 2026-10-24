import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {createApp, h, ref} from "vue";
import {useStaleReload} from "../src/composables/staleReload.js";

let reloads = 0;
// the window the page runs in, its reload counted
const win = Object.assign(new EventTarget(), {
    document,
    location: {reload: () => reloads++},
    setInterval: (run, ms) => setInterval(run, ms),
    clearInterval: (id) => clearInterval(id),
});

beforeEach(() => {
    vi.useFakeTimers();
    reloads = 0;
});
afterEach(() => vi.useRealTimers());

function mounted(stale, drafting = () => false) {
    let made = null;
    const app = createApp({setup: () => ((made = useStaleReload(stale, drafting, win)), () => h("div"))});
    app.mount(document.createElement("div"));
    return {app, made};
}

test("a newer viewer build never reloads the page by itself, however long it is left or hidden; the reader reloads it", () => {
    const stale = ref(true);
    const {app, made} = mounted(stale);
    vi.advanceTimersByTime(30 * 60 * 1000);
    Object.defineProperty(document, "visibilityState", {configurable: true, get: () => "hidden"});
    document.dispatchEvent(new Event("visibilitychange"));
    expect(reloads).toBe(0);
    made.reload();
    expect(reloads).toBe(1);
    app.unmount();
});

test("asked to reload while a message is being written, the page waits until the draft is gone", () => {
    let writing = true;
    const {app, made} = mounted(ref(true), () => writing);
    win.dispatchEvent(new Event("keydown"));
    expect(made.waiting.value).toBe(true);
    writing = false;
    win.dispatchEvent(new Event("keydown"));
    expect(made.waiting.value).toBe(false);
    app.unmount();
});
