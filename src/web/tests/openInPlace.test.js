import {readFileSync} from "node:fs";
import {createApp, h, nextTick, ref} from "vue";
import {afterEach, expect, test, vi} from "vitest";

const {useFollowing} = await import("../src/composables/following.js");
const {useOpenInPlace} = await import("../src/composables/openInPlace.js");
const {default: SubagentMark} = await import("../src/chat/SubagentMark.vue");

const FAR = 40;
let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.useRealTimers();
});

// a chat as the thread wires it: a pane following its foot, the reader's press on a turn heard on the pane, and the rows growing told to
// it as the thread's settled() does: an opening turn decides alone, else a reader away keeps their place and one at the foot follows
function chat(top, height = 1000, visible = 400) {
    const size = {height, top};
    let following = null;
    let opening = null;
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({
        setup() {
            const pane = ref(null);
            following = useFollowing(pane, FAR);
            opening = useOpenInPlace(pane, FAR, following.left);
            const mark = h("div", {class: "thread-turn subagent"}, [h(SubagentMark, {task: "look into the tests", finished: true, returned: "Found 3 failing tests.\n\nAll in the viewer.", time: 10})]);
            return () => h("div", {ref: pane, class: "pane", onPointerdown: opening.press, onKeydown: opening.keyed}, [mark]);
        },
    });
    app.mount(host);
    const pane = host.querySelector(".pane");
    Object.defineProperty(pane, "scrollHeight", {get: () => size.height});
    Object.defineProperty(pane, "clientHeight", {get: () => visible});
    Object.defineProperty(pane, "scrollTop", {get: () => size.top, set: (at) => (size.top = Math.min(at, size.height - visible))});
    following.scrolled();
    const settled = (by) => {
        size.height += by;
        if (opening.grew()) return;
        if (!following.away.value) following.toBottom();
    };
    return {host, size, settled, following};
}

test("opening a subagent mark's output at the foot of the chat keeps the chat where it is, then and when the rows settle later", async () => {
    vi.useFakeTimers();
    const {host, size, settled, following} = chat(600);
    const mark = host.querySelector(".mark");
    mark.dispatchEvent(new Event("pointerdown", {bubbles: true}));
    mark.click();
    await nextTick();
    expect(host.textContent).toContain("Found 3 failing tests.");
    settled(300);
    expect(size.top).toBe(600);
    vi.advanceTimersByTime(3000);
    settled(2);
    expect([size.top, following.away.value]).toEqual([600, true]);
});

test("opened from the keyboard in a scrolled chat it keeps the chat where it is too, and a chat at its foot with nothing opened still follows", async () => {
    vi.useFakeTimers();
    const scrolled = chat(200);
    const top = scrolled.host.querySelector(".mark .top");
    top.dispatchEvent(new KeyboardEvent("keydown", {key: "Enter", bubbles: true}));
    top.click();
    await nextTick();
    scrolled.settled(300);
    expect(scrolled.size.top).toBe(200);
    app.unmount();
    const foot = chat(600);
    foot.settled(300);
    expect(foot.size.top).toBe(900);
});

test("the thread tells an opening turn first that the rows grew, and hears presses and keys on its pane", () => {
    const thread = readFileSync("src/chat/Thread.vue", "utf8");
    expect(thread.split("function settled() {")[1].split("\n}\n")[0].trim().startsWith("if (opening.grew()) return;")).toBe(true);
    expect(thread).toContain("const opening = useOpenInPlace(scroller, FAR, readingUp);");
    expect(thread).toContain('@pointerdown="pressed"');
    expect(thread).toContain('@keydown="keyed"');
});
