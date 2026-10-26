// Before/after review of all five voices on the rope swing in the app's front view, plus the Butler from the side to show the arc.
// FIGURE_ROOT may point at a baseline checkout; its old CSS scaling is included when present. Every voice is checked at the full
// forward/backward arc for canvas clipping. FIGURE_SIDE_VOICES can request other side views, comma separated.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/swing");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});

try {
    const page = await browser.newPage({deviceScaleFactor: 1});
    page.on("console", (message) => {if (message.type() === "log") console.log(message.text());});
    page.on("pageerror", (error) => console.error(error));
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async ({pixels, sideVoices}) => {
        const {ACTS} = await import("/src/figure/acts.js");
        const {CLIPS, GROUND, Stage, figureOf} = await import("/src/figure/figure.js");
        const places = await import("/src/figure/places.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const stage = new Stage();
        const act = ACTS.rope_swing;
        const clip = CLIPS.find((each) => each.name === "rope_swing");
        const cycle = act.hold / act.swings;
        const moments = [
            {frame: 0, label: "sit down"},
            ...[0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1].map((phase) => ({frame: act.intro + phase * cycle, label: `${(phase * 100).toFixed(1)}% cycle`})),
            {frame: clip.frames, label: "settled"},
        ];
        const left = 84;
        const top = 40;
        const row = pixels + 30;
        const margins = [];
        const sheets = [];
        const figures = new Map();
        for (const view of ["front", "side"]) {
            const voices = Object.entries(index).filter(([voice]) => view === "front" || sideVoices.includes(voice));
            const sheet = document.createElement("canvas");
            sheet.width = left + moments.length * pixels;
            sheet.height = top + voices.length * row;
            const paint = sheet.getContext("2d");
            paint.fillStyle = "#15161a";
            paint.fillRect(0, 0, sheet.width, sheet.height);
            paint.fillStyle = "#e8e7ef";
            paint.font = "bold 18px sans-serif";
            paint.fillText(`rope swing · ${view} · ${places.swingView ? "original CSS motion" : "fixed knots and pendulum arc"}`, 12, 26);
            stage.camera.position.set(view === "side" ? 8 : 0, 2.4, view === "front" ? 8 : 0);
            stage.camera.lookAt(0, 2.4, 0);
            stage.camera.updateMatrixWorld(true);
            for (const [voiceRow, [voice, file]] of voices.entries()) {
                if (!figures.has(voice)) figures.set(voice, await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/"));
                const figure = figures.get(voice);
                const y = top + voiceRow * row;
                paint.fillStyle = "#aaadbf";
                paint.font = "13px sans-serif";
                paint.fillText(voice, 8, y + pixels / 2);
                for (const [column, moment] of moments.entries()) {
                    const source = document.createElement("canvas");
                    source.width = source.height = pixels;
                    for (const material of figure.screens) {
                        delete material.userData.waiting;
                        delete material.userData.shownKey;
                        delete material.userData.frame;
                    }
                    stage.draw(figure, clip, moment.frame, 0, source, {posture: "sit"});
                    const canvas = document.createElement("canvas");
                    canvas.width = canvas.height = pixels;
                    const context = canvas.getContext("2d");
                    if (places.swingView) {
                        const swing = places.swingView(moment.frame / clip.frames, GROUND);
                        context.translate(swing.origin.x * pixels, swing.origin.y * pixels);
                        context.scale(swing.scale, swing.scale);
                        context.translate(-swing.origin.x * pixels, -swing.origin.y * pixels);
                    }
                    context.drawImage(source, 0, 0);
                    const x = left + column * pixels;
                    paint.drawImage(canvas, x, y);
                    paint.fillStyle = "#aaadbf";
                    paint.font = "12px monospace";
                    paint.fillText(moment.label, x + 20, y + pixels + 18);
                    if (view !== "front") continue;
                    const data = canvas.getContext("2d").getImageData(0, 0, pixels, pixels).data;
                    const bounds = {left: pixels, right: 0, top: pixels, bottom: 0};
                    for (let py = 0; py < pixels; py++) {
                        for (let px = 0; px < pixels; px++) {
                            if (data[(py * pixels + px) * 4 + 3] < 24) continue;
                            bounds.left = Math.min(bounds.left, px);
                            bounds.right = Math.max(bounds.right, px);
                            bounds.top = Math.min(bounds.top, py);
                            bounds.bottom = Math.max(bounds.bottom, py);
                        }
                    }
                    margins.push({voice, frame: moment.frame, label: moment.label, left: bounds.left, right: pixels - 1 - bounds.right, top: bounds.top, bottom: pixels - 1 - bounds.bottom});
                }
                console.log(`${voice}: swing ${view} rendered`);
            }
            sheets.push({name: `swing_${view}`, png: sheet.toDataURL("image/png")});
        }
        return {sheets, margins, pixels};
    }, {pixels: Number(process.env.FIGURE_SIZE ?? 192), sideVoices: (process.env.FIGURE_SIDE_VOICES ?? "butler").split(",").filter(Boolean)});
    mkdirSync(out, {recursive: true});
    for (const sheet of result.sheets) {
        const path = `${out}/${sheet.name}.png`;
        mkdirSync(dirname(path), {recursive: true});
        writeFileSync(path, Buffer.from(sheet.png.split(",")[1], "base64"));
        console.log(path);
    }
    writeFileSync(`${out}/swing_margins.json`, JSON.stringify({pixels: result.pixels, margins: result.margins}, null, 4));
    const clipped = result.margins.filter((item) => Math.min(item.left, item.right, item.top, item.bottom) < 2);
    if (errors.length || clipped.length) throw new Error(JSON.stringify({errors, clipped}));
    console.log(`All ${result.margins.length} front-view samples retain at least 2 pixels of clear canvas.`);
} finally {
    await browser.close();
    await server.close();
}
