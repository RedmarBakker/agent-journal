import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import {flush} from "./flush.js";

const {default: ReportCard} = await import("../src/chat/ReportCard.vue");

let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
});

test("a worker's report card is one line saying what it is and on which task, with no state or time of its own, and opens in place to the whole report", async () => {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(ReportCard, {worker: "Mr. Bertillon", workerId: 1126, messageId: 9, taskId: 3318, text: "the reminder test drains its queue first"})});
    app.mount(host);
    await flush();
    expect(host.querySelector(".report-card-worker").textContent).toBe("Report from worker 1126, Mr. Bertillon, on task 3318");
    expect(host.querySelector(".report-card").textContent.trim()).toBe("Report from worker 1126, Mr. Bertillon, on task 3318");
    expect(host.querySelector(".report-card-report")).toBeNull();
    host.querySelector(".report-card").click();
    await flush();
    expect(host.querySelector(".report-card-report").textContent).toBe("the reminder test drains its queue first");
    host.querySelector(".report-card").click();
    await flush();
    expect(host.querySelector(".report-card-report")).toBeNull();
});
