import {createApp, h, nextTick, ref} from "vue";
import {expect, test, vi} from "vitest";

import ChatMark from "../src/kit/ChatMark.vue";

test("a mark opened or closed hides its contents while it moves and shows them once it has its size", async () => {
    vi.useFakeTimers();
    const open = ref(false);
    const host = document.createElement("div");
    document.body.append(host);
    const mark = {key: "watch:1", label: "Building the viewer", command: "npm run build", detail: "built in 3 seconds"};
    const app = createApp({render: () => h(ChatMark, {mark, open: open.value}, () => h("pre", {class: "terminal"}, "vite build"))});
    app.mount(host);
    await nextTick();
    const node = host.querySelector(".mark");
    expect(node.classList.contains("moving")).toBe(false);
    open.value = true;
    await nextTick();
    expect(node.hasAttribute("data-open") && node.classList.contains("moving")).toBe(true);
    vi.advanceTimersByTime(400);
    await nextTick();
    expect(node.classList.contains("moving")).toBe(false);
    open.value = false;
    await nextTick();
    expect(!node.hasAttribute("data-open") && node.classList.contains("moving")).toBe(true);
    app.unmount();
    host.remove();
    vi.useRealTimers();
});
