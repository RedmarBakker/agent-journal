import {createApp, nextTick} from "vue";
import {expect, test} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
const {default: StatusBar} = await import("../src/layout/StatusBar.vue");
const {store} = await import("../src/state/store.js");
const {choose} = await import("../src/state/environment.js");

const standing = (task) => ({environments: [{environment: {id: 1, name: "main"}, agent: null, task, questions: 0, messages: 0, tasks: 1, silent: false}]});

test("the status line above the chat shows a chevron beside what it opens, and none when there is nothing to open", async () => {
    choose("main");
    store.agents = [{table: "agents", id: 1, session: "s1", status: "working", state: "working", heard_at: new Date().toISOString()}];
    store.summary = standing({id: 3, title: "Fix the cover", awaiting: ""});
    const host = window.document.createElement("div");
    window.document.body.append(host);
    const app = createApp(StatusBar);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".statusbar-roll.link .statusbar-chevron")).not.toBe(null);
    store.summary = standing(null);
    await nextTick();
    expect(host.querySelector(".statusbar-chevron")).toBe(null);
    app.unmount();
    host.remove();
});

test("an agent waiting with no task in hand names what it waits for", async () => {
    choose("main");
    store.agents = [{table: "agents", id: 1, session: "s1", status: "idle", state: "expecting", awaiting: "the full run for 4.1.0", wait_refs: "", awaiting_since: new Date().toISOString(), heard_at: new Date().toISOString()}];
    store.summary = standing(null);
    const host = window.document.createElement("div");
    window.document.body.append(host);
    const app = createApp(StatusBar);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".statusbar-text b").textContent).toBe("Waiting");
    expect(host.querySelector(".statusbar-text").textContent).toContain("the full run for 4.1.0");
    app.unmount();
    host.remove();
});

test("the mode buttons read only their mode's name, and the fitness score is a badge beside them whose hover gives the score and its advice", async () => {
    const {readFileSync} = await import("node:fs");
    const bar = readFileSync("src/layout/StatusBar.vue", "utf8");
    expect(bar).toContain("        label: one.label,\n");
    expect(bar).toContain(`:class="['statusbar-fitness', {low: fitness.is_measured && fitness.score < LOW_FITNESS}]"\n                        v-tip:fitness="fitnessTip"`);
    expect(bar).toContain("title: `Fitness ${fitness.value.score} of 100`");
});

test("the fitness badge opens the measures furthest off the ideal and a timeline of the last hours whose every point names what moved it", async () => {
    const {default: FitnessTimeline} = await import("../src/layout/FitnessTimeline.vue");
    const now = Date.now() / 1000;
    const points = [
        {at: now - 3000, score: 100, is_measured: false, gaps: [], moved: "not scored yet: too few tool uses in this mode"},
        {at: now - 2000, score: 92, is_measured: true, gaps: [], moved: "first score in this mode"},
        {at: now - 1000, score: 61, is_measured: true, gaps: ["your merges are 0%, ideal 90-100%: read the proofs"], moved: "your merges: 100% to 0% of the ideal"},
    ];
    const host = window.document.createElement("div");
    window.document.body.append(host);
    const app = createApp(FitnessTimeline, {score: 61, lines: ["your merges are 0%, ideal 90-100%: read the proofs"], points, hours: 6, low: 70});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".fitness-timeline-heading").textContent).toBe("Fitness 61 of 100");
    expect(host.querySelector(".fitness-timeline-lines").textContent).toContain("your merges are 0%, ideal 90-100%: read the proofs");
    expect(host.querySelector(".fitness-timeline-label").textContent).toBe("Scores over the last 6 hours");
    expect(host.querySelectorAll(".fitness-timeline-dot").length).toBe(2);
    expect(host.querySelectorAll(".fitness-timeline-dot.low").length).toBe(1);
    const moved = [...host.querySelectorAll(".fitness-timeline-point")].map((row) => row.textContent);
    expect(moved[0]).toContain("your merges: 100% to 0% of the ideal");
    expect(moved[0]).toContain("read the proofs");
    expect(moved[2]).toContain("not scored yet");
    const bar = (await import("node:fs")).readFileSync("src/layout/StatusBar.vue", "utf8");
    expect(bar).toContain(`<FitnessTimeline :score="fitness.score" :lines="fitness.lines" :points="fitness.timeline"`);
    app.unmount();
    host.remove();
});
