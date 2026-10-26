// Render the confession for all five voices: FIGURE_PROJECT_ROOT=/path/to/project node tests/figureRepentStrip.browser.mjs out.png.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, join, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_PROJECT_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = process.argv[2] ?? join(root, "tests", "strips", "repent-strip.png");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE_PATH || process.env.CHROMIUM_PATH || undefined, args: ["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    page.on("pageerror", (error) => failures.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async ({voices, facing}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const manifest = await (await fetch("/voices/figures/figures.json")).json();
        const index = Object.fromEntries(Object.entries(manifest).filter(([voice]) => !voices.length || voices.includes(voice)));
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "repent");
        const size = 224;
        const label = 24;
        const moments = [0, 0.12, 0.2, 0.28, 0.38, 0.52, 0.66, 0.78, 0.9, (clip.frames - 1) / clip.frames];
        const sheet = document.createElement("canvas");
        sheet.width = size * moments.length;
        sheet.height = (size + label) * Object.keys(index).length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#1b1d21";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const drawn = [];
        for (const [row, [voice, filename]] of Object.entries(index).entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${filename}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            for (const [column, u] of moments.entries()) {
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = size;
                const frame = Math.min(Math.floor(u * clip.frames), clip.frames - 1);
                for (const material of figure.screens) {
                    delete material.userData.waiting;
                    delete material.userData.shownKey;
                    delete material.userData.frame;
                }
                stage.draw(figure, clip, frame, facing, canvas);
                paint.drawImage(canvas, column * size, row * (size + label));
                paint.fillStyle = "#a9adb9";
                paint.font = "12px sans-serif";
                paint.fillText(`${voice} · ${(u * 100).toFixed(0)}%`, column * size + 12, row * (size + label) + size + 16);
                drawn.push(frame);
            }
        }
        stage.renderer.dispose();
        stage.screenRenderer.dispose();
        return {png: sheet.toDataURL("image/png"), drawn, cells: moments.length};
    }, {voices: (process.env.REPENT_VOICES ?? "").split(",").filter(Boolean), facing: Number(process.env.REPENT_FACING ?? 32)});
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.png.split(",")[1], "base64"));
    if (new Set(strip.drawn).size !== strip.cells) failures.push("two cells drew the same frame");
    console.log(`strip written to ${out}`);
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
