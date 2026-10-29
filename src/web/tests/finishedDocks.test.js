import {computed, createApp, h, ref} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import WatchDock from "../src/chat/WatchDock.vue";
import {useSharedNow} from "../src/composables/now.js";
import {dockedRows, keptRuns} from "../src/domain/docks.js";
import {flush} from "./flush.js";

let app;
afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
    vi.useRealTimers();
});

const run = (id, data = {}) => ({
    id, table: "messages", text: `Run ${id}`, created_at: new Date().toISOString(),
    data: {card_type: "process", process: "output", output: id, docked: true, active: true, state: "running", lines: [], ...data},
});

function mountRuns(messages) {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({setup() {
        const now = useSharedNow();
        const runs = computed(() => keptRuns(dockedRows(messages.value, now.value)));
        return () => h("div", runs.value.map((message) => h(WatchDock, {key: message.id, message})));
    }});
    app.provide("scope", {env: "", api: {}});
    app.directive("tip", {});
    app.mount(host);
    return host;
}

test("a finished run stays for five seconds even when six other runs are docked", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-28T12:00:00Z"));
    const messages = ref([run(1, {active: false, ending: "completed", state: "completed", undock_at: Date.now() / 1000 + 5}),
        ...Array.from({length: 6}, (_, index) => run(index + 2))]);
    const host = mountRuns(messages);
    await flush();
    expect(host.querySelectorAll(".watch-dock-title")).toHaveLength(7);
    await vi.advanceTimersByTimeAsync(4999);
    expect(host.querySelectorAll(".watch-dock-title")).toHaveLength(7);
    await vi.advanceTimersByTimeAsync(1);
    expect([...host.querySelectorAll(".watch-dock-title")].map((node) => node.textContent)).toEqual(
        ["Run 2", "Run 3", "Run 4", "Run 5", "Run 6", "Run 7"]);
});

test.each([{pinned: true}, {undock_at: Date.now() / 1000 + 60}])("a protected finished run survives the dock limit: %j", async (protection) => {
    const host = mountRuns(ref([run(1, {active: false, ending: "completed", state: "completed", ...protection}),
        ...Array.from({length: 6}, (_, index) => run(index + 2))]));
    await flush();
    expect(host.querySelectorAll(".watch-dock-title")).toHaveLength(7);
});

test("the pin becomes filled and says Unpin when a run is pinned", async () => {
    const messages = ref([run(1)]);
    const host = mountRuns(messages);
    await flush();
    const button = host.querySelector(".watch-dock-pin");
    expect(button.getAttribute("aria-pressed")).toBe("false");
    const icon = button.querySelector("svg");
    expect(icon.style.fill || icon.getAttribute("fill")).toBe("none");
    messages.value[0].data.pinned = true;
    await flush();
    expect(button.getAttribute("aria-pressed")).toBe("true");
    expect(button.title).toMatch(/^Unpin:/);
    expect((icon.style.fill || icon.getAttribute("fill")).toLowerCase()).toBe("currentcolor");
});
