import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {removeWords, worktreeWords} from "../src/domain/journals.js";

test("an environment with a worktree offers to remove the worktree alone, through its own route, and removing the environment says the worktree stays", () => {
    const page = readFileSync("src/pages/SettingsEnvironments.vue", "utf8");
    const client = readFileSync("src/api/client.js", "utf8");
    expect(page).toContain("Remove worktree");
    expect(page).toContain("api.removeWorktree(row.id)");
    expect(client).toContain('this.act("environments", environment, "worktree-removal")');
    expect(removeWords({name: "calm-river"}, false)).toContain("its worktree, if it has one, stays");
    expect(worktreeWords("calm-river")).toContain("its branch and its last commit stay");
});
