import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

vi.mock("../src/pages/Home.vue", () => ({default: {template: "<section data-main-chat />"}}));

const {default: AppPages} = await import("../src/AppPages.vue");
const {ApiClient} = await import("../src/api/client.js");
const {store} = await import("../src/state/store.js");
const {PAGES} = await import("../src/route.js");
const {pageTitle} = await import("../src/composables/pageTitle.js");

let app = null;
let host = null;

beforeEach(() => {
    location.hash = "#/chat";
    store.people = {hosted: false};
    store.settings = {plans: {plan_agents: false}};
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    vi.restoreAllMocks();
    document.body.innerHTML = "";
});

test("the Chat route opens the existing main chat and is named Chat", async () => {
    expect(PAGES).toContain("chat");
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(AppPages, {page: "chat"})});
    app.mount(host);
    await new Promise((resolve) => setTimeout(resolve, 0));
    await nextTick();

    expect(host.querySelector("[data-main-chat]")).not.toBeNull();
    expect(pageTitle.value).toBe("Chat");
});

test("an environment link without a page opens its Chat page", () => {
    const api = new ApiClient({env: () => "main"});

    expect(api.page("plan-3")).toContain("env=plan-3");
    expect(api.page("plan-3")).toContain("#/chat");
});
