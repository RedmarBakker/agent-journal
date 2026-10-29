import {createApp, h, nextTick} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import HubBoard from "../src/pages/HubBoard.vue";
import HubHome from "../src/pages/HubHome.vue";
import {pageOf} from "../src/sync/paging.js";

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("the Home task board pages its cards and can be reached by keyboard", async () => {
    const tasks = Array.from({length: pageOf("tasks") + 1}, (_, index) => ({
        table: "tasks",
        id: index + 1,
        title: `Home task ${index + 1}`,
        state: "open",
        environment_id: 1,
    }));
    const open = vi.fn();
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(HubBoard, {tasks, environments: [], onOpen: open})});
    app.mount(host);
    await nextTick();

    const board = host.querySelector("[data-hub-board]");
    expect(board.getAttribute("role")).toBe("region");
    expect(board.getAttribute("aria-label")).toBe("Home task board");
    expect(board.tabIndex).toBe(0);
    const lane = board.querySelector('[data-column="open"]');
    expect(lane.querySelectorAll(".card")).toHaveLength(pageOf("tasks"));
    expect(lane.querySelector(".paged-cards-controls span").textContent).toContain("1–50 of 51 tasks");
    const firstCard = lane.querySelector(".card");
    expect(firstCard.tagName).toBe("BUTTON");
    firstCard.focus();
    expect(document.activeElement).toBe(firstCard);
    firstCard.click();
    expect(open).toHaveBeenCalledWith(tasks[0]);

    lane.querySelector('button[aria-label="Next Open tasks page"]').click();
    await nextTick();
    expect(lane.querySelectorAll(".card")).toHaveLength(1);
    expect(lane.querySelector(".card").textContent).toContain("Home task 51");
});

test("the Home plan list pages plans and opens the selected card", async () => {
    const plans = Array.from({length: pageOf("plans") + 1}, (_, index) => ({id: index + 1, title: `Home plan ${index + 1}`}));
    const open = vi.fn();
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(HubHome, {hub: {name: "Home"}, plans, onOpen: open})});
    app.mount(host);
    await nextTick();

    const homePlans = host.querySelector("[data-hub-plans]");
    expect(homePlans.querySelectorAll(".line")).toHaveLength(pageOf("plans"));
    expect(homePlans.querySelector(".paged-cards-controls span").textContent).toContain("1–50 of 51 plans");
    homePlans.querySelector('button[aria-label="Next Home plans page"]').click();
    await nextTick();
    expect(homePlans.querySelectorAll(".line")).toHaveLength(1);
    expect(homePlans.querySelector(".line").textContent).toContain("Home plan 51");
    homePlans.querySelector(".line").click();
    expect(open).toHaveBeenCalledWith(plans[50]);
});
