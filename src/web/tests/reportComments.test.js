import {expect, test, vi} from "vitest";
import {createApp, h, inject, nextTick} from "vue";
import {api} from "../src/api/client.js";

const report = {table: "reports", id: 5, title: "Findings", body: "## One\n\nText", comment_count: 3, links: [], data: {}};
const old = {table: "messages", id: 901, author: "user", text: "An old comment the newest page no longer holds", comments_on: ["reports:5"], created_at: "2026-10-01T10:00:00+00:00", data: {}};

test("a report's page shows the count it was read with, and reads its comments only when the comment sidebar opens", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const read = vi.spyOn(api, "commentsOn").mockResolvedValue({rows: [old], is_last_page: true});
    const {default: DocumentPage} = await import("../src/resource/DocumentPage.vue");
    let talk = null;
    const Probe = {setup: () => ((talk = inject("talk")), () => h("span", {class: "probe-count"}, String(talk.count.value)))};
    const host = document.createElement("div");
    document.body.append(host);
    createApp({render: () => h(DocumentPage, {resource: report}, {default: () => h(Probe)})}).mount(host);
    await nextTick();
    expect(host.querySelector(".probe-count").textContent).toBe("3");
    expect(read).not.toHaveBeenCalled();
    talk.toggle();
    await new Promise((done) => setTimeout(done, 350));
    await nextTick();
    expect(read).toHaveBeenCalledTimes(1);
    expect(read).toHaveBeenCalledWith("reports:5");
    expect(host.querySelector(".document-aside").textContent).toContain("An old comment the newest page no longer holds");
    read.mockRestore();
});
