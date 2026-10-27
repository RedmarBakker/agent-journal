import {createApp, h, nextTick, ref} from "vue";
import {beforeEach, describe, expect, test, vi} from "vitest";
import Skeleton from "../src/kit/Skeleton.vue";
import {useScrollback} from "../src/composables/scrollback.js";

beforeEach(() => {
    window.IntersectionObserver = class {
        observe() {}
        disconnect() {}
    };
    globalThis.IntersectionObserver = window.IntersectionObserver;
});

// a scroller of the given sizes, as the browser measures them
function sized(client, scroll, top = 0) {
    const box = window.document.createElement("div");
    const sizes = {clientHeight: client, scrollHeight: scroll, scrollTop: top};
    for (const name of Object.keys(sizes)) Object.defineProperty(box, name, {get: () => sizes[name], set: (v) => (sizes[name] = v), configurable: true});
    box.sizes = sizes;
    return box;
}

function paged(load, ready = () => true, box = sized(800, 3000)) {
    const made = {};
    const host = window.document.createElement("div");
    createApp({
        setup() {
            Object.assign(made, useScrollback(ref(box), ref(null), load, {ready}));
            return () => h("div", made.loading.value ? "loading" : "idle");
        },
    }).mount(host);
    return {made, host};
}

describe("paging back in a chat", () => {
    test("says it is loading while the older page is on its way, and asks for one page at a time", async () => {
        let arrive;
        const load = vi.fn(() => new Promise((resolve) => (arrive = resolve)));
        const {made, host} = paged(load);
        const first = made.older();
        await nextTick();
        expect(host.textContent).toBe("loading");
        await made.older();
        expect(load).toHaveBeenCalledTimes(1);
        arrive(true);
        await first;
        await nextTick();
        expect(host.textContent).toBe("idle");
    });

    test("loads nothing while the chat is not ready to page back", async () => {
        const load = vi.fn(async () => true);
        const {made} = paged(load, () => false);
        expect(await made.older()).toBe(false);
        expect(load).not.toHaveBeenCalled();
    });

    test("draws skeleton rows for the page that is arriving", () => {
        const host = window.document.createElement("div");
        createApp({render: () => h(Skeleton, {shape: "older", label: "Loading older messages"})}).mount(host);
        expect(host.querySelector("[aria-busy='true']").getAttribute("aria-label")).toBe("Loading older messages");
        expect(host.querySelectorAll(".skeleton-message").length).toBe(3);
    });

    test("loads one older page at the top and the next only after the reader leaves the top and returns", async () => {
        const box = sized(800, 3000);
        const mark = window.document.createElement("div");
        let markTop = 0;
        box.getBoundingClientRect = () => ({top: 0});
        mark.getBoundingClientRect = () => ({top: markTop});
        const load = vi.fn(async () => true);
        const made = {};
        createApp({
            setup() {
                Object.assign(made, useScrollback(ref(box), ref(mark), load));
                return () => h("div");
            },
        }).mount(window.document.createElement("div"));
        await made.older();
        await made.older();
        box.dispatchEvent(new Event("scroll"));
        await made.older();
        expect(load).toHaveBeenCalledTimes(1);
        markTop = -900;
        box.dispatchEvent(new Event("scroll"));
        markTop = 0;
        await made.older();
        await made.older();
        expect(load).toHaveBeenCalledTimes(2);
        await made.older();
        expect(load).toHaveBeenCalledTimes(2);
    });

    function pagedIn(box, load, options = {}) {
        const made = {};
        createApp({
            setup() {
                Object.assign(made, useScrollback(ref(box), ref(null), load, options));
                return () => h("div");
            },
        }).mount(window.document.createElement("div"));
        return made;
    }

    test("a first page too short to scroll fills the window with just the pages it takes to scroll, then stops", async () => {
        const box = sized(800, 300);
        const load = vi.fn(async () => (box.sizes.scrollHeight += 300) > 0);
        const made = pagedIn(box, load);
        await made.older();
        expect(load).toHaveBeenCalledTimes(2);
        expect(box.sizes.scrollHeight).toBeGreaterThan(800);
    });

    test("a chat too short to scroll fills itself once it is ready, though nothing scrolls and its top mark is never sighted again", async () => {
        const isReady = ref(false);
        const load = vi.fn(async () => true);
        paged(load, () => isReady.value, sized(800, 300));
        isReady.value = true;
        await nextTick();
        await nextTick();
        expect(load).toHaveBeenCalled();
    });

    test("a chat that never grows past its window asks for no more than five pages", async () => {
        const load = vi.fn(async () => true);
        await pagedIn(sized(800, 300), load).older();
        expect(load).toHaveBeenCalledTimes(5);
    });

    test("a chat that scrolls pages back only when the reader has scrolled up into its top screenful", async () => {
        const load = vi.fn(async () => true);
        expect(await pagedIn(sized(800, 3000, 2200), load).older()).toBe(false);
        expect(await pagedIn(sized(800, 3000, 800), load).older()).toBe(false);
        expect(await pagedIn(sized(800, 3000, 0), load, {scrolled: () => false}).older()).toBe(false);
        expect(load).not.toHaveBeenCalled();
        await pagedIn(sized(800, 3000, 799), load).older();
        expect(load).toHaveBeenCalledTimes(1);
    });

    test("a window with no height asks for nothing", async () => {
        const load = vi.fn(async () => true);
        expect(await pagedIn(sized(0, 0), load).older()).toBe(false);
        expect(load).not.toHaveBeenCalled();
    });
});
