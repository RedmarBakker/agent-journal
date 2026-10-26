import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";

test("the journal's name shows on a tab return unless the switch on the Settings page turned it off", async () => {
    const {store} = await import("../src/state/store.js");
    const {ui} = await import("../src/state/ui.js");
    const {catalog} = await import("../src/domain/settingsCatalog.js");
    const {default: ProjectFlash} = await import("../src/layout/ProjectFlash.vue");
    const sections = catalog({features: [], groups: [{key: "project", title: "Project"}]}, {viewer: {flash: false}});
    expect(JSON.stringify(sections)).toContain("Show the journal's name when you come back");
    store.settings = {viewer: {flash: false}, features: {}};
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(ProjectFlash)});
    app.mount(host);
    ui.flash.at = Date.now();
    await nextTick();
    expect(host.querySelector(".flash-veil")).toBe(null);
    store.settings = {viewer: {flash: true}, features: {}};
    ui.flash.at = Date.now() + 1;
    await nextTick();
    await nextTick();
    expect(host.querySelector(".flash-veil")).not.toBe(null);
    app.unmount();
    host.remove();
});
