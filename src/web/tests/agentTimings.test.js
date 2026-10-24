import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import AgentTimings from "../src/chat/AgentTimings.vue";

globalThis.ResizeObserver ??= class {
    observe() {}
    disconnect() {}
};

const parts = [
    {name: "PreToolUse", average_ms: 40, count: 250},
    {name: "Stop", average_ms: 12, count: 8},
];

async function mounted() {
    const root = document.createElement("div");
    document.body.append(root);
    createApp({render: () => h(AgentTimings, {icon: "hook", title: "t", heading: "Hooks", average: 26, parts})}).mount(root);
    await nextTick();
    return root;
}

test("hovering the reading opens a dropdown of each part with its own average and how many timings it has, slowest first", async () => {
    const root = await mounted();
    expect(root.textContent).toContain("26 ms");
    root.querySelector(".agent-timings").dispatchEvent(new Event("mouseenter"));
    await nextTick();
    const rows = [...document.body.querySelectorAll(".timings-row")].map((row) => [...row.children].map((cell) => cell.textContent.trim()).join(" "));
    expect(rows).toEqual(["PreToolUse 40 ms 250 timed", "Stop 12 ms 8 timed"]);
});

test("clicking the reading holds the dropdown open past the pointer leaving", async () => {
    const root = await mounted();
    const bar = root.querySelector(".agent-timings");
    bar.dispatchEvent(new Event("mouseenter"));
    root.querySelector("button").click();
    bar.dispatchEvent(new Event("mouseleave"));
    await new Promise((done) => setTimeout(done, 400));
    expect(document.body.querySelectorAll(".timings-row").length).toBeGreaterThan(0);
});
