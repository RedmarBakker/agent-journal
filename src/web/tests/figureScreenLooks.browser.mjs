import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

// The same screen targets before and after the fix: a short glance, the composer and bar, then a sustained read to either side and
// straight behind. FIGURE_ROOT selects a saved version without changing the poses used for the comparison.
const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/screen-looks");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});

try {
    const page = await browser.newPage({deviceScaleFactor: 1});
    page.on("pageerror", (error) => console.error(error));
    page.on("console", (message) => { if (message.type() === "log") console.log(message.text()); });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const png = await page.evaluate(async ({voices, size}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {headBlend, looksFor} = await import("/src/figure/looks.js");
        const {readingFacing} = await import("/src/figure/reactions.js");
        const all = await (await fetch("/voices/figures/figures.json")).json();
        const entries = Object.entries(all).filter(([voice]) => !voices.length || voices.includes(voice));
        const moments = [
            {label: "Message glance", kind: "said", x: 0.65, y: 0.25},
            {label: "Composer", kind: "typing", x: 0.8, y: 1.0},
            {label: "Progress bar", kind: "bar", x: 0.65, y: 0.75},
            {label: "Read left", kind: "reading", x: -0.2, y: 0.25, reading: true},
            {label: "Read above", kind: "reading", x: 0.5, y: 0.12, reading: true},
            {label: "Read right", kind: "reading", x: 1.2, y: 0.25, reading: true},
        ];
        const margin = 84;
        const header = 42;
        const rowHeight = size + 12;
        const sheet = document.createElement("canvas");
        sheet.width = margin + size * moments.length;
        sheet.height = header + rowHeight * entries.length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        paint.font = "13px sans-serif";
        paint.fillStyle = "#d2d4e2";
        for (const [column, moment] of moments.entries()) paint.fillText(moment.label, margin + column * size + 12, 26);
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "idle");
        for (const [row, [voice, file]] of entries.entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            paint.fillStyle = "#aaadbf";
            paint.fillText(voice, 8, header + row * rowHeight + size * 0.5);
            for (const [column, moment] of moments.entries()) {
                const point = {x: moment.x, y: moment.y};
                const look = looksFor(clip, [{key: moment.kind, kind: moment.kind, point}])[0];
                const facing = moment.reading ? readingFacing({left: point.x * size - 18, right: point.x * size + 18}, size / 2, size) : 0;
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = size;
                stage.draw(figure, clip, 0, facing, canvas, {at: {...look.point, amount: headBlend(look, clip)}});
                paint.drawImage(canvas, margin + column * size, header + row * rowHeight);
            }
            console.log(`${voice}: screen looks rendered`);
        }
        return sheet.toDataURL("image/png");
    }, {voices: (process.env.FIGURE_VOICES ?? "").split(",").filter(Boolean), size: Number(process.env.FIGURE_SIZE ?? 200)});
    const path = `${out}/screen_looks.png`;
    mkdirSync(dirname(path), {recursive: true});
    writeFileSync(path, Buffer.from(png.split(",")[1], "base64"));
    console.log(path);
} finally {
    await browser.close();
    await server.close();
}
