import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {actorName, agentName, colleagueOwner, environmentLabel, isMe, personName, sidebarEnvironments} from "../src/domain/people.js";
import {workerActions} from "../src/domain/workers.js";

const team = (me) => ({me, device: me === 3 ? "d3" : "d7", people: [{id: 3, name: "Jesse Gall"}, {id: 7, name: "Anna de Vries"}], owners: {12: 7, 13: 3}});

test("a message by user 7 is Anna de Vries to user 3 and you to user 7", () => {
    expect(actorName("user:7", team(3))).toBe("Anna de Vries");
    expect(actorName("user:7", team(7))).toBe("you");
    expect(isMe("user:7", team(7)) && !isMe("user:7", team(3))).toBe(true);
});

test("an agent is named by the person who owns its environment", () => {
    expect(actorName("agent:abc", team(3), 12)).toBe("Anna de Vries's agent");
    expect(agentName(13, team(3))).toBe("the agent");
    expect(agentName(99, team(3))).toBe("the agent");
});

test("another machine's worker offers no action here", () => {
    const worker = {id: 1, state: "dispatched", pid: 5, device: "d7", started_at: "2026-10-23T10:00:00Z"};
    expect(workerActions(worker, "d3")).toEqual([]);
    expect(workerActions(worker, "d7").length).toBeGreaterThan(0);
    expect(workerActions({...worker, device: ""}).length).toBeGreaterThan(0);
});

test("a colleague's environment opens with a box to comment as yourself and no controls of its agent", () => {
    expect(colleagueOwner(12, team(3))).toBe(7);
    expect(colleagueOwner(13, team(3))).toBe(0);
    expect(personName(3, team(3))).toBe("Jesse Gall");
    const thread = readFileSync(resolve(__dirname, "../src/chat/Thread.vue"), "utf8");
    expect(thread).toMatch(/:placeholder="colleague \? `Comment as \$\{me\}` : 'Message the agent'"/);
    const bar = readFileSync(resolve(__dirname, "../src/chat/AgentBar.vue"), "utf8");
    expect(bar).toMatch(/<template v-else-if="colleague && data">\s*<div class="agent-bar agent-bar-read-only">\s*<AgentFacts :data="data" open="" @toggle="\(\) => \{\}" \/>\s*<span class="agent-bar-owner">\{\{ colleague \}\}'s agent, read only<\/span>/);
    expect(bar).toMatch(/<div class="agent-bar agent-bar-colleague">\{\{ colleague \}\}'s environment: no agent is running there<\/div>/);
    const status = readFileSync(resolve(__dirname, "../src/layout/StatusBar.vue"), "utf8");
    expect(status).toMatch(/<template v-if="running && !colleague">/);
});

test("a colleague's comment is drawn as theirs, named above it in their colour, and never as yours", async () => {
    const {threadTurns} = await import("../src/domain/thread.js");
    const {
        turns: [turn],
    } = threadTurns([{id: 9, author: "colleague", creator: "user:7", text: "nice work", created_at: "2026-10-23T10:00:00Z", files: [], data: {colleague: "Anna de Vries", colleague_user: 7}}], []);
    expect(turn.who).toBe("colleague");
    const message = readFileSync(resolve(__dirname, "../src/chat/TurnMessage.vue"), "utf8");
    expect(message).toMatch(/<template v-if="turn.who === 'colleague'">\s*<p class="thread-who">\{\{ \(turn.data \|\| \{\}\).colleague \}\}<\/p>/);
});

test("a side thread view sits beside the chat for people, and says no agent reads it", async () => {
    const {VIEWS} = await import("../src/domain/panes.js");
    expect(VIEWS).toContain("side");
    const side = readFileSync(resolve(__dirname, "../src/chat/SideThread.vue"), "utf8");
    expect(side).toMatch(/People talk here beside the chat\. No agent reads it\./);
    expect(side).toMatch(/actorName\(row\.creator, store\.people\)/);
});

test("a colleague's command card is drawn from its message, and opening it says the output stays on their machine", () => {
    const live = readFileSync(resolve(__dirname, "../src/composables/activeCards.js"), "utf8");
    expect(live).toMatch(/colleague\.value \? \[\] :/);
    const dock = readFileSync(resolve(__dirname, "../src/chat/WatchDock.vue"), "utf8");
    expect(dock).toMatch(/This output stays on \{\{ colleague \}\}'s machine/);
    expect(dock).toMatch(/if \(!colleague\.value && card\.value\.output\) await pages\.poll\(\)/);
    const dialog = readFileSync(resolve(__dirname, "../src/chat/OutputDialog.vue"), "utf8");
    expect(dialog).toMatch(/This output stays on \{\{ owner \}\}'s machine/);
    const thread = readFileSync(resolve(__dirname, "../src/chat/Thread.vue"), "utf8");
    expect(thread).toMatch(/<OutputDialog :key="outputOpen" :n="outputOpen" :owner="colleague"/);
});

test("the Team chat is named so in the sidebar, and each person's message there is named by its writer", () => {
    const sidebar = readFileSync(resolve(__dirname, "../src/layout/Sidebar.vue"), "utf8");
    expect(sidebar).toMatch(/environmentLabel\(e, store\.people\)/);
    expect(environmentLabel({id: 13, name: "team", environment_type: "session"}, team(3))).toBe("Team chat");
    const header = readFileSync(resolve(__dirname, "../src/chat/TurnHeader.vue"), "utf8");
    expect(header).toMatch(/mine && !isMe\(turn\.creator, store\.people\)/);
    expect(actorName("user:7", team(3))).toBe("Anna de Vries");
    expect(isMe("user:3", team(3))).toBe(true);
});

test("the Team chat's bar names who holds it and offers a Claim", () => {
    const bar = readFileSync(resolve(__dirname, "../src/chat/AgentBar.vue"), "utf8");
    expect(bar).toMatch(/<template v-if="teamChat">\s*<TeamChatBar \/>/);
    const team = readFileSync(resolve(__dirname, "../src/chat/TeamChatBar.vue"), "utf8");
    expect(team).toMatch(/usePoll\("team.chat"/);
    expect(team).toMatch(/<Btn class="team-chat-claim" @click="claim">Claim<\/Btn>/);
});

test("the sidebar lists the viewer's own environments and the Team chat", () => {
    const people = {me: 1, device: "d1", people: [{id: 1, name: "Ada"}, {id: 2, name: "Bob"}], owners: {"10": 1, "11": 2, "12": 2, "13": 0}};
    const rows = [{id: 10, name: "ada-main"}, {id: 11, name: "bob-main"}, {id: 12, name: "bob-docs"}, {id: 13, name: "team"}];
    expect(sidebarEnvironments(rows, people).map((row) => row.name)).toEqual(["ada-main", "team"]);
    const sidebar = readFileSync(resolve(__dirname, "../src/layout/Sidebar.vue"), "utf8");
    expect(sidebar).toMatch(/ownEnvironments\(rows\("environments"\), store\.people\)/);
    expect(sidebar).toMatch(/teamGroups\(rows\("environments"\), store\.people\)/);
});

test("an environment a colleague shares with the team shows in the sidebar with their name, and leaves it once taken back", () => {
    const people = {me: 1, device: "d1", people: [{id: 1, name: "Ada"}, {id: 2, name: "Bob"}], owners: {"10": 1, "12": 2}};
    const shared = {id: 12, name: "bob-docs", environment_type: "local", team_key: "k1"};
    expect(sidebarEnvironments([{id: 10, name: "ada-main"}, shared], people).map((row) => environmentLabel(row, people))).toEqual(["ada-main", "bob-docs · Bob"]);
    expect(sidebarEnvironments([{id: 10, name: "ada-main"}, {...shared, team_key: ""}], people).map((row) => row.name)).toEqual(["ada-main"]);
    const sidebar = readFileSync(resolve(__dirname, "../src/layout/Sidebar.vue"), "utf8");
    expect(sidebar).toMatch(/v-if="!onPhone && !colleagueOwner\(e\.id, store\.people\)"/);
    const settings = readFileSync(resolve(__dirname, "../src/pages/SettingsEnvironments.vue"), "utf8");
    expect(settings).toMatch(/row\.shared \? api\.unshareEnvironment\(row\.id\) : api\.shareEnvironment\(row\.id\)/);
});

test("the Team page lists each person with their environments and opens a colleague's in place", () => {
    const page = readFileSync(resolve(__dirname, "../src/pages/TeamPage.vue"), "utf8");
    expect(page).toMatch(/api\.teamPeople\(\)/);
    expect(page).toMatch(/<TeamConnect :email="standing\.email" @joined="joined" \/>/);
    const people = readFileSync(resolve(__dirname, "../src/pages/TeamPeople.vue"), "utf8");
    expect(people).toMatch(/@click="choose\(environment\.name\)"/);
    const tab = readFileSync(resolve(__dirname, "../src/pages/SettingsTeam.vue"), "utf8");
    expect(tab).toMatch(/<TeamConnect :email="standing\.email" @joined="joined" \/>/);
    const local = readFileSync(resolve(__dirname, "../src/pages/TeamLocal.vue"), "utf8");
    expect(local).toMatch(/<template v-if="standing\.admin">\s*<TeamAdmin \/>/);
    const admin = readFileSync(resolve(__dirname, "../src/pages/TeamAdmin.vue"), "utf8");
    expect(admin).toMatch(/<TeamInvite \/>\s*<TeamDevices \/>/);
});

test("connecting opens on two choices: claiming a server asks its address and then the admin account, an account connects with the form", async () => {
    const read = (name) => readFileSync(resolve(__dirname, `../src/pages/${name}.vue`), "utf8");
    const form = read("TeamConnect") + read("TeamChoice") + read("TeamClaim") + read("TeamAccount");
    expect(form).toMatch(/const step = ref\("choice"\)/);
    expect(read("TeamConnect")).toMatch(/<SwitchCase :value="step">[\s\S]*#choice[\s\S]*#claim[\s\S]*#default/);
    expect(read("TeamChoice")).toMatch(/<Btn kind="primary" @click="\$emit\('open', 'claim'\)">Claim a server<\/Btn>\s*<Btn @click="\$emit\('open', 'connect'\)">Connect with an account<\/Btn>/);
    expect([...form.matchAll(/<FormField label="([^"]+)"/g)].map((m) => m[1])).toEqual(["Server address", "Team URL", "Email", "Password"]);
    expect(form).not.toMatch(/[Ss]etup code|setup_code/);
    expect(form).toMatch(/<Btn @click="\$emit\('generate'\)">Generate<\/Btn>/);
    expect(form).not.toMatch(/ListBox/);
    expect(form).toMatch(/const got = await api\.checkTeam\(\{url: url\.value\}\);[\s\S]*?if \(got\.refusal\) failure\.value = got\.refusal;\s*else step\.value = "account";/);
    expect(form).toMatch(/\{\{ busy \? "Checking" : "Next" \}\}/);
    const page = readFileSync(resolve(__dirname, "../src/pages/TeamPage.vue"), "utf8");
    expect(page).toMatch(/\.team-page-content\.flush \{\s*gap: 0;\s*padding: 0;/);
    const {strongPassword} = await import("../src/domain/passwords.js");
    const made = strongPassword();
    expect(made).toHaveLength(22);
    expect(strongPassword()).not.toBe(made);
});

test("a journal behind its team updates from a button on the Team tab, never a command to copy", () => {
    const sync = readFileSync(resolve(__dirname, "../src/pages/TeamSync.vue"), "utf8");
    expect(sync).toMatch(/<Btn kind="primary" :busy="updating" @click="update">Update to \{\{ standing\.version \}\}<\/Btn>/);
    expect(sync).not.toMatch(/journal update apply/);
});

test("the viewer keeps a chat's messages in the order they were written, whichever journal numbered them", () => {
    const rows = readFileSync(resolve(__dirname, "../src/sync/rows.js"), "utf8");
    expect(rows).toMatch(/const ORDERS = \{messages: byWriting\}/);
    expect(rows).not.toMatch(/\.sort\(byId\)/);
});

test("a joined journal shows a Team button with a dot for how its sync stands, and no sync line by the pause button", () => {
    const top = readFileSync(resolve(__dirname, "../src/layout/TopBar.vue"), "utf8");
    expect(top).toMatch(/<a class="icon-btn team-btn" :href="href\.settings\('team'\)"/);
    expect(top).toMatch(/const SYNC_TONES = \{in_step: "good", waiting: "busy", connecting: "busy", not_connected: "bad", version: "bad"\}/);
    const bar = readFileSync(resolve(__dirname, "../src/layout/StatusBar.vue"), "utf8");
    expect(bar).not.toMatch(/statusbar-sync/);
});

test("the Team page opens the shared journal by a one-time link from this journal", () => {
    const page = readFileSync(resolve(__dirname, "../src/pages/TeamPage.vue"), "utf8");
    expect(page).toMatch(/<Btn small :busy="opening" @click="openShared">Open the shared journal <Icon name="open" :size="12" \/><\/Btn>/);
    expect(page).toMatch(/window\.open\(\(await api\.openSharedJournal\(\)\)\.url, "_blank", "noopener"\)/);
});

test("a person changes their team password, and an admin resets a member's from the people list", () => {
    const own = readFileSync(resolve(__dirname, "../src/pages/TeamPassword.vue"), "utf8");
    expect(own).toMatch(/api\.changeTeamPassword\(old\.value, password\.value\)/);
    expect(own).toMatch(/<Btn @click="generate">Generate<\/Btn>/);
    const people = readFileSync(resolve(__dirname, "../src/pages/TeamPeople.vue"), "utf8");
    expect(people).toMatch(/<Btn small @click="reset\(person\)">Reset password<\/Btn>/);
    const local = readFileSync(resolve(__dirname, "../src/pages/TeamLocal.vue"), "utf8");
    expect(local).toMatch(/<TeamPeople :people="people" :devices="devices" :admin="standing\.admin" \/>\s*<TeamPassword \/>/);
});

test("a joined Team page offers Disconnect and names the team server's address", () => {
    const page = readFileSync(resolve(__dirname, "../src/pages/TeamPage.vue"), "utf8");
    expect(page).toMatch(/<Btn small :busy="leaving" @click="leave">Disconnect<\/Btn>/);
    expect(page).toMatch(/await api\.leaveTeam\(\)/);
    expect(page).toMatch(/`team server \$\{standing\.value\.address\}`/);
});


test("each colleague's messages carry their own steady colour, never the viewer's blue, and the viewer's own stay unmarked", async () => {
    const {colleagueColour, COLLEAGUE_COLOURS} = await import("../src/domain/people.js");
    const people = {me: 1, device: "", people: [], owners: {}};
    const ada = colleagueColour("user:2", people);
    const bob = colleagueColour("user:3", people);
    expect(colleagueColour("user:1", people)).toBe("");
    expect(colleagueColour("agent:s1", people)).toBe("");
    expect(ada).not.toBe(bob);
    expect(COLLEAGUE_COLOURS).toContain(ada);
    expect(colleagueColour("user:2", {...people, me: 3})).toBe(ada);
});
