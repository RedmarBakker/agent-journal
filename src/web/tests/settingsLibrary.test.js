import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {TABS} from "../src/domain/settingsCatalog.js";

test("Settings has a Library tab in place of the Team tab, which connects, disconnects and holds the admin panes", () => {
    const tab = readFileSync("src/pages/SettingsLibrary.vue", "utf8");
    expect(TABS.map((t) => t.key)).toContain("library");
    expect(TABS.map((t) => t.key)).not.toContain("team");
    for (const call of ["api.connectLibrary", "api.disconnectLibrary", "api.inviteToLibrary", "api.libraryDevices", "api.revokeLibraryDevice", "api.libraryPeople", "api.changeLibraryPassword"]) {
        expect(tab).toContain(call);
    }
});
