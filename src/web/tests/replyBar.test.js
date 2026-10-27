import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {createApp, h} from "vue";
import {settle} from "./settle.js";
import {quoteLine} from "../src/format/quote.js";

const answered = [
    "The **build** fails here, see [the log](https://example.com/log):",
    "",
    "```js",
    "const a = 1;",
    "throw new Error(a);",
    "```",
    "",
    "- first, _fix_ the `import`",
].join("\n");

test("replying to a message with a code block puts it in the reply bar as one clipped line of plain words, never a block", async () => {
    const {default: Compose} = await import("../src/chat/Compose.vue");
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(Compose, {send: () => {}, quote: answered, quoteLabel: "Replying to"})});
    app.mount(host);
    await settle();
    const bar = host.querySelector(".compose-quote-text");
    expect(bar.tagName).toBe("P");
    expect(bar.children.length).toBe(0);
    expect(host.querySelector(".compose-quote pre, .compose-quote code")).toBeNull();
    expect(bar.textContent).toBe("The build fails here, see the log: const a = 1; throw new Error(a); first, fix the import");
    expect(bar.title).toBe(bar.textContent);
    const css = readFileSync("src/chat/Compose.vue", "utf8").split(".compose-quote-text {")[1].split("}")[0];
    expect(css).toContain("white-space: nowrap;");
    expect(css).toContain("text-overflow: ellipsis;");
    expect(css).toContain("overflow: hidden;");
    expect(css).not.toContain("line-clamp");
    app.unmount();
    host.remove();
});

test("a quoted line keeps a chip's words and drops quote, heading and list marks", () => {
    expect(quoteLine("> earlier\n# Plan\n1. one\n2) two")).toBe("earlier Plan one two");
    expect(quoteLine("see [[tasks 12|task 12]] now")).toBe("see task 12 now");
});
