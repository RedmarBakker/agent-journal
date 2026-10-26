import {createApp, h, nextTick, reactive} from "vue";
import {expect, test, vi} from "vitest";

vi.mock("../src/route.js", async (original) => ({...(await original()), peek: vi.fn()}));
import {threadTurns} from "../src/domain/thread.js";

const card = (status) => ({table: "messages", id: 7, created_at: new Date(1e4).toISOString(), creator: "agent:1", author: "system", agent_role: "main", text: "Created document 3: The cart", files: [], comments_on: [], idempotency: "", data: {kind: "made", made_type: "docs", row: "docs:3", status}});

test("a document's chat mark carries its title and says it is being written until it is ready", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: MadeCard} = await import("../src/chat/MadeCard.vue");
    const held = reactive({made: threadTurns([card("Being written")], []).turns[0].made});
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(MadeCard, {made: held.made})});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".thread-made").textContent).toContain("Created document 3: The cart");
    expect(host.querySelector(".settled").textContent).toBe("Being written");
    held.made = threadTurns([card("Ready")], []).turns[0].made;
    await nextTick();
    expect(host.querySelector(".settled")).toBe(null);
    app.unmount();
    host.remove();
});
