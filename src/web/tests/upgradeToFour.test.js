import {createApp, h, nextTick} from "vue";
import {describe, expect, test} from "vitest";
import UpgradeToFourDialog from "../src/layout/UpgradeToFourDialog.vue";

async function shown(onNo = () => {}) {
    window.document.body.innerHTML = "";
    const host = window.document.createElement("div");
    window.document.body.append(host);
    createApp({render: () => h(UpgradeToFourDialog, {version: "4.0.0", onNo})}).mount(host);
    for (let i = 0; i < 3; i++) await nextTick();
    return window.document.body;
}

describe("the upgrade to version 4 dialog", () => {
    test("has two buttons and no close button, and the backdrop does not close it", async () => {
        const page = await shown();
        expect([...page.querySelectorAll("button")].map((one) => one.textContent.trim())).toEqual(["Upgrade and migrate", "No"]);
        page.querySelector(".dialog").click();
        await nextTick();
        expect(page.querySelector("[role=dialog]")).not.toBeNull();
    });

    test("says what will happen in plain words", async () => {
        const text = (await shown()).textContent;
        for (const said of ["close completely", "install script", "to-dos become tasks", "kept whole", "board is set aside"]) {
            expect(text.toLowerCase()).toContain(said.toLowerCase());
        }
    });

    test("No tells the page to put it off", async () => {
        let put = 0;
        const page = await shown(() => put++);
        [...page.querySelectorAll("button")].find((one) => one.textContent.trim() === "No").click();
        expect(put).toBe(1);
    });
});
