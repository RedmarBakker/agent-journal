import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {api} = await import("../src/api/client.js");
const {store} = await import("../src/state/store.js");
const {meta} = await import("../src/domain/tables.js");
const {actsOf} = await import("../src/domain/acts.js");
const {default: ResourceBody} = await import("../src/resource/ResourceBody.vue");

afterEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("a memory's inspector shows its text, its weight, when it was added and last weighed, and its acts, with no console error", async () => {
    const memory = {table: "memories", id: 3, text: "The user signs off with a single word", weight: 7, keywords: [], removed_at: null, created_at: new Date(Date.now() - 3 * 86400e3).toISOString(), updated_at: new Date(Date.now() - 3600e3).toISOString()};
    store.rows = {memories: [memory], messages: [], links: [], comments: []};
    const act = vi.spyOn(api, "act").mockResolvedValue({});
    const errors = [];
    vi.spyOn(console, "error").mockImplementation((...args) => errors.push(args.join(" ")));
    expect(meta("memories")).toMatchObject({title: "Memory", icon: "pin"});
    expect(actsOf(memory).map((a) => a.label)).toEqual(["Weigh", "Remove"]);
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(ResourceBody, {resource: memory, comments: false, links: false})});
    app.config.errorHandler = (error) => errors.push(String(error));
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.textContent).toContain("The user signs off with a single word");
    const facts = [...host.querySelectorAll(".memory-facts .fact")].map((fact) => [fact.querySelector(".label").textContent, fact.querySelector(".value").textContent.trim()]);
    expect(facts.map(([label]) => label)).toEqual(["Weight", "Added", "Last weighed"]);
    expect(facts[0][1]).toBe("7 of 10");
    expect(facts[1][1]).not.toBe("");
    const buttons = [...host.querySelectorAll("button")];
    const weigh = buttons.find((b) => b.textContent.trim() === "Weigh");
    expect(buttons.some((b) => b.textContent.trim() === "Remove")).toBe(true);
    weigh.click();
    await flush();
    const input = host.querySelector('input[placeholder="A weight from 1 to 10"]');
    expect(input).not.toBeNull();
    input.value = "9";
    input.dispatchEvent(new Event("input"));
    [...host.querySelectorAll("button")].find((b) => b.textContent.trim() === "Weigh").click();
    await flush();
    expect(act).toHaveBeenCalledWith("memories", 3, "weigh", {weight: "9"});
    expect(errors).toEqual([]);
    app.unmount();
});
