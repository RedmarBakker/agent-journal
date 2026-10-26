import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

vi.mock("../src/route.js", async (original) => ({...(await original()), peek: vi.fn()}));
import {threadTurns} from "../src/domain/thread.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const abstract = "The total adds the tax twice";

async function shown(component, props) {
    const host = document.createElement("div");
    document.body.append(host);
    createApp({render: () => h(component, props)}).mount(host);
    await nextTick();
    return host;
}

test("a report's chat card shows its abstract under its title, never the first bullet of its text", async () => {
    const {default: MadeCard} = await import("../src/chat/MadeCard.vue");
    const message = {table: "messages", id: 7, created_at: new Date(1e4).toISOString(), creator: "agent:1", author: "system", agent_role: "main", text: "Created report 2: The cart", files: [], comments_on: [], idempotency: "", data: {kind: "made", made_type: "reports", row: "reports:2", status: "Ready", summary: abstract}};
    const host = await shown(MadeCard, {made: threadTurns([message], []).turns[0].made});
    expect(host.querySelector(".thread-made-summary").textContent).toBe(abstract);
});

test("a report's docked card shows its abstract as its summary line", async () => {
    const {default: RowDock} = await import("../src/chat/RowDock.vue");
    const docked = {table: "messages", id: 41, author: "system", data: {kind: "docked", row: "reports:2", docked: true, heading: "Report 2: The cart", summary: abstract, status: "Ready", dock: {buttons: []}}};
    const host = await shown(RowDock, {message: docked});
    expect(host.querySelector(".row-dock-summary").textContent.trim()).toBe(abstract);
});
