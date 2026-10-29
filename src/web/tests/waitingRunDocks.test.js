import {createApp, h, ref} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import WatchDock from "../src/chat/WatchDock.vue";
import {useDockedCards} from "../src/composables/dockedCards.js";
import {dockedRows} from "../src/domain/docks.js";
import {api, ApiClient} from "../src/api/client.js";
import {flush} from "./flush.js";

let app;
afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
    vi.useRealTimers();
    vi.restoreAllMocks();
});

test("the docked cards are read apart from the chat's pages, under a request key of their own", async () => {
    const client = new ApiClient({env: () => "main"});
    const get = vi.spyOn(client, "get").mockResolvedValue({});
    await client.list("messages", {limit: 50});
    await client.list("messages", {docked: true});
    await client.chat("worker-session", {docked: true});
    const calls = get.mock.calls;
    expect(calls[1][0]).toContain("docked=1");
    expect(calls[2][0]).toContain("docked=1");
    expect(calls[0][1]).not.toBe(calls[1][1]);
    expect(calls[2][1]).toContain("docked");
});

const card = (waiting) => ({
    id: 1,
    table: "messages",
    text: "Running the build",
    created_at: new Date().toISOString(),
    data: {card_type: "process", process: "output", output: 12, docked: true, active: true, waiting_run: waiting, state: "running", lines: []},
});

test.each([true, false])("a docked run offers its close button only when no agent waits for it: waiting=%s", async (waiting) => {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(WatchDock, {message: card(waiting)})});
    app.provide("scope", {env: "", api: {}});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    expect(host.querySelector(".watch-dock-title").textContent).toBe("Running the build");
    expect(Boolean(host.querySelector('[aria-label="Take the watched output down from above the chat"]'))).toBe(!waiting);
});

test("a card docked long ago is drawn though its message is older than the chat's newest page", async () => {
    vi.useFakeTimers();
    const old = card(true);
    const list = vi.spyOn(api, "list").mockResolvedValue({rows: [old], is_last_page: true});
    const messages = ref([{id: 100, text: "The latest message", data: {}}]);
    let docks;
    app = createApp({
        setup() {
            docks = useDockedCards(messages);
            return () => h("div");
        },
    });
    app.provide("scope", {env: "", api});
    app.mount(document.createElement("div"));
    await vi.advanceTimersByTimeAsync(1000);
    expect(list).toHaveBeenCalledWith("messages", expect.objectContaining({docked: true}));
    expect(dockedRows(docks.value).map((message) => message.id)).toEqual([1]);
    list.mockResolvedValue({rows: [{...old, data: {...old.data, waiting_run: false}}], is_last_page: true});
    await vi.advanceTimersByTimeAsync(3000);
    expect(docks.value.find((message) => message.id === 1).data.waiting_run).toBe(false);
});
