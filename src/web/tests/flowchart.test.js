import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const {default: Turn} = await import("../src/chat/Turn.vue");
const {threadTurns} = await import("../src/domain/thread.js");
const {layoutOf} = await import("../src/domain/flowchart.js");

let app = null;
afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

const EDGES = [
    ["Start", "Ask the user", ""],
    ["Ask the user", "Done", "yes"],
    ["Ask the user", "Try again", "no"],
];
const drawn = {table: "messages", id: 4, created_at: new Date(1e4).toISOString(), author: "system", text: "How a request is handled", files: [], comments_on: [], data: {kind: "flowchart", edges: EDGES}};

test("an agent's flowchart message shows in the chat as a flowchart mark and its button opens the chart large in a dialog", async () => {
    const scope = {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}};
    const turn = threadTurns([drawn], []).turns[0];
    expect(turn.kind).toBe("flowchart");
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(Turn, {turn})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".mark").textContent).toContain("How a request is handled");
    expect(host.querySelector(".mact").getAttribute("aria-label")).toBe("Open the flowchart");
    expect(document.querySelector(".flowchart")).toBeNull();
    host.querySelector(".mact").click();
    await flush();
    const chart = document.querySelector(".flowchart");
    expect(chart.querySelectorAll(".flowchart-node").length).toBe(4);
    expect(chart.querySelectorAll(".flowchart-arrow").length).toBe(3);
    expect([...chart.querySelectorAll(".flowchart-label")].map((label) => label.textContent)).toEqual(["yes", "no"]);
});

test("the chart puts each name a step below the one that leads to it, the top name first", () => {
    const {nodes} = layoutOf(EDGES);
    const at = Object.fromEntries(nodes.map((node) => [node.name, node.y]));
    expect(at.Start).toBeLessThan(at["Ask the user"]);
    expect(at["Ask the user"]).toBeLessThan(at.Done);
    expect(at.Done).toBe(at["Try again"]);
    expect(layoutOf([["A", "B", ""], ["B", "A", ""]]).nodes.map((node) => node.name)).toEqual(["A", "B"]);
});
