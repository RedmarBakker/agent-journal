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

test("scrolled up, the chat follows again only on the reader's own scroll to the very foot, or after resting near it for five seconds once the pointer has left the chat a minute ago", () => {
    const watch = thread.split("function watchScroll() {")[1].split("\n}\n")[0];
    // reaching the foot without a hand on the pane, as when the docks fold and the pane gets shorter, only starts the rest
    expect(watch).toContain("else if (!away.value || (Date.now() - scrolledAt < BY_HAND && (gap <= AT_BOTTOM || presence.isGone()))) atTheFoot();");
    expect(watch).toContain("else restAtFoot();");
    expect(thread).toContain("const RESTED_MS = 5000;");
    expect(thread.split("function restAtFoot() {")[1].split("\n}\n")[0]).toContain("Date.now() - scrolledAt >= RESTED_MS");
});

test("scrolled up, messages that arrive are held off the screen and counted, and appear once the chat is back at its foot", () => {
    expect(thread).toContain("watch(away, (isAway) => (heldAfter.value = isAway ?");
    expect(thread).toContain("threadTurns(streamRows(shownChat.value");
    expect(thread).toContain("m.id > heldAfter.value");
    expect(thread).toContain("`${held || missed} new`");
});

test("a turn that arrives while the reader follows grows into its height with the pane held at its foot, so the chat slides up instead of jumping; the user's own message shows at once", () => {
    expect(thread).toContain(`@enter="growIn"`);
    expect(thread).toContain("const arrivalPane = () => ({pane: scroller.value, follows: () => settledOnce.value && !away.value});");
    expect(thread).toContain("const growIn = (el, done) => (isOwnSent(el) ? arriveAtOnce(el, arrivalPane(), done) : arrive(el, arrivalPane(), done));");
});

test("the status line keeps its row at the foot, busy or idle, and slides out only while the pane is scrolled up from it", () => {
    expect(thread).toContain("{faded: offFoot}");
    expect(thread).not.toContain("{faded: away}");
    expect(thread.split("function watchScroll() {")[1].split("\n}\n")[0]).toContain("offFoot.value = gap > FAR;");
    expect(thread).toContain("<span>idle</span>");
});

test("the docks and the status line take their own room under the pane, so a bubble never sits behind them and a reader at the foot stays at it", () => {
    const pane = thread.split('ref="scroller"')[1].split('<Transition name="pane">')[0];
    const [inside, below] = pane.split(':class="[\'chat-foot\'');
    expect(below).toContain('ref="docks" class="chat-docks"');
    expect(inside).not.toContain("chat-docks");
    expect(rule(".chat-foot")).not.toContain("sticky");
    expect(thread).toContain(
        "const paneWatch = new ResizeObserver(() => scroller.value && !away.value && (scroller.value.scrollTop = scroller.value.scrollHeight));"
    );
    expect(thread).toContain("paneWatch.observe(scroller.value);");
});

test("while the plan bar is open the chat never snaps itself to its foot after resting, so the bar never folds and flashes open again", () => {
    const rest = thread.split("function restAtFoot() {")[1].split("\n}\n")[0];
    expect(rest).toContain("!planOpen.value");
});
