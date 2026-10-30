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
    const page = ["src/pages/TeamPage.vue", "src/resource/TeamConnectForm.vue", "src/resource/TeamMembers.vue"].map((file) => readFileSync(file, "utf8")).join("\n");
    for (const call of ["api.team", "api.connectTeam", "api.disconnectTeam", "api.inviteToTeam", "api.teamDevices", "api.revokeTeamDevice", "api.teamPeople", "api.changeTeamPassword"]) {
        expect(page).toContain(call);
    }
    expect(readFileSync("src/resource/LibraryItems.vue", "utf8")).toContain("api.libraryItems");
});

test("with no team connected the page offers the connect form and the server setup with this release's install.sh", async () => {
    const status = vi.spyOn(api, "teams").mockResolvedValue({teams: []});
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
    const status = vi.spyOn(api, "teams").mockResolvedValue({teams: []});
    const releases = vi.spyOn(api, "releases").mockResolvedValue({installed: "development at 4158ac7"});
    store.summary = {version: "3.4.5"};
    const root = mounted();
    await settled();
    expect(root.textContent).toContain("releases/download/v3.4.5/install.sh");
    expect(root.textContent).not.toContain("development");
    [status, releases].forEach((spy) => spy.mockRestore());
});

const shop = {team: "shop", address: "https://shop.example.com", name: "Ada", role: "admin", people: 2, devices: 1, items: 1};
const studio = {team: "studio", address: "https://studio.example.com", name: "Ada", role: "member", people: 1, devices: 0, items: 0};
const releaseItem = {item: {item_type: "sequence", name: "release", description: "How a release goes out"}, version: {number: 2, note: "", published_at: 1793300002}, imported_version: 0};

test("with one team a connected admin sees as whom, the people, the devices and the shared items", async () => {
    const listed = vi.spyOn(api, "teams").mockResolvedValue({teams: [shop]});
    const people = vi.spyOn(api, "teamPeople").mockResolvedValue({people: [{id: 1, name: "Ada", role: "admin"}, {id: 2, name: "Carl", role: "member"}]});
    const devices = vi.spyOn(api, "teamDevices").mockResolvedValue({devices: [{id: 4, name: "laptop", account_id: 2, revoked_at: null}]});
    const items = vi.spyOn(api, "libraryItems").mockResolvedValue({items: [releaseItem]});
    const root = mounted();
    await settled();
    expect(root.textContent).toContain("Connected to https://shop.example.com as Ada, admin");
    expect(root.textContent).toContain("Carl, member");
    expect(root.textContent).toContain("laptop");
    expect(root.textContent).toContain("release");
    expect(items).toHaveBeenLastCalledWith("", "", "shop");
    [listed, people, devices, items].forEach((spy) => spy.mockRestore());
});

test("with two teams the page lists both, shows the chosen one's people and items, and asks before it disconnects one", async () => {
    const listed = vi.spyOn(api, "teams").mockResolvedValue({teams: [shop, studio]});
    const people = vi.spyOn(api, "teamPeople").mockResolvedValue({people: [{id: 1, name: "Ada", role: "admin"}]});
    const devices = vi.spyOn(api, "teamDevices").mockResolvedValue({devices: []});
    const items = vi.spyOn(api, "libraryItems").mockResolvedValue({items: []});
    const disconnect = vi.spyOn(api, "disconnectTeam").mockResolvedValue({connected: false});
    const root = mounted();
    await settled();
    expect(root.textContent).toContain("shop");
    expect(root.textContent).toContain("studio");
    expect(root.textContent).toContain("Add a team");
    expect(people).toHaveBeenLastCalledWith("shop");
    [...root.querySelectorAll("button")].find((b) => b.textContent.trim() === "studio").click();
    await settled();
    expect(people).toHaveBeenLastCalledWith("studio");
    expect(items).toHaveBeenLastCalledWith("", "", "studio");
    expect(root.textContent).toContain("Connected to https://studio.example.com as Ada, member");
    [...root.querySelectorAll("button")].find((b) => b.textContent.includes("Disconnect from studio")).click();
    await settled();
    expect(disconnect).not.toHaveBeenCalled();
    [...document.body.querySelectorAll("button")].find((b) => b.textContent.trim() === "Disconnect").click();
    await settled();
    expect(disconnect).toHaveBeenLastCalledWith("studio");
    [listed, people, devices, items, disconnect].forEach((spy) => spy.mockRestore());
});
