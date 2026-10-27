import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

const {api} = await import("../src/api/client.js");
const {default: SettingsServices} = await import("../src/pages/SettingsServices.vue");
const {TABS} = await import("../src/domain/settingsCatalog.js");

afterEach(() => {
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("the Services tab lists every process the supervisor runs, with its state, since when and its process id, from the served answer", async () => {
    const now = Date.now() / 1000;
    const answer = {
        processes: [
            {environment: "main", name: "agent", pid: 4101, is_active: true, started_at: now - 7200, restarts: 0, front: true},
            {environment: "main", name: "journal", pid: 4102, is_active: true, started_at: now - 3600, restarts: 1, front: false},
            {environment: "main", name: "tunnel", pid: 0, is_active: false, started_at: 0, restarts: 3, front: false},
        ],
    };
    vi.spyOn(api, "supervised").mockResolvedValue(answer);
    expect(TABS.map((tab) => tab.key)).toContain("services");
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(SettingsServices)});
    app.directive("tip", {});
    app.mount(host);
    await flush();
    const rows = [...host.querySelectorAll(".table-row:not(.head):not(.empty)")].map((row) => [...row.querySelectorAll(".cell")].map((cell) => cell.textContent.trim()));
    expect(rows.map((row) => row[0])).toEqual(["agent (the agent's terminal)", "journal", "tunnel"]);
    expect(rows.map((row) => row[2])).toEqual(["Running", "Running", "Stopped"]);
    expect(rows.map((row) => row[4])).toEqual(["4101", "4102", ""]);
    expect(rows[0][3]).toContain("ago");
    expect(rows[1][5]).toBe("1");
    app.unmount();
});
