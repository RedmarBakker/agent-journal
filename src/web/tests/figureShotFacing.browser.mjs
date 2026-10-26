// Render the same side-wall and top-wall firing poses before and after a change. FIGURE_ROOT may point at a baseline checkout.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/shooting-facing.png");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage({deviceScaleFactor: 1});
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const png = await page.evaluate(async ({voices, size}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const all = await (await fetch("/voices/figures/figures.json")).json();
        const index = Object.entries(all).filter(([name]) => !voices.length || voices.includes(name));
        const cases = [
            {label: "Left wall", target: {x: -1.4, y: 0.2, back: 0}},
            {label: "Right wall", target: {x: 2.2, y: 0.35, back: 0}},
            {label: "Top wall / behind", target: {x: 0.3, y: -1.6, back: 1}},
        ];
        const sheet = document.createElement("canvas");
        sheet.width = 80 + cases.length * size;
        sheet.height = 36 + index.length * size;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        paint.fillStyle = "#dddfea";
        paint.font = "13px sans-serif";
        cases.forEach(({label}, i) => paint.fillText(label, 84 + i * size, 23));
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "bug_shot");
        for (const [row, [voice, file]] of index.entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            paint.fillText(voice, 8, 36 + row * size + size / 2);
            for (const [column, {target}] of cases.entries()) {
                const cell = document.createElement("canvas");
                cell.width = cell.height = size;
                stage.draw(figure, clip, clip.frames * 0.36, 0, cell, {target});
                paint.drawImage(cell, 80 + column * size, 36 + row * size);
            }
        }
        return sheet.toDataURL("image/png");
    }, {voices: (process.env.FIGURE_VOICES ?? "butler").split(",").filter(Boolean), size: Number(process.env.FIGURE_SIZE ?? 224)});
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(png.split(",")[1], "base64"));
    console.log(out);
} finally {
    await browser.close();
    await server.close();
}
