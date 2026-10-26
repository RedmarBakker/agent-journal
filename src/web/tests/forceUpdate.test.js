import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

vi.mock("../src/platform/timing.js", async (original) => ({...(await original()), wait: async () => {}}));
import {api} from "../src/api/client.js";

test("the changelog page offers the install command from the README, which runs even while GitHub refuses to list the releases", async () => {
    vi.spyOn(api, "freshReleases").mockResolvedValue({installed: "4.63.4", latest: "4.63.4", newer: false, changelog: "", shown: 0, is_last_page: true, started_at: 1});
    const forced = vi.spyOn(api, "forceUpdate").mockResolvedValue({installed: "4.63.4", started_at: 1});
    vi.spyOn(api, "releases").mockResolvedValue({installed: "4.63.4", started_at: 2});
    const reload = vi.fn();
    Object.defineProperty(window, "location", {value: {...window.location, hash: "", reload}, configurable: true});
    const {default: AboutPage} = await import("../src/pages/AboutPage.vue");
    const host = document.createElement("div");
    document.body.append(host);
    createApp({render: () => h(AboutPage)}).mount(host);
    await new Promise((resolve) => setTimeout(resolve));
    await nextTick();
    const button = host.querySelector(".force-update");
    expect(button.textContent).toContain("Install the latest release with the README command");
    button.click();
    await new Promise((resolve) => setTimeout(resolve));
    expect(forced).toHaveBeenCalled();
    expect(reload).toHaveBeenCalled();
});
