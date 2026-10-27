import {expect, test} from "vitest";

const {render} = await import("../src/text/index.js");
const {peekChip} = await import("../src/route.js");
await import("../src/text/all.js");

test("a row named inside a sentence is a chip that opens the row", () => {
    const into = document.createElement("div");
    into.innerHTML = render("see task 546 and plan 12", {env: ""});
    const chips = [...into.querySelectorAll("a[data-peek]")];
    expect(chips.map((c) => c.dataset.peek)).toEqual(["tasks:546", "plans:12"]);
    expect(into.textContent).toBe("see task 546 and plan 12");
    into.addEventListener("click", peekChip);
    chips[1].click();
    expect(location.hash).toContain("open=plans:12");
});

test("a row named inside code or a link stays as it is", () => {
    const html = render("run `task 5` or [task 6](https://x.test)", {env: ""});
    expect(html).not.toContain("data-peek");
});

test("a row named with a line, a span of lines or a section is a chip that opens the row at that place", () => {
    const into = document.createElement("div");
    into.innerHTML = render("read doc 55:120, then doc 55:10-14 and doc 55:section 3; task 7 stays plain", {env: ""});
    const chips = [...into.querySelectorAll("a[data-peek]")];
    expect(chips.map((c) => [c.dataset.peek, c.dataset.sub || ""])).toEqual([["docs:55", "120"], ["docs:55", "10-14"], ["docs:55", "section 3"], ["tasks:7", ""]]);
    expect(into.textContent).toBe("read doc 55:120, then doc 55:10-14 and doc 55:section 3; task 7 stays plain");
});

test("a chat mark draws the rows its words name as plain text, so a click on it opens its own row", () => {
    const into = document.createElement("div");
    into.innerHTML = render("Started task 1398: the worker wait", {env: "", rowNames: false});
    expect(into.querySelectorAll("a[data-peek]").length).toBe(0);
    expect(into.textContent).toBe("Started task 1398: the worker wait");
});

test("a row number in parentheses after its word is a chip too", () => {
    const into = document.createElement("div");
    into.innerHTML = render("the joining task (1463) and plan (24)", {env: ""});
    expect([...into.querySelectorAll("a[data-peek]")].map((c) => c.dataset.peek)).toEqual(["tasks:1463", "plans:24"]);
    expect(into.textContent).toBe("the joining task 1463 and plan 24");
});

test("a word with a list of numbers makes each number its own chip of the singular word", () => {
    const into = document.createElement("div");
    into.innerHTML = render("Messages 62830, 62833 and 62837 hold the same text, as do tasks 12, 13", {env: ""});
    const chips = [...into.querySelectorAll("a[data-peek]")];
    expect(chips.map((c) => c.dataset.peek)).toEqual(["messages:62830", "messages:62833", "messages:62837", "tasks:12", "tasks:13"]);
    expect(chips.map((c) => c.textContent)).toEqual(["Message 62830", "Message 62833", "Message 62837", "task 12", "task 13"]);
    expect(into.textContent).toBe("Message 62830, Message 62833 and Message 62837 hold the same text, as do task 12, task 13");
});

test("a table whose cells name rows keeps its shape, each name a chip inside its cell", async () => {
    const {render} = await import("../src/text/index.js");
    const html = render("| Key | Now |\n|---|---|\n| a | task 3 is open |\n| b | plan 4 is done |");
    expect(html.startsWith("<table>")).toBe(true);
    expect((html.match(/<tr>/g) || []).length).toBe(3);
    expect(html).not.toContain("|");
});
