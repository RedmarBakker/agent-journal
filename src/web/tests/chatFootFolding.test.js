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





test("a turn that arrives while the reader follows grows into its height with the pane held at its foot, so the chat slides up instead of jumping; the user's own message shows at once", () => {
    expect(thread).toContain(`@enter="growIn"`);
    expect(thread).toContain("const following = () => settledOnce.value && !away.value && !releasingHeld.value && !ui.away.tabHidden && !ui.away.readingLatest;");
    expect(thread).toContain("const arrivalPane = () => ({pane: scroller.value, follows: following});");
    expect(thread).toContain("const growIn = (el, done) => (isOwnSent(el) ? arriveAtOnce(el, arrivalPane(), done) : comeIn(el, arrivalPane(), done));");
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



test("the docked cards run the composer's whole width: their side margins cancel the foot's side padding exactly", () => {
    const padding = rule(".chat-foot").match(/padding: 0 (\d+)px;/)[1];
    expect(rule(".chat-docks")).toContain(`margin: 0 -${padding}px;`);
    expect(rule(".chat-docks")).not.toContain("width: 100%");
});
