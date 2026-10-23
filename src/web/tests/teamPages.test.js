import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {api} = await import("../src/api/client.js");
const {narrow} = await import("../src/platform/view.js");
const {default: TeamLocal} = await import("../src/pages/TeamLocal.vue");
const {default: TeamHosted} = await import("../src/pages/TeamHosted.vue");

const now = Date.now() / 1000;
const standing = {joined: true, address: "https://team.example", line: "In step with the team", state: "in_step", version: "4.38.0", running: "4.38.0", waiting: 0, admin: true, device: "1"};
const people = [
    {id: 1, name: "Jesse Gall", role: "admin", me: true, online: true, seen_at: now, environments: [{id: 2, name: "main"}]},
    {id: 2, name: "Ada Lovelace", role: "member", me: false, online: false, seen_at: now - 3600, environments: [{id: 5, name: "ada/sync"}]},
];
const devices = [
    {id: 1, name: "jesse-mbp", person: "Jesse Gall", pulled_at: now, this: true},
    {id: 2, name: "ada-thinkpad", person: "Ada Lovelace", pulled_at: now - 3600, this: false},
];
let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    narrow.value = false;
    vi.restoreAllMocks();
});

async function mounted(component) {
    vi.spyOn(api, "teamChat").mockResolvedValue({line: "Held by Ada Lovelace", mine: false, claimable: false, holder: "Ada Lovelace"});
    vi.spyOn(api, "teamDevices").mockResolvedValue({devices});
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(component, {standing, people, devices})});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    return host;
}

const titles = (el) => [...el.querySelectorAll(".list-box-title")].map((title) => title.textContent.trim());
const columns = (host) => [...host.querySelectorAll(".team-grid > .team-column")].map(titles);

test("the local Team page places each section in its column as drawn, the pool's drawn empty, and stacks them in the drawn order when narrow", async () => {
    let host = await mounted(TeamLocal);
    expect(columns(host)).toEqual([
        ["Lent out now", "Your workers on other machines", "Connected now"],
        ["Sync", "Worker pool offer", "Team chat", "Your password", "Invite a person", "Devices"],
    ]);
    expect(host.textContent).toContain("This machine offers no workers to the team, so none is lent out.");
    expect(host.textContent).toContain("None of your workers runs on another machine.");
    expect(host.textContent).toContain("1 of 2 online");
    expect(host.textContent).toContain("ada-thinkpad");
    expect([...host.querySelectorAll(".list-box-aside")].map((aside) => aside.textContent)).toEqual(["No workers offered", "Admin", "Admin"]);
    app.unmount();
    narrow.value = true;
    host = await mounted(TeamLocal);
    expect(titles(host)).toEqual(["Lent out now", "Sync", "Your workers on other machines", "Worker pool offer", "Team chat", "Connected now", "Your password", "Invite a person", "Devices"]);
});

test("the hosted Team page puts the summary on top and each section in its column as drawn, with no claim of the Team chat, and stacks them in the drawn order when narrow", async () => {
    let host = await mounted(TeamHosted);
    expect([...host.querySelectorAll(".team-summary .team-label")].map((label) => label.textContent)).toEqual(["Team server", "Team version", "People", "Worker pool"]);
    expect(columns(host)).toEqual([
        ["Pool workers running", "Machines"],
        ["Team version", "Team chat", "People", "Team server"],
    ]);
    expect(host.textContent).toContain("No pool worker is running.");
    expect([...host.querySelectorAll(".team-th")].map((head) => head.textContent)).toEqual(["Machine", "Person", "Presence", "Journal version", "Pool offer"]);
    expect([...host.querySelectorAll("button")].some((button) => ["Claim", "Release"].includes(button.textContent.trim()))).toBe(false);
    app.unmount();
    narrow.value = true;
    host = await mounted(TeamHosted);
    expect(titles(host)).toEqual(["Pool workers running", "Team version", "Machines", "Team chat", "People", "Team server"]);
});
