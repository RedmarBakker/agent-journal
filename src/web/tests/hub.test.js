import {readFileSync} from "node:fs";
import {createApp, h} from "vue";
import {afterEach, expect, test} from "vitest";
import {ownEnvironments, teamGroups} from "../src/domain/hub.js";
import HubBoard from "../src/pages/HubBoard.vue";
import HubHome from "../src/pages/HubHome.vue";

let app = null;

afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
});

function mounted(component, props) {
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp({render: () => h(component, props)});
    app.mount(host);
    return host;
}

const hub = {id: 5, kind: "hub", name: "acme", team_name: "acme", team_key: "k1"};
const environments = [
    {id: 1, name: "main", kind: "local"},
    {id: 2, name: "docs", kind: "local", is_shared_with_team: true},
    {id: 3, name: "team", kind: "local", is_team_chat: true},
    {id: 4, name: "bobs-api", kind: "local", is_shared_with_team: true},
    hub,
];
const people = {me: 1, device: "", people: [], owners: {1: 1, 2: 1, 4: 2}};

test("the sidebar groups each team's hub and its sessions under the team's name, apart from the person's own environments", () => {
    const [group] = teamGroups(environments, people);
    expect(group.team).toBe("acme");
    expect(group.hub.id).toBe(5);
    expect(group.sessions.map((row) => row.name)).toEqual(["team", "bobs-api"]);
    expect(ownEnvironments(environments, people).map((row) => row.name)).toEqual(["main", "docs"]);
    expect(readFileSync("src/layout/Sidebar.vue", "utf8")).toContain("teamGroups(rows(\"environments\")");
});

test("the hub home lists the hub's documents, plans and recent activity", () => {
    const host = mounted(HubHome, {
        hub,
        docs: [{id: 1, table: "docs", title: "Handbook"}],
        plans: [{id: 2, table: "plans", title: "Launch"}],
        activity: [{id: 9, table: "messages", text: "Ada filed a task", updated_at: "2026-10-25T08:00:00Z"}],
    });
    expect(host.querySelector(".team").textContent).toBe("acme");
    expect(host.querySelector("[data-hub-docs]").textContent).toContain("Handbook");
    expect(host.querySelector("[data-hub-plans]").textContent).toContain("Plan 2: Launch");
    expect(host.querySelector("[data-hub-activity]").textContent).toContain("Ada filed a task");
});

test("the hub board puts each task of the hub in the column of its state", () => {
    const host = mounted(HubBoard, {tasks: [{id: 1, title: "a", state: "open"}, {id: 2, title: "b", state: "started"}, {id: 3, title: "c", state: "blocked"}, {id: 4, title: "d", state: "done"}, {id: 5, title: "e", state: "open"}]});
    const column = (key) => [...host.querySelectorAll(`[data-column=${key}] .card`)].map((card) => card.textContent.trim());
    expect(column("open")).toEqual(["Task 1: a", "Task 5: e"]);
    expect(column("started")).toEqual(["Task 2: b"]);
    expect(column("waiting")).toEqual(["Task 3: c"]);
    expect(column("done")).toEqual(["Task 4: d"]);
});

test("a hub task is named with its team on its card", () => {
    const host = mounted(HubBoard, {tasks: [{id: 57, title: "ship it", state: "open", environment_id: 5}, {id: 8, title: "local", state: "open", environment_id: 1}], environments: environments});
    expect([...host.querySelectorAll("[data-column=open] .card")].map((card) => card.textContent.trim())).toEqual(["acme task 57: ship it", "Task 8: local"]);
});
