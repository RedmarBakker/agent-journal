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
    createApp({render: () => h(AgentTimings, {icon: "hook", title: "t", heading: "Agent actions", average: 26, parts})}).mount(root);
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

test("a menu with many parts is no taller than its limit and scrolls its rows, the heading and the back row staying outside the scrolling rows", async () => {
    const root = document.createElement("div");
    document.body.append(root);
    const many = Array.from({length: 80}, (_, i) => ({name: `GET /journal/route${i}`, average: 80 - i, count: 3, details: Array.from({length: 40}, (_, n) => ({label: `table${n}`, text: "1 rows, 0 KB, 0 writes"}))}));
    createApp({render: () => h(AgentTimings, {icon: "request", title: "t", heading: "Requests", average: 40, parts: many})}).mount(root);
    await nextTick();
    root.querySelector(".agent-timings").dispatchEvent(new Event("mouseenter"));
    await nextTick();
    const [list] = document.body.querySelectorAll(".timings-rows");
    const widthBefore = document.body.querySelector(".menu-panel").style.width;
    expect(list.querySelectorAll(".timings-row")).toHaveLength(80);
    expect([list.style.maxHeight, list.style.overflowY]).toEqual(["min(420px, 60vh)", "auto"]);
    expect(list.contains(document.body.querySelector(".timings-head"))).toBe(false);
    document.body.querySelector(".timings-row").click();
    await nextTick();
    const [, drilledList] = document.body.querySelectorAll(".timings-rows");
    expect(drilledList.querySelectorAll(".timings-detail")).toHaveLength(40);
    expect([drilledList.style.maxHeight, drilledList.style.overflowY]).toEqual(["min(420px, 60vh)", "auto"]);
    expect(drilledList.contains(document.body.querySelector(".timings-back"))).toBe(false);
    const panel = document.body.querySelector(".menu-panel");
    expect([panel.style.width, panel.style.minWidth, panel.style.maxWidth]).toEqual([widthBefore, "340px", "340px"]);
    expect(widthBefore).toBe("340px");
    document.body.querySelector(".timings-back").click();
    await nextTick();
    expect([panel.style.width, document.body.querySelectorAll(".menu-panel").length]).toEqual(["340px", 1]);
});
