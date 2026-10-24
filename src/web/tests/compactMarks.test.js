import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import ChatMark from "../src/kit/ChatMark.vue";
import {ui} from "../src/state/ui.js";

function mounted(mark) {
    const root = document.createElement("div");
    const app = createApp({render: () => h(ChatMark, {mark})});
    app.mount(root);
    return {root, app};
}

test("a fresh viewer's chat is compact: a mark shows one line until a click opens its second, and a second click folds it", async () => {
    expect(ui.compactMarks).toBe(true);
    const {root, app} = mounted({icon: "check", label: "Task 7 done", detail: "the footer names the shop"});
    const mark = root.querySelector(".mark");
    expect(root.querySelector(".detail")).toBeNull();
    mark.click();
    await nextTick();
    expect(root.querySelector(".detail").textContent).toContain("the footer names the shop");
    mark.click();
    await nextTick();
    expect(root.querySelector(".detail")).toBeNull();
    app.unmount();
});

test("turning Compact off shows every mark's second line, and the choice is kept for a reload", async () => {
    ui.compactMarks = false;
    await nextTick();
    const {root, app} = mounted({icon: "check", label: "Task 7 done", detail: "the footer names the shop"});
    expect(root.querySelector(".detail").textContent).toContain("the footer names the shop");
    expect(JSON.parse(localStorage.getItem("journal.chat.compact"))).toBe(false);
    app.unmount();
    ui.compactMarks = true;
});

test("the chat's menu offers Compact, checked while the marks are folded", async () => {
    const {readFileSync} = await import("node:fs");
    const extras = readFileSync("src/panes/PaneMenuExtras.vue", "utf8");
    expect(extras).toMatch(/<PaneMenuToggle icon="list" :on="ui\.compactMarks" @click="ui\.compactMarks = !ui\.compactMarks">Compact<\/PaneMenuToggle>/);
});
