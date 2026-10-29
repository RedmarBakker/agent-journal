// Needs a browser: node src/web/tests/heldMessages.browser.mjs
import assert from "node:assert/strict";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const server = await createServer({root: fileURLToPath(new URL("..", import.meta.url)), logLevel: "error", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH});

try {
    const page = await browser.newPage({viewport: {width: 1100, height: 720}});
    await page.clock.install();
    await page.route("**/journal/**", (route) => route.fulfill({json: {rows: [], outputs: [], is_last_page: true}}));
    for (const gap of [1, 80]) {
        await page.goto(new URL("tests/fixtures/heldMessages.html", server.resolvedUrls.local[0]).href);
        await page.locator(".thread-scroll [data-ref]").first().waitFor();
        await page.waitForTimeout(700);
        const before = await page.evaluate((gap) => {
            const pane = document.querySelector(".thread-scroll");
            pane.dispatchEvent(new WheelEvent("wheel", {deltaY: -gap, bubbles: true}));
            pane.scrollTop = pane.scrollHeight - pane.clientHeight - gap;
            pane.dispatchEvent(new Event("scroll"));
            return {top: pane.scrollTop, height: pane.scrollHeight, gap: pane.scrollHeight - pane.scrollTop - pane.clientHeight};
        }, gap);
        assert.ok(before.top > 0 && before.gap >= gap, "the fixture has a real scrollable chat and the reader has left its bottom");
        await page.evaluate(() => window.receiveMessages([
            {id: 1100, text: "First held arrival"}, {id: 10, text: "Arrival from another machine"}, {id: 1101, text: "Last held arrival"},
        ]));
        await page.waitForTimeout(100);
        const held = await page.locator(".thread-scroll").evaluate((pane) => ({top: pane.scrollTop, height: pane.scrollHeight, text: pane.textContent}));
        assert.equal(held.height, before.height, `${gap}px up: arrivals must not enter the rendered chat`);
        assert.ok(Math.abs(held.top - before.top) <= 0.5, `${gap}px up: the reading position stays fixed`);
        assert.ok(!held.text.includes("held arrival") && !held.text.includes("another machine"), "every incoming message stays held, regardless of its numeric id");
        await page.evaluate(() => window.returnToTab());
        await page.clock.fastForward(65000);
        assert.ok(await page.locator(".thread-scroll").evaluate((pane) => !pane.textContent.includes("held arrival") && !pane.textContent.includes("another machine")), "resting or returning to the tab never releases held messages automatically");
        if (gap === 1) {
            await page.locator(".thread-scroll").evaluate((pane) => {
                pane.dispatchEvent(new WheelEvent("wheel", {deltaY: 100, bubbles: true}));
                pane.scrollTop = pane.scrollHeight;
                pane.dispatchEvent(new Event("scroll"));
            });
        } else {
            await page.locator(".thread-down").click();
        }
        await page.waitForTimeout(20);
        const released = await page.locator(".thread-scroll").evaluate((pane) => ({
            text: pane.textContent, gap: pane.scrollHeight - pane.scrollTop - pane.clientHeight,
            hidden: [...pane.querySelectorAll("[data-ref]")].filter((element) => element.getBoundingClientRect().height === 0 || getComputedStyle(element.closest(".thread-turn") || element).opacity === "0").length,
        }));
        assert.ok(["First held arrival", "Arrival from another machine", "Last held arrival"].every((text) => released.text.includes(text)), "returning to the bottom releases the entire batch");
        assert.equal(released.hidden, 0, "held messages appear together without queued fade-in");
        assert.ok(released.gap <= 1, `the released batch leaves the reader at the bottom, gap ${released.gap}`);
    }
    await page.screenshot({path: "/tmp/held-messages.png"});
    console.log("Scrolling up holds every arrival without movement; returning to the bottom shows the whole batch at once.");
} finally {
    await browser.close();
    await server.close();
}
