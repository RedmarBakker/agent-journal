import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

test("the sidebar's task count says it counts the open tasks outside a plan, since a plan's own are on its bar", () => {
    const navigation = readFileSync("src/composables/navigation.js", "utf8");
    const sidebar = readFileSync("src/layout/Sidebar.vue", "utf8");
    expect(navigation).toContain('tasks: "open tasks outside a plan"');
    expect(sidebar).toContain(":title=\"link.countTitle && link.count ? `${link.count} ${link.countTitle}` : null\"");
});
