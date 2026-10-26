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

test("a worker's report card is one line with the worker's initial, saying what it is and on which task, with no state or time of its own, and opens in place to the whole report", async () => {
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(ReportCard, {worker: "Mr. Bertillon", workerId: 1126, messageId: 9, taskId: 3318, text: "the reminder test drains its queue first"})});
    app.mount(host);
    await flush();
    expect(host.querySelector(".growing-card-title").textContent).toBe("Report from worker 1126, Mr. Bertillon, on task 3318");
    expect(host.querySelector(".growing-card-avatar").textContent.trim()).toBe("B");
    const wrap = host.querySelector(".growing-card-wrap");
    expect(wrap.classList.contains("open")).toBe(false);
    host.querySelector(".growing-card").click();
    await flush();
    expect(wrap.classList.contains("open")).toBe(true);
    expect(wrap.contains(host.querySelector(".growing-card-text"))).toBe(true);
    expect(host.querySelectorAll(".growing-card-body").length).toBe(1);
    expect(host.querySelector(".growing-card-text").textContent).toBe("the reminder test drains its queue first");
    host.querySelector(".growing-card").click();
    await flush();
    expect(wrap.classList.contains("open")).toBe(false);
});
