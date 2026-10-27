import {readFileSync} from "node:fs";
import {createApp, h, ref} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const {SETTLE_AFTER_MS, useFollowing} = await import("../src/composables/following.js");
const {POINTER_GONE_MS, usePointerPresence} = await import("../src/composables/pointerPresence.js");

let app = null;

beforeEach(() => vi.useFakeTimers());

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.useRealTimers();
});

// a chat as the thread wires it: the pointer's presence heard on the whole chat, the pane inside it following its foot, and below the
// pane the docks; the pane's sizes are set by hand, since the test page lays nothing out
function chat(height = 1000, visible = 400) {
    const size = {height, top: 0};
    let following = null;
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({
        setup() {
            const root = ref(null);
            const pane = ref(null);
            const presence = usePointerPresence(() => following.away.value && following.toBottom(), POINTER_GONE_MS, root);
            following = useFollowing(pane, 40, presence.isGone);
            return () => h("div", {ref: root, class: "thread"}, [h("div", {ref: pane, class: "pane"}), h("div", {class: "docks"})]);
        },
    });
    app.mount(host);
    const pane = host.querySelector(".pane");
    Object.defineProperty(pane, "scrollHeight", {get: () => size.height});
    Object.defineProperty(pane, "clientHeight", {get: () => visible});
    Object.defineProperty(pane, "scrollTop", {get: () => size.top, set: (top) => (size.top = Math.min(top, size.height - visible))});
    const scrollTo = (top) => {
        size.top = top;
        following.scrolled();
    };
    const grow = (by) => {
        size.height += by;
        following.arrived(1);
    };
    return {host, pane, size, scrollTo, grow, following};
}

test("with the pointer over a scrolled-up chat, the thread growing below never moves it, however long it rests", () => {
    const {pane, size, scrollTo, grow} = chat();
    pane.dispatchEvent(new WheelEvent("wheel", {bubbles: true, deltaY: -300}));
    scrollTo(100);
    grow(600);
    grow(400);
    vi.advanceTimersByTime(SETTLE_AFTER_MS * 4 + POINTER_GONE_MS * 2);
    expect(size.top).toBe(100);
});

test("a pointer resting on the docks, or one that was over the chat before it drew and only moved, still holds a scrolled-up chat in place", () => {
    const {host, size, scrollTo, grow} = chat();
    host.querySelector(".docks").dispatchEvent(new Event("pointermove", {bubbles: true}));
    scrollTo(510);
    grow(30);
    vi.advanceTimersByTime(SETTLE_AFTER_MS * 4 + POINTER_GONE_MS * 2);
    expect(size.top).toBe(510);
});

test("a reader at the foot still follows what arrives, and once the pointer has left the chat a minute a reader still away goes back to the foot", () => {
    const {host, size, scrollTo, grow, following} = chat();
    scrollTo(600);
    grow(500);
    expect([following.away.value, size.top]).toEqual([false, 1100]);
    host.querySelector(".thread").dispatchEvent(new Event("pointerenter"));
    scrollTo(200);
    host.querySelector(".thread").dispatchEvent(new Event("pointerleave"));
    vi.advanceTimersByTime(POINTER_GONE_MS);
    expect([following.away.value, size.top]).toEqual([false, 1100]);
});

test("the thread hears the pointer on its whole root, so its pane, its docks and its composer all count as over the chat", () => {
    const thread = readFileSync("src/chat/Thread.vue", "utf8");
    expect(thread).toContain("usePointerPresence(() => away.value && toBottom(true), POINTER_GONE_MS, threadRoot);");
    expect(thread).toContain('<div ref="threadRoot" class="thread">');
    expect(thread).not.toContain('@pointerenter="presence.entered"');
});
