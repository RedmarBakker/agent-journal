import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const environments = [{id: 1, key: "main-key", name: "main", environment_type: "local", team_key: ""}];
const api = {
    env: () => "main",
    list: vi.fn(),
    entries: vi.fn(),
    organization: vi.fn(),
};
vi.mock("../src/api/client.js", () => ({api, onWrite: vi.fn()}));
vi.mock("../src/chat/outbox.js", () => ({onOutboxChange: vi.fn()}));
vi.mock("../src/platform/view.js", () => ({narrow: {value: false}}));
vi.mock("../src/layout/EnvStart.vue", () => ({default: {template: "<span />"}}));
vi.mock("../src/layout/NewEnvironment.vue", () => ({default: {template: "<span />"}}));

const {default: Sidebar} = await import("../src/layout/Sidebar.vue");
const {PAGES} = await import("../src/domain/navigation.js");
const {TABS} = await import("../src/domain/settingsCatalog.js");
const {store} = await import("../src/state/store.js");
const settingsPage = PAGES.settings;

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((settle) => setTimeout(settle, 10));
    await nextTick();
}

let app = null;
let host = null;
let previousSettings = null;
afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    PAGES.settings = previousSettings;
    document.body.innerHTML = "";
});

beforeEach(() => {
    previousSettings = PAGES.settings;
    PAGES.settings = {
        ...settingsPage,
        count: 5,
        children: TABS.map((tab, index) => ({...tab, count: index === 0 ? 2 : index === 1 ? 3 : 0})),
    };
    location.hash = "#/chat";
    store.booted = true;
    store.settings = {plans: {plan_agents: false}};
    store.spec = {version: "test"};
    store.sideMini = false;
    store.pluginPage = null;
    store.organization = null;
    store.rows.environments = environments;
    store.rows.domain_counts = [];
    store.rows.plans = [];
    store.rows.plugins = [];
    store.entries = [];
    api.list.mockReset().mockResolvedValue({rows: environments, counts: {all: 1, open: 1, unread: 0}, is_last_page: true});
    api.entries.mockReset().mockResolvedValue([]);
    api.organization.mockReset().mockResolvedValue({domains: []});
});

test("Settings uses the sidebar sub-page configuration", () => {
    expect(settingsPage.children.map(({key, title}) => [key, title])).toEqual(TABS.map(({key, title}) => [key, title]));
});

test("a child-page entry opens its first child, moves counts, and hides its children elsewhere", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(Sidebar)});
    app.directive("tip", {});
    app.mount(host);

    await until(() => host.querySelector('.item.parent[href="#/settings?sub=agent"]'));
    const parent = host.querySelector('.item.parent[href="#/settings?sub=agent"]');
    expect(parent.getAttribute("aria-expanded")).toBe("false");
    expect(parent.querySelector(".count").textContent).toBe("5");
    expect(parent.classList.contains("open")).toBe(false);
    expect(parent.querySelector(".exp svg")).not.toBeNull();
    expect(host.querySelector(".item-subpages")).toBeNull();

    parent.click();
    await until(() => parent.getAttribute("aria-expanded") === "true");
    expect(location.hash).toBe("#/settings?sub=agent");
    const children = [...host.querySelectorAll(".item-subpages .item-subpage")];
    expect(children.map((child) => child.querySelector(".label").textContent)).toEqual(TABS.map(({title}) => title));
    expect(children[0].classList.contains("on")).toBe(true);
    expect(children[1].classList.contains("on")).toBe(false);
    expect(parent.classList.contains("in")).toBe(true);
    expect(parent.classList.contains("open")).toBe(true);
    expect(parent.classList.contains("on")).toBe(false);
    expect(parent.querySelector(".count")).toBeNull();
    expect(children[0].querySelector(".count").textContent).toBe("2");
    expect(children[1].querySelector(".count").textContent).toBe("3");

    children[1].click();
    await until(() => children[1].classList.contains("on"));
    expect(location.hash).toBe("#/settings?sub=features");
    expect(children[1].classList.contains("on")).toBe(true);

    location.hash = "#/chat";
    await until(() => parent.getAttribute("aria-expanded") === "false");
    expect(host.querySelector(".item-subpages")).toBeNull();
    expect(parent.querySelector(".count").textContent).toBe("5");
});
