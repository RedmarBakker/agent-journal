import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

let answer;
vi.mock(import("../src/api/client.js"), async (importOriginal) => {
    const actual = await importOriginal();
    return {...actual, api: {...actual.api, freshReleases: () => new Promise((resolve) => (answer = resolve))}};
});

const {default: AboutPage} = await import("../src/pages/AboutPage.vue");

test("the About page shows a skeleton until the version and changelog arrive, then the version in its place", async () => {
    const root = document.createElement("div");
    createApp({render: () => h(AboutPage)}).mount(root);
    await nextTick();
    expect(root.querySelector("[aria-busy='true']")).not.toBeNull();
    expect(root.querySelector(".version")).toBeNull();
    answer({installed: "4.67.4", latest: "4.67.4", changelog: "", is_last_page: true});
    await nextTick();
    await nextTick();
    expect(root.querySelector("[aria-busy='true']")).toBeNull();
    expect(root.querySelector(".version").textContent).toBe("Agent journal 4.67.4");
});
