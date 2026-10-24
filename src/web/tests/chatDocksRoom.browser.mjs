// Needs a browser and a running journal, so it is not in the default run: node src/web/tests/chatDocksRoom.browser.mjs [journal address] [screenshot path]
// The docks take their own room under the chat's pane: this checkout's viewer, served by vite in a real browser over the live journal with
// every write refused, has docks of a set height put in its foot, none, one and two, with and without the reader's hand on the pane, and
// two frames later the last bubble's bottom is above the docks' top and just above it; a message sent with two docks open lands above
// them, and the page is saved as a screenshot.
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const journal = process.argv[2] || "http://127.0.0.1:8420";
const shot = process.argv[3] || "/tmp/chatDocksRoom.png";
const root = fileURLToPath(new URL("..", import.meta.url));
const server = await createServer({root, logLevel: "silent", server: {port: 0, proxy: {"/journal": journal}}});
await server.listen();
const browser = await chromium.launch();
const failures = [];
const expect = (holds, what) => holds || failures.push(what);
const DOCK_PX = 56;

// the last bubble and the docks, measured two frames after `count` docks are put in the foot, the journal's own hidden, with the
// reader's hand put on the pane first when `hand`
const measure = (page, count, hand = false) =>
    page.evaluate(
        async ([count, height, hand]) => {
            const pane = document.querySelector(".thread-scroll");
            if (hand) pane.dispatchEvent(new PointerEvent("pointerdown", {bubbles: true}));
            const docks = document.querySelector(".chat-docks");
            for (const el of docks.children) if (!el.dataset.probe) el.style.display = "none";
            docks.querySelectorAll("[data-probe]").forEach((el) => el.remove());
            for (let i = 0; i < count; i++) {
                const dock = document.createElement("div");
                dock.dataset.probe = "";
                dock.style.cssText = `height: ${height}px; border: 1px solid #2a6; border-radius: 8px; background: #132a1c; flex: none`;
                docks.append(dock);
            }
            await new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)));
            const bubbles = [...pane.querySelectorAll("[data-ref]")];
            return {
                text: bubbles.at(-1).textContent,
                bottom: bubbles.at(-1).getBoundingClientRect().bottom,
                docksTop: docks.getBoundingClientRect().top,
                docksHeight: docks.offsetHeight,
            };
        },
        [count, DOCK_PX, hand]
    );

try {
    const page = await browser.newPage({viewport: {width: 1280, height: 800}});
    await page.route("**/journal/**", (route) => (route.request().method() === "GET" ? route.continue() : route.abort()));
    await page.goto(server.resolvedUrls.local[0]);
    await page.waitForSelector(".thread-scroll [data-ref]", {timeout: 20000});
    await page.waitForTimeout(2000);

    for (const hand of [false, true]) {
        for (const count of [1, 2, 0, 2]) {
            const seen = await measure(page, count, hand);
            const docked = `with ${count} docks${hand ? " and the reader's hand on the pane" : ""}`;
            expect(seen.docksHeight >= count * DOCK_PX, `${docked} the docks are ${seen.docksHeight}px high`);
            expect(
                seen.bottom <= seen.docksTop + 0.5,
                `${docked} the last bubble ends at ${seen.bottom}, below the docks' top at ${seen.docksTop}`
            );
            expect(
                seen.docksTop - seen.bottom <= 24,
                `${docked} the last bubble ends at ${seen.bottom}, far above the docks' top at ${seen.docksTop}`
            );
        }
        await page.waitForTimeout(800);
    }

    const said = `A message sent with two docks open ${Date.now()}`;
    await page.locator(".thread-write textarea").fill(said);
    await page.locator(".thread-write textarea").press("Enter");
    await page.waitForTimeout(800);
    const sent = await measure(page, 2);
    expect(sent.text.includes(said), `the last bubble reads "${sent.text.slice(0, 80)}", not the message sent`);
    expect(sent.bottom <= sent.docksTop + 0.5, `the message sent ends at ${sent.bottom}, below the docks' top at ${sent.docksTop}`);
    await page.screenshot({path: shot});
} finally {
    await browser.close();
    await server.close();
}

if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
console.log("the last bubble ends above the docks with none, one and two open, and a sent message lands above them");
