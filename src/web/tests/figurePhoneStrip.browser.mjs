// Render the call from its actual models, including the seat and either side of the handset.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.argv[3] ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/phone-call.png");
const server = await createServer({root, configFile: false, logLevel: "silent", define: {__DEMO__: false}, server: {port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || undefined, args: ["--no-sandbox", "--enable-unsafe-swiftshader"]});

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const clip = CLIPS.find((each) => each.name === "phone_call");
        const stage = new Stage();
        const rows = [
            ["butler", "stand", 0, 1], ["butler", "sit", 0, -1], ["butler", "sit", 70, -1],
            ["butler", "composed", 0, 1], ["homie", "stand", 25, 1], ["coach", "sit", 0, 1],
            ["colleague", "composed", 25, -1], ["squire", "stand", -25, 1],
        ];
        const size = 256;
        const heading = 30;
        const moments = [0, 0.17, 0.24, 0.36, 0.45, 0.56, 0.64, 0.78, 0.84, 1];
        const sheet = document.createElement("canvas");
        sheet.width = size * moments.length;
        sheet.height = (size + heading) * rows.length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#1b1d21";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const figures = new Map();
        for (const [row, [voice, posture, facing, phoneWay]] of rows.entries()) {
            if (!figures.has(voice)) figures.set(voice, await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/"));
            paint.fillStyle = "#d8dde8";
            paint.font = "15px sans-serif";
            paint.fillText(`${voice} · ${posture} · ${facing}° · phone ${phoneWay < 0 ? "left" : "right"}`, 12, row * (size + heading) + 21);
            for (const [column, u] of moments.entries()) {
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = size;
                const figure = figures.get(voice);
                for (const material of figure.screens) {
                    delete material.userData.waiting;
                    delete material.userData.shownKey;
                    delete material.userData.frame;
                }
                stage.draw(figure, clip, u * (clip.frames - 1), facing, canvas, {posture, phoneWay});
                paint.drawImage(canvas, column * size, row * (size + heading) + heading);
                paint.fillStyle = "#8e98aa";
                paint.fillText(`${Math.round(u * 100)}%`, column * size + 8, (row + 1) * (size + heading) - 9);
            }
        }
        return sheet.toDataURL("image/png");
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.split(",")[1], "base64"));
    console.log(`Phone strip written to ${out}`);
} finally {
    await browser.close();
    await server.close();
}
