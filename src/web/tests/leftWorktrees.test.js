import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

test("worktrees whose environment is gone are listed under the environments with their own Remove, and a hosted journal offers no worktree removal", () => {
    const page = readFileSync("src/pages/SettingsEnvironments.vue", "utf8");
    const client = readFileSync("src/api/client.js", "utf8");
    expect(page).toContain('title="Worktrees with no environment"');
    expect(page).toContain("api.removeLeftWorktree(tree.name)");
    expect(page).toContain('worktree: hosted.value ? ""');
    expect(client).toContain('this.get(this.here("/worktrees"))');
});
