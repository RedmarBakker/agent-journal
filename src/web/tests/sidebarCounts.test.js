import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {useNavigation} from "../src/composables/navigation.js";
import {store} from "../src/state/store.js";

test("the sidebar's task count says it counts the open tasks outside a plan, since a plan's own are on its bar", () => {
    const navigation = readFileSync("src/composables/navigation.js", "utf8");
    const sidebar = readFileSync("src/layout/Sidebar.vue", "utf8");
    expect(navigation).toContain('tasks: "open tasks outside a plan"');
    expect(sidebar).toContain(":title=\"link.countTitle && link.count ? `${link.count} ${link.countTitle}` : null\"");
});

test("the sidebar's Plans item shows the plans being worked, which the API reports beside the open ones", () => {
    store.counts = {...store.counts, plans: {all: 9, open: 7, unread: 4}, tasks: {all: 3, open: 2, unread: 0}};
    const {sections} = useNavigation();
    const links = sections.value.flatMap((section) => section.links);
    expect(links.find((link) => link.key === "plans").count).toBe(4);
    expect(links.find((link) => link.key === "tasks").count).toBe(2);
});
