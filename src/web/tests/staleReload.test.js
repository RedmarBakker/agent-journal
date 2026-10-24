import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {createApp, h, ref} from "vue";
import {RELOAD_AFTER, useStaleReload} from "../src/composables/staleReload.js";

let reloads = 0;
let visibility = "visible";
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
    visibility = "visible";
    Object.defineProperty(document, "visibilityState", {configurable: true, get: () => visibility});
});
afterEach(() => vi.useRealTimers());

function mounted(stale, drafting = () => false) {
    const host = document.createElement("div");
    const app = createApp({setup: () => (useStaleReload(stale, drafting, win), () => h("div"))});
    app.mount(host);
    return app;
}

test("a newer viewer build reloads the page only once it has been left untouched a minute, or at once when it goes out of sight", () => {
    const stale = ref(false);
    const app = mounted(stale);
    // the page in use runs its viewer on: no reload while its build is the newest
    vi.advanceTimersByTime(5 * RELOAD_AFTER * 1000);
    expect(reloads).toBe(0);
    // a newer build: every touch starts the minute again, so a reader at work keeps the page
    stale.value = true;
    for (let second = 0; second < 3 * RELOAD_AFTER; second += 20) {
        vi.advanceTimersByTime(20 * 1000);
        win.dispatchEvent(new Event("wheel"));
    }
    expect(reloads, "touched every twenty seconds, never reloaded").toBe(0);
    // left alone a whole minute, it reloads
    vi.advanceTimersByTime(RELOAD_AFTER * 1000);
    expect(reloads).toBe(1);
    app.unmount();
});

test("a stale page reloads at once when it goes out of sight, and never while a message is being written", () => {
    const stale = ref(true);
    let writing = true;
    const app = mounted(stale, () => writing);
    vi.advanceTimersByTime(3 * RELOAD_AFTER * 1000);
    expect(reloads, "a draft holds it").toBe(0);
    writing = false;
    win.dispatchEvent(new Event("keydown"));
    visibility = "hidden";
    document.dispatchEvent(new Event("visibilitychange"));
    expect(reloads).toBe(1);
    app.unmount();
});
