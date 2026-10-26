import {createApp, h} from "vue";
import {afterEach, describe, expect, test} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {default: TurnFromMain} = await import("../src/chat/TurnFromMain.vue");

let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

async function mounted(data) {
    const root = document.createElement("div");
    document.body.appendChild(root);
    app = createApp({render: () => h(TurnFromMain, {data, text: "the parser is done"})});
    app.mount(root);
    await flush();
    return root.querySelector(".growing-card-wrap");
}

describe("a message between agents in the chat", () => {
    test("one another agent sent comes in on the right, its icon at the far right and its title against it", async () => {
        const card = await mounted({peer: "agent-journal-b6"});
        expect(card.classList.contains("incoming")).toBe(true);
        expect(card.querySelector(".growing-card-title").textContent).toBe("Message from agent-journal-b6");
    });

    test("one this agent sent stays on the left", async () => {
        const card = await mounted({sent_to: "agent-journal"});
        expect(card.classList.contains("incoming")).toBe(false);
        expect(card.querySelector(".growing-card-title").textContent).toBe("Message sent to agent-journal");
    });
});
