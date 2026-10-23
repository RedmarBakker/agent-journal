import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";

test("a new environment can carry on from a kept session, and the form opens by itself while there is no environment", () => {
    const form = readFileSync(resolve(__dirname, "../src/layout/NewEnvironment.vue"), "utf8");
    expect(form).toMatch(/onMounted\(async \(\) => \(sessions\.value = await api\.pastSessions\(\)\)\)/);
    expect(form).toMatch(/<span class="new-env-label">Carry on from<\/span>/);
    expect(form).toMatch(/:disabled="!!row\.environment"/);
    expect(form).toMatch(/api\.create\("environments", \{name: name\.value\.trim\(\), \.\.\.from\}\)/);
    const sidebar = readFileSync(resolve(__dirname, "../src/layout/Sidebar.vue"), "utf8");
    expect(sidebar).toMatch(/onMounted\(async \(\) => \(creating\.value = !\(await api\.list\("environments"\)\)\.rows\.length\)\)/);
});
