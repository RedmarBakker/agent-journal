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

test("scrolled up, the chat follows again only on the reader's own scroll to the foot or after resting near it for five seconds", () => {
    const watch = thread.split("function watchScroll() {")[1].split("\n}\n")[0];
    // reaching the foot without a hand on the pane, as when the docks fold and the pane gets shorter, only starts the rest
    expect(watch).toContain("else if (!away.value || Date.now() - scrolledAt < BY_HAND) atTheFoot();");
    expect(watch).toContain("else restAtFoot();");
    expect(thread).toContain("const RESTED_MS = 5000;");
    expect(thread.split("function restAtFoot() {")[1].split("\n}\n")[0]).toContain("Date.now() - scrolledAt >= RESTED_MS");
});
