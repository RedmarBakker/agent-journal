// Render one complete line and its return for every voice: node tests/figureReadingStrip.browser.mjs reading.png.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, join, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_PROJECT_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = process.argv[2] ?? join(root, "tests", "strips", "reading-line-strip.png");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE_PATH || process.env.CHROMIUM_PATH || undefined, args: ["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    page.on("pageerror", (error) => failures.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {CLIPS, LOOK_REACH, Stage, eyesAboveOf, figureOf, headPivotOf} = await import("/src/figure/figure.js");
        const {READING, gazeAfter, readingAt} = await import("/src/figure/reactions.js");
        const {lookInFigure} = await import("/src/figure/looks.js");
        const manifest = await (await fetch("/voices/figures/figures.json")).json();
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "idle");
        const size = 224;
        const header = 50;
        const footer = 25;
        const cell = size + header + footer;
        const phases = [0, 0.16, 0.32, 0.48, 0.57, 0.7, 0.84, 1];
        const sheet = document.createElement("canvas");
        sheet.width = size * phases.length;
        sheet.height = cell * Object.keys(manifest).length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const frames = [];
        const facing = 90;
        for (const [row, [voice, filename]] of Object.entries(manifest).entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${filename}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            const origin = {x: 0, y: 0};
            const center = {x: size / 2, y: size * headPivotOf(figure)};
            const head = {depth: LOOK_REACH * size, above: eyesAboveOf(figure) * size, tip: {up: 25, down: 35}, facing};
            const box = {left: -size * 0.4, right: size * 1.5, top: center.y - 2, bottom: center.y + 100};
            let gaze = {point: null, amount: 0, at: 1};
            for (let warm = 1; warm <= 60; warm++) gaze = gazeAfter(gaze, readingAt(box, 0), center, 1 + warm * 1000 / 60, head, 1);
            let next = 0;
            for (let frame = 0; frame <= Math.ceil(READING.sweep * 60); frame++) {
                const seconds = frame / 60;
                const point = readingAt(box, seconds);
                gaze = gazeAfter(gaze, point, center, 1001 + frame * 1000 / 60, head, 1);
                if (next >= phases.length || seconds + 1e-8 < phases[next] * READING.sweep) continue;
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = size;
                for (const material of figure.screens) {
                    delete material.userData.waiting;
                    delete material.userData.shownKey;
                    delete material.userData.frame;
                }
                stage.draw(figure, clip, 0, facing, canvas, {posture: "sit", at: lookInFigure(gaze, origin, size)});
                const x = next * size;
                const y = row * cell;
                paint.fillStyle = "#20222a";
                paint.fillRect(x + 12, y + 10, size - 24, 30);
                paint.strokeStyle = "#5b5f70";
                paint.lineWidth = 2;
                for (let line = 0; line < 2; line++) {
                    paint.beginPath();
                    paint.moveTo(x + 23, y + 20 + line * 10);
                    paint.lineTo(x + size - 23, y + 20 + line * 10);
                    paint.stroke();
                }
                const across = (point.x - box.left - READING.inset) / (box.right - box.left - 2 * READING.inset);
                const down = (point.y - box.top - READING.inset) / READING.line;
                paint.fillStyle = "#a5a8ff";
                paint.beginPath();
                paint.arc(x + 23 + across * (size - 46), y + 20 + down * 10, 3.5, 0, 2 * Math.PI);
                paint.fill();
                paint.drawImage(canvas, x, y + header);
                paint.fillStyle = "#b8bbc9";
                paint.font = "12px sans-serif";
                const label = seconds < READING.sweep - READING.returnSeconds ? "reading" : seconds < READING.sweep ? "return" : "next line";
                paint.fillText(`${voice} · ${seconds.toFixed(2)}s · ${label}`, x + 12, y + header + size + 16);
                frames.push({voice, seconds, yaw: gaze.point.readingYaw, shoulders: gaze.point.readingFollow});
                next++;
            }
        }
        stage.renderer.dispose();
        stage.screenRenderer.dispose();
        return {png: sheet.toDataURL("image/png"), frames};
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.png.split(",")[1], "base64"));
    if (strip.frames.length !== 40) failures.push(`expected 40 images, drew ${strip.frames.length}`);
    console.log(`Reading strip written to ${out}; ${strip.frames.length} frames, all five voices.`);
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
