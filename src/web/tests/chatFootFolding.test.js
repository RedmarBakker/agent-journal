import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

const thread = readFileSync("src/chat/Thread.vue", "utf8");
const rule = (selector) => thread.split(`${selector} {`)[1]?.split("}")[0] ?? "";

test("scrolled up, the faded status line gives up its row so the folded docks sit right above the composer", () => {
    const faded = rule(".thread-turn.busy.faded");
    expect(faded).toContain("max-height: 0");
    expect(faded).toContain("margin-top: -7px");
    expect(faded).toContain("opacity: 0");
    expect(rule(".thread-turn.busy")).toMatch(/max-height 0\.25s/);
});
