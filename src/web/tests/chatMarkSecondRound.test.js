import {existsSync, readFileSync} from "node:fs";
import {createApp, h, nextTick, reactive, ref} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const {api} = await import("../src/api/client.js");
const {choose} = await import("../src/state/environment.js");
const {default: ChatMark} = await import("../src/kit/ChatMark.vue");
const {default: FoldSign} = await import("../src/kit/FoldSign.vue");
const {default: GrowingCard} = await import("../src/chat/GrowingCard.vue");
const {default: Turn} = await import("../src/chat/Turn.vue");
const {default: WatchDock} = await import("../src/chat/WatchDock.vue");
const {default: DockGroup} = await import("../src/chat/DockGroup.vue");
const {default: TaskLine} = await import("../src/chat/TaskLine.vue");
const {MARK_ICONS} = await import("../src/kit/markIcons.js");
const {isDocked} = await import("../src/domain/docks.js");
const {useRunGroup} = await import("../src/composables/runGroup.js");
const {receiptParts, receiptWords} = await import("../src/domain/receipt.js");
const {threadTurns} = await import("../src/domain/thread.js");

choose("main");
let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

async function mounted(component, props, scope = null) {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(component, props)});
    if (scope) app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    return host;
}

const source = (path) => readFileSync(path, "utf8");
// the cards and the row fold one into the other out and then in, each step waiting a frame where the test page has no transitions: wait
// until no fold transition is left on the page, a second at most
const folds = async () => {
    const moving = () => document.querySelector(".folding, [class*='runs-fold-'], [class*='runs-unfold-']");
    for (let waited = 0; waited < 1000 && (waited < 40 || moving()); waited += 20) await new Promise((done) => setTimeout(done, 20));
    await flush();
};
const now = () => Date.now() / 1000;
const watched = (id, data = {}) => ({
    table: "messages",
    id,
    author: "system",
    text: `Running the tests ${id}`,
    data: {kind: "card", output: id, line: "pytest -q", lines: [], fraction: 0.4, docked: true, ...data},
});

test("1. one design: every mark, card and dock folds with the one chevron, the second status and the old chevron are gone, and a card acts from its line alone", async () => {
    expect(MARK_ICONS.fold).toBe('<polyline points="4,6 8,10 12,6"/>');
    expect(MARK_ICONS.chevron).toBeUndefined();
    expect(existsSync("src/kit/ChatMarkStatus.vue")).toBe(false);
    for (const path of [
        "src/kit/ChatMark.vue",
        "src/chat/GrowingCard.vue",
        "src/chat/WatchDock.vue",
        "src/chat/RowDock.vue",
        "src/chat/DockGroup.vue",
        "src/chat/TaskLine.vue",
    ]) {
        expect(source(path)).toContain("<FoldSign");
    }
    const host = await mounted(GrowingCard, {
        title: "Report from Lady Lovelace",
        text: "Done.",
        person: "Lady Lovelace",
        action: "Open the worker",
    });
    expect(host.querySelector(".growing-card-action")).toBeNull();
    expect(host.querySelector(".growing-card-top .mact").getAttribute("aria-label")).toBe("Open the worker");
});

test("2. a mark's quick action opens what it is about, shown by its weight, and in words once the mark is open", async () => {
    const acts = vi.fn();
    const host = await mounted(ChatMark, {
        mark: {label: "Check lint passed", tone: "good", detail: "all clean", action: "Open the check"},
        onAct: acts,
    });
    const action = host.querySelector(".mact");
    expect([action.getAttribute("aria-label"), action.dataset.tip, host.querySelector(".mact-word")]).toEqual([
        "Open the check",
        "Open the check",
        null,
    ]);
    action.click();
    await flush();
    expect(acts).toHaveBeenCalledTimes(1);
    expect(host.querySelector(".mark").classList.contains("open")).toBe(false);
    host.querySelector(".mark").click();
    await flush();
    expect(host.querySelector(".mark").classList.contains("open")).toBe(true);
    expect(host.querySelector(".mact-word").textContent).toBe("Open the check");
    expect(acts).toHaveBeenCalledTimes(1);
    app.unmount();
    const scope = {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}};
    const created = {
        table: "messages",
        id: 3,
        created_at: new Date(1e4).toISOString(),
        author: "system",
        text: "Task 12 started",
        files: [],
        comments_on: [],
        data: {kind: "card", detail: "", lines: [], row: "tasks:12"},
    };
    const card = await mounted(Turn, {turn: threadTurns([created], []).turns[0]}, scope);
    expect(card.querySelector(".mact").getAttribute("aria-label")).toBe("Open the task");
    const css = source("src/kit/ChatMark.vue");
    expect(css).toMatch(/\.mark \.mact \{\s*opacity: 0;/);
    expect(css).toMatch(/\.mark\.w-process \.mact \{\s*margin-left: 11px;\s*color: var\(--text-4\);\s*opacity: 1;/);
    expect(css).toMatch(
        /\.mark\.w-attention \.mact:hover \{\s*background: color-mix\(in srgb, var\(--mark, var\(--danger\)\) 18%, transparent\);/
    );
    expect(source("src/kit/MarkAction.vue")).toMatch(/transition-delay: 0\.45s;/);
});

test("3. a running check's mark stops from a button beside it, which asks first with Keep it running focused, then says Stopping, then is a grey quiet line", async () => {
    const act = vi.fn().mockResolvedValue({});
    const scope = {
        env: "",
        api: {act},
        rows: (table) => (table === "checks" ? [{id: 4, title: "types"}] : []),
        loaded: () => true,
        holding: () => {},
        earlier: () => {},
    };
    const running = {
        table: "messages",
        id: 5,
        created_at: new Date(1e4).toISOString(),
        author: "system",
        text: "Check types running",
        files: [],
        comments_on: [],
        data: {kind: "card", check: 4, row: "checks:4", began_at: now(), figure: "3 of 5", detail: "", lines: []},
    };
    const host = await mounted(Turn, {turn: threadTurns([running], []).turns[0]}, scope);
    expect(host.querySelector(".mark").classList.contains("w-process")).toBe(true);
    host.querySelector(".mark-row .run-stop-button").click();
    await flush();
    const ask = document.querySelector(".run-stop-ask");
    expect(ask.querySelector(".run-stop-question").textContent).toBe("Stop the check types now?");
    expect(ask.querySelector(".run-stop-note").textContent).toBe("The run is killed at once. It cannot be resumed or undone.");
    expect(document.activeElement.textContent.trim()).toBe("Keep it running");
    window.dispatchEvent(new KeyboardEvent("keydown", {key: "Escape"}));
    await flush();
    expect(document.querySelector(".run-stop-ask")).toBeNull();
    host.querySelector(".mark-row .run-stop-button").click();
    await flush();
    [...document.querySelectorAll(".run-stop-ask button")].find((b) => b.textContent.trim() === "Stop the run").click();
    await flush();
    expect(act).toHaveBeenCalledWith("checks", 4, "stop");
    expect(host.querySelector(".mark").classList.contains("stopping")).toBe(true);
    expect(host.querySelector(".mark .status").textContent).toContain("Stopping");
    expect(host.querySelector(".run-stop")).toBeNull();
    await new Promise((done) => setTimeout(done, 800));
    await flush();
    const mark = host.querySelector(".mark");
    expect(mark.querySelector(".head").textContent).toContain("Check types stopped by you at 3 of 5");
    expect([mark.classList.contains("w-event"), mark.classList.contains("failed"), Boolean(mark.querySelector(".sign.stopped"))]).toEqual([
        true,
        false,
        true,
    ]);
    expect(mark.getAttribute("style")).toContain("--mark: var(--text-3)");
    expect(source("src/chat/RunStop.vue")).toMatch(
        /\.run-stop-ask \{\s*position: fixed;\s*z-index: 40;\s*width: 276px;\s*padding: 11px 12px 10px;/
    );
    expect(source("src/tokens.css")).toContain("--on-danger: #17181b;");
    expect(source("src/light.css")).toContain("--on-danger: #ffffff;");
});

test("4. the chevron points down while folded and turns 180 degrees once open, on a mark only on hover or once open", async () => {
    const sign = await mounted(FoldSign, {open: false});
    expect(sign.querySelector(".fold svg").innerHTML).toBe('<polyline points="4,6 8,10 12,6"></polyline>');
    app.unmount();
    const host = await mounted(ChatMark, {mark: {label: "Lint found a problem", detail: "a long method"}});
    expect(host.querySelector(".fold").classList.contains("open")).toBe(false);
    expect(host.querySelector(".top").getAttribute("aria-expanded")).toBe("false");
    host.querySelector(".mark").click();
    await flush();
    expect(host.querySelector(".fold").classList.contains("open")).toBe(true);
    app.unmount();
    const card = await mounted(GrowingCard, {title: "Message to Lady Lovelace", text: "Look at this."});
    card.querySelector(".growing-card").click();
    await flush();
    expect(card.querySelector(".growing-card .fold").classList.contains("open")).toBe(true);
    expect(source("src/kit/FoldSign.vue")).toMatch(/\.fold\.open \{\s*transform: rotate\(180deg\);/);
    expect(source("src/kit/FoldSign.vue")).toMatch(/transform 0\.3s var\(--ease\)/);
    expect(source("src/kit/ChatMark.vue")).toMatch(/\.mark \.fold \{\s*width: 10px;\s*height: 10px;\s*margin-left: 0;\s*opacity: 0;/);
});

test("5a. the closing line lies inside the docked card along its top edge, its full width", async () => {
    const docked = reactive(watched(8, {auto_docked: true, undock_at: now() + 3, ending: "finished", outcome: "passed"}));
    const host = await mounted(WatchDock, {message: docked});
    expect(host.querySelector(".chat-dock-card > .dock-leave")).not.toBeNull();
    expect(source("src/chat/DockLeave.vue")).toMatch(/\.dock-leave \{\s*position: absolute;\s*top: 0;\s*right: 0;\s*left: 0;/);
});

test("5. a card the journal docked by itself runs a line down its top edge before it closes, held while pointed at, and kept by Keep", async () => {
    const act = vi.spyOn(api, "act").mockResolvedValue({});
    const ends = now() + 3;
    const docked = reactive(watched(7, {auto_docked: true, undock_at: ends, ending: "finished", outcome: "passed"}));
    const host = await mounted(WatchDock, {message: docked});
    const line = host.querySelector(".dock-leave i");
    expect(Number.parseFloat(line.style.animationDelay)).toBeCloseTo(-2, 0);
    expect(line.style.animationDuration).toBe("5s");
    host.querySelector(".chat-dock").dispatchEvent(new Event("pointerenter"));
    expect(docked.data.held_at).toBeGreaterThan(0);
    expect(isDocked(docked, ends + 60)).toBe(true);
    host.querySelector(".chat-dock").dispatchEvent(new Event("pointerleave"));
    expect(docked.data.held_at).toBeUndefined();
    expect(docked.data.undock_at).toBeGreaterThanOrEqual(ends);
    expect(isDocked(docked, ends + 60)).toBe(false);
    const keep = host.querySelector(".watch-dock-keep");
    expect([keep.textContent.trim(), keep.dataset.tip]).toEqual(["Keep", "Keep this card here until you close it"]);
    keep.click();
    await flush();
    expect(act).toHaveBeenCalledWith("messages", 7, "dock");
    expect(docked.data.auto_docked).toBe(false);
    expect(source("src/chat/DockLeave.vue")).toMatch(/top: 0;\s*right: 0;\s*left: 0;/);
    expect(source("src/kit/ChatDock.vue")).toMatch(/\.chat-dock\.timed\.dock-leave-to \.chat-dock-card \{\s*transform: translateY\(6px\);/);
});

test("6. from three docked runs they share one row of chips until one is left; its title opens every card, a chip opens its own and folds the others", async () => {
    const runs = ref([watched(1)]);
    const grouped = useRunGroup(runs);
    const seen = [];
    for (const count of [1, 2, 3, 2, 1]) {
        runs.value = [1, 2, 3].slice(0, count).map((id) => watched(id));
        await nextTick();
        seen.push(grouped.value);
    }
    expect(seen).toEqual([false, false, true, true, false]);
    const act = vi.spyOn(api, "act").mockResolvedValue({});
    const three = [watched(1), watched(2, {auto_docked: true}), watched(3)];
    const host = await mounted(DockGroup, {runs: three, grouped: true});
    expect(host.querySelector(".dock-group-toggle").textContent.trim()).toBe("3 runs");
    expect(host.querySelectorAll(".run-chip").length).toBe(3);
    expect(host.querySelector(".run-chip").getAttribute("aria-label")).toBe("Running the tests 1; show its card");
    host.querySelectorAll(".run-chip")[1].click();
    await folds();
    const folded = [...host.querySelectorAll(".chat-dock-body")].map((body) => body.classList.contains("folded"));
    expect(folded).toEqual([true, false, true]);
    expect(act).toHaveBeenCalledWith("messages", 2, "dock");
    expect(host.querySelector(".dock-group-head").textContent.trim()).toBe("3 runs");
    host.querySelector(".dock-group-head .dock-group-toggle").click();
    await folds();
    expect(host.querySelectorAll(".run-chip").length).toBe(3);
    const chip = source("src/chat/RunChip.vue");
    expect(chip).toMatch(/max-width: 190px;\s*height: 24px;/);
    expect(chip).toMatch(/@container \(max-width: 100px\) \{\s*\.run-chip-name \{\s*display: none;/);
    expect(chip).toMatch(/@container \(max-width: 64px\) \{\s*\.run-chip-figure \{\s*display: none;/);
});

test("7. the line under the user's message keeps up to three tasks as chips, and from four a count that opens the created and the linked under their labels", async () => {
    const tasks = (verb, ids) => `${verb} ${ids.map((id) => `task ${id}`).join(", ")} from your message`;
    expect(receiptWords(receiptParts(tasks("Created", [1, 2, 3, 4])))).toBe("4 tasks created from your message");
    expect(receiptWords(receiptParts(tasks("Linked", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])))).toBe("10 linked tasks");
    expect(receiptWords(receiptParts(`${tasks("Created", [1, 2, 3])}; ${tasks("Linked", [4, 5, 6, 7, 8, 9, 10])}`))).toBe(
        "10 tasks from your message: 3 created, 7 linked"
    );
    const few = await mounted(TaskLine, {receipt: tasks("Created", [1, 2])});
    expect([few.querySelector(".task-line-count"), few.querySelector(".task-line-few").textContent.trim()]).toEqual([
        null,
        "Created from your message: task 1 task 2",
    ]);
    app.unmount();
    const three = await mounted(TaskLine, {receipt: tasks("Created", [1, 2, 3])});
    expect([
        three.querySelector(".task-line").classList.contains("three"),
        three.querySelector(".task-line").classList.contains("many"),
        Boolean(three.querySelector(".task-line-count")),
    ]).toEqual([true, false, true]);
    app.unmount();
    const many = await mounted(TaskLine, {receipt: `${tasks("Created", [1, 2])}; ${tasks("Linked", [3, 4])}`});
    expect(many.querySelector(".task-line").classList.contains("many")).toBe(true);
    many.querySelector(".task-line-count").click();
    await flush();
    const labels = [...many.querySelectorAll(".task-line-label")].map((label) => label.textContent);
    expect(labels).toEqual(["Created from your message", "Linked: the agent's reply named them"]);
    expect(many.querySelectorAll(".task-line-row").length).toBe(4);
    const css = source("src/chat/TaskLine.vue");
    expect(css).toMatch(/width: 300px;\s*max-width: calc\(100vw - 24px\);\s*max-height: 260px;/);
    expect(css).toMatch(/padding: 0\.05em 0\.35em 0\.05em 0\.45em;/);
});

test("8. docked runs fold into their row and out of it with a transition, the dock's height easing along", async () => {
    const props = reactive({runs: [watched(1), watched(2), watched(3)], grouped: false});
    const host = await mounted(DockGroup, props);
    expect([host.querySelectorAll(".dock-group-cards .chat-dock").length, host.querySelector(".run-chip")]).toEqual([3, null]);
    props.grouped = true;
    await nextTick();
    expect(host.querySelector(".dock-group-cards").classList.contains("runs-fold-leave-active")).toBe(true);
    expect(host.querySelector(".dock-group").classList.contains("folding")).toBe(true);
    await folds();
    expect(host.querySelectorAll(".run-chip").length).toBe(3);
    expect(host.querySelector(".dock-group").classList.contains("folding")).toBe(false);
    host.querySelector(".dock-group-toggle").click();
    await nextTick();
    expect(host.querySelector(".chat-dock").classList.contains("runs-unfold-leave-active")).toBe(true);
    await folds();
    expect(host.querySelectorAll(".dock-group-cards .chat-dock").length).toBe(3);
    const css = source("src/chat/DockGroup.vue");
    expect(css).toMatch(/\.dock-group \{\s*transition: height 0\.3s var\(--ease\);/);
    expect(css).toMatch(/transform 0\.15s var\(--ease\),\s*opacity 0\.15s ease;/);
    expect(source("src/chat/Thread.vue")).toContain('<DockGroup :runs="runDocks" :grouped="grouped" :folded="short || !planOpen" />');
});

test("9. three runs the journal docked by itself, grouped and all ended, undock as a single run does, even with the pointer on a card as they fold", async () => {
    const {dockedRows} = await import("../src/domain/docks.js");
    const ends = now() + 3;
    const ended = (id) => reactive(watched(id, {auto_docked: true, ending: "finished", outcome: "passed", undock_at: ends}));
    const runs = [ended(1), ended(2), ended(3)];
    const props = reactive({runs: dockedRows(runs, now()), grouped: false});
    const host = await mounted(DockGroup, props);
    expect(props.runs).toHaveLength(3);
    host.querySelectorAll(".dock-group-cards .chat-dock")[1].dispatchEvent(new Event("pointerenter"));
    expect(runs[1].data.held_at).toBeGreaterThan(0);
    props.grouped = true;
    await folds();
    expect(host.querySelectorAll(".run-chip")).toHaveLength(3);
    expect(runs.map((run) => run.data.held_at)).toEqual([undefined, undefined, undefined]);
    props.runs = dockedRows(runs, ends + 6);
    await folds();
    expect(props.runs).toEqual([]);
    expect(host.querySelector(".dock-group .chat-dock")).toBeNull();
});

test("10. a running command's mark shows its stop beside it while pointed at, and pressing it asks the journal to stop the output", async () => {
    const act = vi.fn().mockResolvedValue({});
    const scope = {env: "", api: {act, readOutput: vi.fn().mockResolvedValue({lines: [], start: 0, next: 0})}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}};
    const running = {table: "messages", id: 8, created_at: new Date(1e4).toISOString(), author: "system", text: "Running npm run build", files: [], comments_on: [], data: {kind: "card", output: 12, line: "npm run build", began_at: now(), detail: "", lines: []}};
    const host = await mounted(Turn, {turn: threadTurns([running], []).turns[0]}, scope);
    expect(source("src/chat/Turn.vue")).toMatch(/\.mark-row:hover \.run-stop,\s*\.mark-row:focus-within \.run-stop \{\s*opacity: 1;/);
    host.querySelector(".mark-row .run-stop-button").click();
    await flush();
    expect(document.querySelector(".run-stop-question").textContent).toBe("Stop the command npm run build now?");
    [...document.querySelectorAll(".run-stop-ask button")].find((b) => b.textContent.trim() === "Stop the run").click();
    await flush();
    expect(act).toHaveBeenCalledWith("outputs", 12, "stop");
    expect(host.querySelector(".mark .status").textContent).toContain("Stopping");
});
