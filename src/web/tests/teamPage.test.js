import {readFileSync} from "node:fs";
import {expect, test, vi} from "vitest";
import {createApp, h, nextTick} from "vue";
import {api} from "../src/api/client.js";
import {PAGES} from "../src/domain/navigation.js";
import {TABS} from "../src/domain/settingsCatalog.js";
import {store} from "../src/state/store.js";
import TeamPage from "../src/pages/TeamPage.vue";

const settled = async () => {
    for (let n = 0; n < 6; n += 1) await nextTick();
};

function mounted() {
    const root = document.createElement("div");
    createApp({render: () => h(TeamPage)}).mount(root);
    return root;
}

test("the sidebar has a Team item where the Library item was, and the Library address opens the Team page", () => {
    expect(PAGES.team.title).toBe("Team");
    expect(PAGES.library).toBeUndefined();
    const navigation = readFileSync("src/composables/navigation.js", "utf8");
    expect(navigation).toContain('"secrets", "team", "resources", "settings"');
    expect(readFileSync("src/route.js", "utf8")).toContain('library: "team"');
});

test("Settings holds neither a Library nor a Team tab, so the connection lives on the Team page alone", () => {
    expect(TABS.map((t) => t.key)).not.toContain("library");
    expect(TABS.map((t) => t.key)).not.toContain("team");
});

test("the Team page connects, disconnects, invites, lists people and devices, changes a password and lists the shared items", () => {
    const page = readFileSync("src/pages/TeamPage.vue", "utf8");
    for (const call of ["api.team", "api.connectTeam", "api.disconnectTeam", "api.inviteToTeam", "api.teamDevices", "api.revokeTeamDevice", "api.teamPeople", "api.changeTeamPassword"]) {
        expect(page).toContain(call);
    }
    expect(readFileSync("src/resource/LibraryItems.vue", "utf8")).toContain("api.libraryItems");
});

test("with no team connected the page offers the connect form and the server setup with this release's install.sh", async () => {
    const status = vi.spyOn(api, "team").mockResolvedValue({connected: false});
    store.summary = {version: "3.4.5"};
    const root = mounted();
    await settled();
    expect(root.textContent).toContain("Connect to a team");
    expect(root.textContent).toContain("Set a team server up");
    expect(root.textContent).toContain("curl -fsSL https://github.com/jessegall/agent-journal/releases/download/v3.4.5/install.sh | sh");
    expect(root.textContent).toContain("Docker");
    status.mockRestore();
});

test("on a development install the setup still names the release the journal carries, never the branch and commit", async () => {
    const status = vi.spyOn(api, "team").mockResolvedValue({connected: false});
    const releases = vi.spyOn(api, "releases").mockResolvedValue({installed: "development at 4158ac7"});
    store.summary = {version: "3.4.5"};
    const root = mounted();
    await settled();
    expect(root.textContent).toContain("releases/download/v3.4.5/install.sh");
    expect(root.textContent).not.toContain("development");
    [status, releases].forEach((spy) => spy.mockRestore());
});

test("a connected admin sees as whom, the people, the devices and the shared items", async () => {
    const status = vi.spyOn(api, "team").mockResolvedValue({connected: true, address: "https://team.example.com", name: "Ada", role: "admin"});
    const people = vi.spyOn(api, "teamPeople").mockResolvedValue({people: [{id: 1, name: "Ada", role: "admin"}, {id: 2, name: "Carl", role: "member"}]});
    const devices = vi.spyOn(api, "teamDevices").mockResolvedValue({devices: [{id: 4, name: "laptop", account_id: 2, revoked_at: null}]});
    const items = vi.spyOn(api, "libraryItems").mockResolvedValue({items: [{item: {item_type: "sequence", name: "release", description: "How a release goes out"}, version: {number: 2, note: "", published_at: 1793300002}, imported_version: 0}]});
    const root = mounted();
    await settled();
    expect(root.textContent).toContain("Connected to https://team.example.com as Ada, admin");
    expect(root.textContent).toContain("Carl, member");
    expect(root.textContent).toContain("laptop");
    expect(root.textContent).toContain("release");
    [status, people, devices, items].forEach((spy) => spy.mockRestore());
});
