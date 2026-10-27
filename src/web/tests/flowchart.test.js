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
const {layoutOf, overlaps} = await import("../src/domain/flowchart.js");

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

test("an agent's flowchart message shows in the chat as a card with its title and a button that opens the chart large in a dialog", async () => {
    const scope = {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}};
    const turn = threadTurns([drawn], []).turns[0];
    expect(turn.kind).toBe("flowchart");
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(Turn, {turn})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".flowchart-card-title").textContent).toBe("How a request is handled");
    expect(host.querySelector(".flowchart-open").textContent.trim()).toBe("Open the flowchart");
    expect(document.querySelector("svg.flowchart")).toBeNull();
    host.querySelector(".flowchart-open").click();
    await flush();
    const chart = document.querySelector("svg.flowchart");
    expect(chart.querySelectorAll(".flowchart-node").length).toBe(4);
    expect(chart.querySelectorAll(".flowchart-arrow").length).toBe(3);
    expect([...chart.querySelectorAll(".flowchart-label")].map((label) => label.textContent)).toEqual(["yes", "no"]);
    expect([...document.querySelectorAll(".flowchart-tools button")].map((button) => button.textContent.trim())).toEqual(["Zoom in", "Zoom out", "Fit the whole chart"]);
});

test("the chart puts each name a step below the one that leads to it, the top name first", () => {
    const {nodes} = layoutOf(EDGES);
    const at = Object.fromEntries(nodes.map((node) => [node.name, node.y]));
    expect(at.Start).toBeLessThan(at["Ask the user"]);
    expect(at["Ask the user"]).toBeLessThan(at.Done);
    expect(at.Done).toBe(at["Try again"]);
    expect(layoutOf([["A", "B", ""], ["B", "A", ""]]).nodes.map((node) => node.name)).toEqual(["A", "B"]);
});

// the chart of how a plan's state follows its tasks, as the agent drew it in message 72785: long names and labels, and arrows going back up
const PLAN_STATES = [
    ["Active, the agent works a task of it", "Delegated, a worker works a task of it", "the agent hands a task to a worker and holds none of the plan's tasks itself"],
    ["Delegated, a worker works a task of it", "Paused", "the last worker on it finishes"],
    ["Delegated, a worker works a task of it", "Active, the agent works a task of it", "the agent starts one of its tasks itself"],
    ["Paused", "Active, the agent works a task of it", "the agent starts it again"],
    ["Paused", "Delegated, a worker works a task of it", "a task of it goes to a worker"],
    ["Active, the agent works a task of it", "Blocked", "every task left is blocked"],
];

test("every card holds its words, no two cards, labels or a card and a label overlap, and all of it lies inside the drawing, in a chart with long names and arrows going back", () => {
    const {nodes, arrows, width, height} = layoutOf(PLAN_STATES);
    const labels = arrows.map((arrow) => arrow.label).filter(Boolean);
    expect(labels.length).toBe(PLAN_STATES.length);
    const boxes = [...nodes, ...labels];
    boxes.forEach((box, index) => boxes.slice(index + 1).forEach((other) => expect(overlaps(box, other), `${box.name ?? box.lines} and ${other.name ?? other.lines}`).toBe(false)));
    nodes.forEach((node) => expect(Math.max(...node.lines.map((line) => line.length)) * 7.4).toBeLessThanOrEqual(node.width));
    boxes.forEach((box) => expect(box.x >= 0 && box.y >= 0 && box.x + box.width <= width && box.y + box.height <= height).toBe(true));
});
