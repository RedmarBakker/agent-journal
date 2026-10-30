import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

vi.mock("../src/kit/MenuPanel.vue", () => ({default: {props: ["anchor"], template: "<div class='menu-panel'><slot /></div>"}}));

const {default: PlanAgentChats} = await import("../src/chat/PlanAgentChats.vue");
const {store} = await import("../src/state/store.js");
const {choose, environment} = await import("../src/state/environment.js");
const {route} = await import("../src/route.js");
const {remembered} = await import("../src/platform/storage.js");

const plans = [
    {table: "plans", id: 3, title: "Floors", mode: "solo", phase: "in_progress", state: "started", chat: "plan-3"},
    {table: "plans", id: 4, title: "Roof", mode: "organization", phase: "planned", state: "ready", chat: "plan-4"},
    {table: "plans", id: 5, title: "Finished plan", mode: "solo", state: "done", updated_at: "2026-01-01T00:00:00Z", chat: "plan-5"},
];

let app = null;
let host = null;

beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    location.hash = "#/";
    store.organization = {plans};
    store.summary = {environments: [
        {environment: {id: 1, key: "main-key", name: "main"}, messages: 1},
        {environment: {id: 3, key: "plan-3-key", parent_key: "main-key", name: "plan-3", generated_for: "plan"}, messages: 2},
        {environment: {id: 4, key: "plan-4-key", parent_key: "main-key", name: "plan-4", generated_for: "plan"}, messages: 0},
    ]};
    store.spec = {environment: "main"};
    store.rows.environments = [];
    choose("plan-3");
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

async function mount() {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(PlanAgentChats)});
    app.mount(host);
    await nextTick();
}

test("the chat dropdown searches open Plan agents, marks unread chats, links back to the plan, and remembers the choice", async () => {
    await mount();

    const heading = host.querySelector(".plan-agent-chat-heading");
    expect(heading.textContent).toContain("Plan 3 · Floors");
    expect(heading.textContent).toContain("Solo mode");
    expect(heading.textContent).toContain("Phase: In progress");
    expect(heading.getAttribute("href")).toContain("plans/3");

    host.querySelector(".plan-agent-chat-toggle").click();
    await nextTick();
    const options = [...host.querySelectorAll(".plan-agent-chat-option")];
    expect(options.map((option) => option.querySelector(".plan-agent-chat-option-title").textContent)).toEqual(["Main agent", "Floors", "Roof"]);
    expect(options.find((option) => option.textContent.includes("Floors")).querySelector('[aria-label="Unread messages"]')).not.toBeNull();
    expect(host.textContent).not.toContain("Finished plan");

    const search = host.querySelector('input[type="search"]');
    search.value = "roof";
    search.dispatchEvent(new Event("input", {bubbles: true}));
    await nextTick();
    expect([...host.querySelectorAll(".plan-agent-chat-option .plan-agent-chat-option-title")].map((title) => title.textContent)).toEqual(["Roof"]);

    host.querySelector(".plan-agent-chat-option").click();
    await nextTick();
    expect(environment.value).toBe("plan-4");
    expect(route.value.env).toBe("plan-4");
    expect(route.value.page).toBe("chat");
    expect(remembered("journal.environment", "")).toBe("plan-4");
});

test("choosing the main chat returns from a plan page to the Chat page", async () => {
    choose("main");
    location.hash = "#/plans/3";
    await new Promise((settle) => setTimeout(settle, 0));
    await mount();

    host.querySelector(".plan-agent-chat-toggle").click();
    await nextTick();
    host.querySelector(".plan-agent-chat-option").click();
    await new Promise((settle) => setTimeout(settle, 0));
    await nextTick();

    expect(route.value.env).toBe("main");
    expect(route.value.page).toBe("chat");
});
