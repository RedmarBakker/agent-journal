import {expect, test} from "vitest";
import {useNavigation} from "../src/composables/navigation.js";

test("collections have their own link in the sidebar's environment section", () => {
    const {sections} = useNavigation();
    const environment = sections.value.find((section) => section.key === "environment");
    expect(environment.links.map((link) => link.key)).toContain("collections");
});
