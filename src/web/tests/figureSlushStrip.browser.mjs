// Needs a browser, so it is not in the default run: node src/web/tests/figureSlushStrip.browser.mjs [where the strip is written, default src/web/tests/strips/slush-strip.png]
// A strip of a shot bug's burst in a real browser: the bug on the left wall of a 900 by 700 window, then the slush flying out and falling,
// the splashes it leaves on the floor and the edges, the splashes fading away, and, for a bug chosen for it, drops on the camera's glass
// sliding down and fading. The same FigureAct the chat draws, one cell for each moment, written as one PNG.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, join} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = fileURLToPath(new URL("..", import.meta.url));
const out = process.argv[2] ?? join(root, "tests", "strips", "slush-strip.png");
const server = await createServer({root, logLevel: "silent", server: {port: 0}});
await server.listen();
const browser = await chromium.launch();
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {createApp, h, nextTick} = await import("/node_modules/.vite/deps/vue.js").catch(() => import("vue"));
        const {default: FigureAct} = await import("/src/chat/FigureAct.vue");
        const {ACTS, bugShotScene, bugShotTimes, sprayesCamera} = await import("/src/figure/acts.js");
        const world = {left: 0, top: 0, right: 900, bottom: 700};
        const SIZE = 112;
        const at = {x: 450 - SIZE / 2, y: 560 - SIZE};
        // a bug on the left wall chosen for the camera splash
        const bug = [0.9, 0.5, 0.3, 0.1].map((along) => ({wall: "left", along, way: 0})).find(sprayesCamera);
        const shot = bugShotTimes(0).shot;
        const seconds = [-0.2, 0.2, 0.5, 1.0, 2.0, 3.5];
        const cell = {width: 300, height: 233};
        const sheet = document.createElement("canvas");
        sheet.width = cell.width * seconds.length;
        sheet.height = cell.height;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#1b1d21";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        let counts = [];
        for (const [index, offset] of seconds.entries()) {
            const scene = bugShotScene([bug], world, (shot + offset) * ACTS.bug_shot.fps);
            const rel = (point) => ({x: point.x - at.x, y: point.y - at.y});
            const host = document.createElement("div");
            const picture = {pictures: ["data:image/gif;base64,R0lGODlhAQABAAAAACw=", "data:image/gif;base64,R0lGODlhAQABAAAAACw="], width: 20, height: 12, at: {x: 10, y: 11}};
            const app = createApp({render: () => h(FigureAct, {name: "bug_shot", u: 0.5, hand: {x: 0.6, y: 0.5, out: 1, other: {x: 0.4, y: 0.5}}, head: {x: 0.5, y: 0.3}, feet: 0.95, size: SIZE, room: {left: 0, right: 0}, bug: picture, wallBugs: scene.bugs.map((each) => ({...each, ...rel(each)})), slush: scene.slush.map((each) => ({...each, ...rel(each)})), camera: scene.camera.map((each) => ({...each, from: rel(each.from)}))})});
            app.mount(host);
            await nextTick();
            const svg = host.querySelector("svg");
            svg.setAttribute("viewBox", `${at.x * -1} ${at.y * -1} ${world.right} ${world.bottom}`);
            svg.setAttribute("width", cell.width);
            svg.setAttribute("height", cell.height);
            counts.push({offset, flying: host.querySelectorAll("[data-act-slush]").length, splashes: host.querySelectorAll("[data-act-splash]").length, lens: host.querySelectorAll("[data-act-lens]").length});
            const image = new Image();
            image.src = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)], {type: "image/svg+xml"}));
            await image.decode();
            paint.drawImage(image, index * cell.width, 0);
            app.unmount();
        }
        return {png: sheet.toDataURL("image/png"), counts};
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.png.split(",")[1], "base64"));
    const [before, burst, , landed, , gone] = strip.counts;
    if (before.flying || before.splashes) failures.push("slush before the shot");
    if (!burst.flying) failures.push("no slush flying at the burst");
    if (!landed.splashes) failures.push("no splash where slush landed");
    if (gone.splashes) failures.push("the splashes did not fade away");
    if (!strip.counts.some((cell) => cell.lens)) failures.push("no drop on the camera for a bug chosen for it");
    console.log(`strip written to ${out}`);
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
