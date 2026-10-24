import {createApp, h, nextTick} from "vue";
import {afterEach, expect, test} from "vitest";
import AgentTimings from "../src/chat/AgentTimings.vue";

globalThis.ResizeObserver ??= class {
    observe() {}
    disconnect() {}
};

const parts = [
    {name: "PreToolUse", average: 40, count: 250, details: [{label: "Average", text: "40 ms"}, {label: "Slowest", text: "900 ms"}, {label: "Newest", text: "12 ms"}]},
    {name: "Stop", average: 12, count: 8},
];

afterEach(() => (document.body.innerHTML = ""));

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
    const rows = [...document.body.querySelectorAll(".timings-row")].map((row) => [...row.children].map((cell) => cell.textContent.trim()).filter(Boolean).join(" "));
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

test("a reading in points names its unit in the reading and in each part", async () => {
    const root = document.createElement("div");
    document.body.append(root);
    createApp({render: () => h(AgentTimings, {icon: "points", title: "t", heading: "Points per answer", unit: "points", average: 25, parts: [{name: "PreToolUse", average: 40, count: 2}]})}).mount(root);
    await nextTick();
    expect(root.textContent).toContain("25 points");
    root.querySelector(".agent-timings").dispatchEvent(new Event("mouseenter"));
    await nextTick();
    expect([...document.body.querySelectorAll(".timings-row")].pop().textContent).toContain("40 points");
});

test("clicking a part drills into what it is made of and the back row returns to the parts", async () => {
    const root = await mounted();
    root.querySelector(".agent-timings").dispatchEvent(new Event("mouseenter"));
    await nextTick();
    document.body.querySelector(".timings-row").click();
    await nextTick();
    const details = [...document.body.querySelectorAll(".timings-detail")].map((row) => [...row.children].map((cell) => cell.textContent.trim()).join(" "));
    expect(details).toEqual(["Average 40 ms", "Slowest 900 ms", "Newest 12 ms"]);
    document.body.querySelector(".timings-back").click();
    await nextTick();
    expect(document.body.querySelector(".menu-slide").classList.contains("second")).toBe(false);
});
