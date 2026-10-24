import {beforeEach, expect, test} from "vitest";
import {register, render} from "../src/text/index.js";
import "../src/text/all.js";
import {store} from "../src/state/store.js";

let scans = 0;
register((text) => {
    scans++;
    return text;
}, {first: true});

beforeEach(() => {
    scans = 0;
    store.rows = {tasks: [{table: "tasks", id: 7, title: "the footer", brief: "make it calm"}]};
});

test("the same text in the same environment is scanned once, whatever object carries the options", () => {
    const first = render("a plain line", {env: "dev", types: []});
    expect(render("a plain line", {env: "dev", types: []})).toBe(first);
    expect(scans).toBe(1);
    render("another line", {env: "dev"});
    render("a plain line", {env: "prod"});
    render("a plain line", {env: "dev", inline: true});
    expect(scans).toBe(4);
});

test("a kept text showing a row's card is drawn again once that row is renamed", () => {
    expect(render("task 7", {env: "dev"})).toContain("the footer");
    store.rows = {tasks: [{table: "tasks", id: 7, title: "the calm footer", brief: "make it calm"}]};
    expect(render("task 7", {env: "dev"})).toContain("the calm footer");
    expect(scans).toBe(2);
});

test("a transformer registered after a render takes effect on the next one", () => {
    render("shout this", {env: "dev"});
    register((text) => text.replace("shout", "SHOUT"));
    expect(render("shout this", {env: "dev"})).toContain("SHOUT");
});

test("the kept renders are bounded, the oldest dropped first", () => {
    render("line 0", {env: "dev"});
    for (let n = 1; n <= 2000; n++) render(`line ${n}`, {env: "dev"});
    scans = 0;
    render("line 2000", {env: "dev"});
    expect(scans).toBe(0);
    render("line 0", {env: "dev"});
    expect(scans).toBe(1);
});
