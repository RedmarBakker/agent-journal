import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import {threadTurns} from "../src/domain/thread.js";
import {fromMainAgent} from "../src/domain/transcript.js";

Object.defineProperty(HTMLElement.prototype, "scrollHeight", {configurable: true, get: () => 2000});
globalThis.ResizeObserver = class {
    constructor(onResize) {
        this.onResize = onResize;
    }
    observe() {
        this.onResize();
    }
    disconnect() {}
};

const at = (seconds) => new Date(seconds * 1000).toISOString();
const card = (id, seconds, data, text) => ({table: "messages", id, created_at: at(seconds), author: "system", text, files: [], data, comments_on: [], idempotency: "", reply_target: null});
const messages = [
    card(1, 10, {kind: "peer", peer: "Coco"}, "the report is ready"),
    card(2, 20, {kind: "peer", sent_to: "Coco"}, "thanks, merging now"),
    card(3, 30, {kind: "peer", sent_to: "Coco", failure: "the socket is stale"}, "thanks, merging now"),
];
const scope = {env: "", api: {}, rows: () => messages, loaded: () => true, holding: () => {}, earlier: () => {}};

async function drawn(turn) {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: TurnMessage} = await import("../src/chat/TurnMessage.vue");
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(TurnMessage, {turn})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    await new Promise((r) => requestAnimationFrame(r));
    await nextTick();
    const card = host.querySelector(".growing-card-wrap");
    const collapsed = card.classList.contains("open");
    host.querySelector(".growing-card").click();
    await nextTick();
    const shown = {
        mine: host.querySelector(".thread-turn").classList.contains("mine"),
        head: host.querySelector(".growing-card-title").textContent,
        time: host.querySelector(".growing-card-time")?.textContent,
        collapsed: !collapsed,
        expanded: card.classList.contains("open") && host.querySelector(".growing-card-text").textContent === turn.text,
        bubble: host.querySelector(".thread-bubble").style.display !== "none",
        header: Boolean(host.querySelector(".thread-meta")),
        red: card.classList.contains("bad"),
    };
    app.unmount();
    host.remove();
    return shown;
}

test("what the agent sends to another agent sits on the agent's side and names who it went to", async () => {
    const [, sent] = threadTurns(messages, []).turns;
    const shown = await drawn(sent);
    expect(shown.mine).toBe(false);
    expect(shown.head).toContain("Message sent to Coco");
});

test("a send that failed says so in red with the tool's reason, never as sent", async () => {
    const [, sent, failed] = threadTurns(messages, []).turns;
    const shown = await drawn(failed);
    expect(shown.head).toContain("Message not sent to Coco: the socket is stale");
    expect(shown.red).toBe(true);
    expect((await drawn(sent)).red).toBe(false);
});

test("what the agent receives from another agent sits on the agents' side, left, and names who sent it; the right side is the user's alone", async () => {
    const [received] = threadTurns(messages, []).turns;
    const [fromMain] = fromMainAgent([{type: "line", who: "agent", data: {}, kind: "message", text: "hi", key: "line:1", time: 1}, {type: "line", who: "user", data: {}, kind: "message", text: "brief", key: "line:2", time: 2}]).slice(1);
    const [peer, main] = [await drawn(received), await drawn(fromMain)];
    expect(peer.mine).toBe(false);
    expect(peer.head).toContain("Message from Coco");
    expect(main.mine).toBe(false);
    expect(main.head).toContain("Message from the main agent");
});

test("a message to or from another agent is a one-line card with its time, never a bubble, and grows to its whole text on a click", async () => {
    const [received, sent] = threadTurns(messages, []).turns;
    for (const shown of [await drawn(received), await drawn(sent)]) {
        expect(shown.collapsed).toBe(true);
        expect(shown.expanded).toBe(true);
        expect(shown.bubble).toBe(false);
        expect(shown.time).toBeTruthy();
        expect(shown.header).toBe(false);
    }
});

test("a message to or from another agent offers Comment, React and Copy, and Comment quotes the card's title", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: TurnMessage} = await import("../src/chat/TurnMessage.vue");
    const [, sent] = threadTurns(messages, []).turns;
    const replies = [];
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(TurnMessage, {turn: sent, onReply: (quote) => replies.push(quote)})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const tools = [...host.querySelectorAll(".from-main-card .thread-tool")].map((button) => button.textContent.trim());
    expect(tools).toEqual(["React", "Comment", "Copy"]);
    [...host.querySelectorAll(".from-main-card .thread-tool")].find((button) => button.textContent.trim() === "Comment").click();
    expect(replies).toEqual([{text: "Message 2 to Coco", ref: sent.key}]);
    app.unmount();
    host.remove();
});
