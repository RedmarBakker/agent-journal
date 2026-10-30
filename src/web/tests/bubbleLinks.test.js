import {expect, test} from "vitest";

const {render} = await import("../src/text/index.js");
await import("../src/text/all.js");

const anchors = (text) => {
    const into = document.createElement("div");
    into.innerHTML = render(text, {env: ""});
    return {into, links: [...into.querySelectorAll("a[href^='http']")]};
};

test("a web address written in a bubble is a link that opens it in a new tab, without its closing punctuation", () => {
    const {into, links} = anchors("the release is at https://github.com/x/y/releases/tag/v1.2. See it, and http://127.0.0.1:8420/?env=main too");
    expect(links.map((a) => a.getAttribute("href"))).toEqual(["https://github.com/x/y/releases/tag/v1.2", "http://127.0.0.1:8420/?env=main"]);
    expect(links.every((a) => a.target === "_blank" && a.rel === "noopener")).toBe(true);
    expect(into.textContent).toBe("the release is at https://github.com/x/y/releases/tag/v1.2. See it, and http://127.0.0.1:8420/?env=main too");
});

test("an address inside code, or already the target of a written link, is not linked again", () => {
    const {links} = anchors("run `curl https://a.test/x` or read [the docs](https://b.test/docs)");
    expect(links.map((a) => a.getAttribute("href"))).toEqual(["https://b.test/docs"]);
    expect(links[0].textContent).toBe("the docs");
});

test("a row named beside an address keeps its own link", () => {
    const into = document.createElement("div");
    into.innerHTML = render("task 546 is filed, see https://c.test/page", {env: ""});
    expect([...into.querySelectorAll("a[data-peek]")].map((a) => a.dataset.peek)).toEqual(["tasks:546"]);
    expect([...into.querySelectorAll("a[href^='http']")].map((a) => a.getAttribute("href"))).toEqual(["https://c.test/page"]);
});
