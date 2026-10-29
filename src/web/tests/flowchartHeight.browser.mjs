// Needs a browser: node src/web/tests/flowchartHeight.browser.mjs [screenshot path]
import assert from "node:assert/strict";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = fileURLToPath(new URL("..", import.meta.url));
const entry = "/flowchart-height-entry.js";
const server = await createServer({
    root,
    logLevel: "error",
    server: {host: "127.0.0.1", port: 0},
    plugins: [{
        name: "flowchart-height-page",
        resolveId: (id) => id === entry ? entry : null,
        load: (id) => id === entry ? `
            import {createApp, h} from "vue";
            import FlowchartMark from "/src/chat/FlowchartMark.vue";
            import "/src/tokens.css";
            createApp({render: () => h(FlowchartMark, {
                title: "How a request is handled", time: 0,
                edges: [["Request arrives", "Read the request", ""], ["Read the request", "Do the work", ""], ["Do the work", "Check the result", ""], ["Check the result", "Finished", ""]]
            })}).mount("#app");
        ` : null,
        configureServer(server) {
            server.middlewares.use("/flowchart-height.html", (request, response) => {
                response.setHeader("Content-Type", "text/html");
                response.end(`<html><body><div id="app"></div><script type="module" src="${entry}"></script></body></html>`);
            });
        },
    }],
});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH});

try {
    const page = await browser.newPage();
    for (const viewport of [{width: 1440, height: 1200}, {width: 1280, height: 600}, {width: 390, height: 844}]) {
        await page.setViewportSize(viewport);
        await page.goto(new URL("flowchart-height.html", server.resolvedUrls.local[0]).href);
        await page.locator(".flowchart-open").click();
        await page.locator(".dialog-panel").waitFor();
        await page.emulateMedia({reducedMotion: "reduce"});
        await page.locator(".dialog-enter-active").waitFor({state: "detached"});
        const sizes = await page.evaluate(() => {
            const body = document.querySelector(".dialog-body");
            const frame = document.querySelector(".flowchart-frame").getBoundingClientRect();
            const tools = document.querySelector(".flowchart-tools").getBoundingClientRect();
            const panel = document.querySelector(".dialog-panel").getBoundingClientRect();
            const bounds = body.getBoundingClientRect();
            const css = getComputedStyle(body);
            return {
                frame: {width: frame.width, height: frame.height},
                available: {
                    width: bounds.width - parseFloat(css.paddingLeft) - parseFloat(css.paddingRight),
                    height: bounds.bottom - parseFloat(css.paddingBottom) - tools.bottom - parseFloat(getComputedStyle(document.querySelector(".flowchart-tools")).marginBottom),
                },
                overflows: body.scrollHeight > body.clientHeight + 1,
                panelHeight: panel.height,
            };
        });
        assert.ok(Math.abs(sizes.frame.height - sizes.available.height) <= 1, `${viewport.height}px window: chart height ${sizes.frame.height}, available ${sizes.available.height}`);
        assert.ok(Math.abs(sizes.frame.width - sizes.available.width) <= 1, "chart fills the body width");
        assert.equal(sizes.overflows, false, "chart and controls fit without scrolling");
        assert.ok(sizes.panelHeight >= viewport.height - 46, "dialog fills the window height");
    }
    await page.setViewportSize({width: 1440, height: 1200});
    await page.reload();
    await page.locator(".flowchart-open").click();
    await page.locator(".dialog-enter-active").waitFor({state: "detached"});
    await page.screenshot({path: process.argv[2] || "/tmp/flowchart-height.png"});
    console.log("The chart fills its dialog at tall, short and phone sizes without scrolling; fresh page screenshot saved.");
} finally {
    await browser.close();
    await server.close();
}
