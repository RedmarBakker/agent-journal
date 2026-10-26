// Needs a browser, so it is not in the default run: node tests/figureSlushStrip.browser.mjs [output PNG, default tests/strips/slush-strip.png]
// A strip of a shot bug's burst in a real browser: the bug on the left wall of a 900 by 700 window, then the slush flying out and falling,
// the splashes sticking to the chat's boxes and running down them, the splashes fading away, and drops on the camera's glass. The same
// FigureAct the chat draws, one cell for each moment, written as one PNG. FIGURE_ROOT can render an earlier copy for comparison.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, join} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = process.argv[2] ?? join(root, "tests", "strips", "slush-strip.png");
const imports = {
    name: "slush-strip-imports",
    resolveId: (id) => id === "/slush-strip-imports.js" ? id : null,
    load: (id) => id === "/slush-strip-imports.js" ? 'export {createApp, h, nextTick} from "vue"; export {default as FigureAct} from "/src/chat/FigureAct.vue";' : null,
};
const server = await createServer({root, plugins: [imports], logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox"]});
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {createApp, h, nextTick, FigureAct} = await import("/slush-strip-imports.js");
        const {ACTS, bugShotScene, bugShotTimes, sprayesCamera} = await import("/src/figure/acts.js");
        const world = {left: 0, top: 0, right: 900, bottom: 700};
        const SIZE = 112;
        const at = {x: 450 - SIZE / 2, y: 560 - SIZE};
        // a bug on the left wall chosen for the camera splash
        const bug = [0.3, 0.9, 0.5, 0.1].map((along) => ({wall: "left", along, way: 0})).find(sprayesCamera);
        const surfaces = [
            {id: "bubble", left: 85, right: 420, top: 320, bottom: 430, text: "A message in the chat"},
            {id: "card", left: 95, right: 425, top: 245, bottom: 295, text: "A nearby task card"},
            {id: "composer", left: 24, right: 876, top: 560, bottom: 675, text: "Write a message..."},
        ];
        const shot = bugShotTimes(0).shot;
        const seconds = [-0.2, 0.12, 0.4, 1.0, 1.8, 4.0];
        const cell = {width: 300, height: 233};
        const sheet = document.createElement("canvas");
        sheet.width = cell.width * seconds.length;
        sheet.height = cell.height + 28;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#1b1d21";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        let counts = [];
        for (const [index, offset] of seconds.entries()) {
            const scene = bugShotScene([bug], world, (shot + offset) * ACTS.bug_shot.fps, {surfaces});
            const scale = cell.width / world.right;
            paint.save();
            paint.translate(index * cell.width, 28);
            paint.scale(scale, scale);
            for (const surface of surfaces) {
                paint.fillStyle = "#292d35";
                paint.strokeStyle = "#636875";
                paint.lineWidth = 2;
                paint.beginPath();
                paint.roundRect(surface.left, surface.top, surface.right - surface.left, surface.bottom - surface.top, 10);
                paint.fill();
                paint.stroke();
                paint.fillStyle = "#c9ccd7";
                paint.font = "19px sans-serif";
                paint.fillText(surface.text, surface.left + 16, surface.top + 32);
                paint.fillStyle = "#808796";
                paint.fillRect(surface.left + 16, surface.top + 53, Math.min(260, surface.right - surface.left - 32), 4);
            }
            paint.restore();
            paint.fillStyle = "#c9ccd7";
            paint.font = "13px monospace";
            paint.fillText(`${offset.toFixed(2)}s after hit`, index * cell.width + 10, 19);
            const rel = (point) => ({x: point.x - at.x, y: point.y - at.y});
            const host = document.createElement("div");
            const picture = {pictures: ["data:image/gif;base64,R0lGODlhAQABAAAAACw=", "data:image/gif;base64,R0lGODlhAQABAAAAACw="], width: 20, height: 12, at: {x: 10, y: 11}};
            const app = createApp({render: () => h(FigureAct, {name: "bug_shot", u: 0.5, hand: {x: 0.6, y: 0.5, out: 1, other: {x: 0.4, y: 0.5}}, head: {x: 0.5, y: 0.3}, feet: 0.95, size: SIZE, room: {left: 0, right: 0}, bug: picture, wallBugs: scene.bugs.map((each) => ({...each, ...rel(each)})), slush: scene.slush.map((each) => ({...each, ...rel(each), ...(each.clip ? {clip: {left: each.clip.left - at.x, right: each.clip.right - at.x, top: each.clip.top - at.y, bottom: each.clip.bottom - at.y}} : {})})), camera: scene.camera.map((each) => ({...each, from: rel(each.from)}))})});
            app.mount(host);
            await nextTick();
            const svg = host.querySelector("svg");
            svg.setAttribute("viewBox", `${at.x * -1} ${at.y * -1} ${world.right} ${world.bottom}`);
            svg.setAttribute("width", cell.width);
            svg.setAttribute("height", cell.height);
            counts.push({offset, flying: host.querySelectorAll("[data-act-slush]").length, splashes: host.querySelectorAll("[data-act-splash]").length, lens: host.querySelectorAll("[data-act-lens]").length, surfaces: host.querySelectorAll("[data-act-surface]").length, runs: host.querySelectorAll("[data-act-surface] [data-act-run]").length});
            const image = new Image();
            image.src = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)], {type: "image/svg+xml"}));
            await image.decode();
            paint.drawImage(image, index * cell.width, 28);
            app.unmount();
        }
        return {png: sheet.toDataURL("image/png"), counts};
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.png.split(",")[1], "base64"));
    const [before, burst, , , landed, gone] = strip.counts;
    if (before.flying || before.splashes) failures.push("slush before the shot");
    if (!burst.flying) failures.push("no slush flying at the burst");
    if (!landed.splashes) failures.push("no splash where slush landed");
    if (gone.splashes) failures.push("the splashes did not fade away");
    if (!strip.counts.some((cell) => cell.lens)) failures.push("no drop on the camera for a bug chosen for it");
    if (process.env.FIGURE_EXPECT_SURFACES !== "0" && !strip.counts.some((cell) => cell.surfaces && cell.runs)) failures.push("no splatter running down the chat boxes");
    console.log(JSON.stringify(strip.counts));
    console.log(`strip written to ${out}`);
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
