import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {useNavigation} from "../src/composables/navigation.js";

test("collections have their own link in the sidebar's environment section", () => {
    const {sections} = useNavigation();
    const environment = sections.value.find((section) => section.key === "environment");
    expect(environment.links.map((link) => link.key)).toContain("collections");
});

test("a collection's card counts its members by kind, read by id since the list carries none", () => {
    const index = readFileSync("src/pages/Index.vue", "utf8");
    const pollers = readFileSync("src/sync/pollers.js", "utf8");
    expect(index).toContain(`<ResourceCard :resource="membersOf(r) || r" @click="go(table, r.id)" />`);
    expect(pollers).toContain('"rows.shown": {read: ({table, ids}) => api.list(table, {ids})');
    expect(readFileSync("src/resource/Reader.vue", "utf8")).toContain("useRowsShown(() => (scope ? \"\" : props.table), computed(() => [props.id]))");
});
