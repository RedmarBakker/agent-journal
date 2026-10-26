import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

vi.mock("../src/route.js", async (original) => ({...(await original()), peek: vi.fn()}));

const moment = (id, text, row) => ({id, text, created_at: new Date().toISOString(), data: {kind: "card", row, detail: "", summary: ""}});

test("the workers dropdown has a second tab, Recent activity, with the workers' moments newest first, each a card", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: WorkerList} = await import("../src/chat/WorkerList.vue");
    const moments = [moment(9, "Worker 2, Ada: its tests passed", ""), moment(4, "Worker 2, Ada: sent its next job", "workers:2")];
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(WorkerList, {rows: [], moments})});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const tabs = [...host.querySelectorAll(".workers-tabs .segmented-option")];
    expect(tabs.map((tab) => tab.textContent.trim())).toEqual(["Workers", "Recent activity"]);
    expect(host.querySelectorAll(".agent").length).toBe(0);
    tabs[1].click();
    await nextTick();
    expect([...host.querySelectorAll(".agent-name")].map((name) => name.textContent)).toEqual(["Worker 2, Ada: its tests passed", "Worker 2, Ada: sent its next job"]);
    expect(host.querySelector(".workers-testing")).toBeNull();
    app.unmount();
    host.remove();
});
