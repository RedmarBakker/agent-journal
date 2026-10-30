import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

// A three-second transparent preview of the production hat tip, sampled at 24fps with its exact starting and ending pose.
const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/hat-preview");
const facings = (process.env.FIGURE_FACINGS ?? "0").split(",").map(Number);
const size = Number(process.env.FIGURE_SIZE ?? 192);
const labelHeight = facings.length > 1 ? 24 : 0;
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const frames = await page.evaluate(async ({facings, size, labelHeight}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch(`/voices/figures/${index.butler}`)).arrayBuffer(), "butler", "/voices/figures/draco/");
        const clip = CLIPS.find((each) => each.name === "hat_tip");
        const stage = new Stage();
        const canvas = Object.assign(document.createElement("canvas"), {width: facings.length * size, height: size + labelHeight});
        const cell = Object.assign(document.createElement("canvas"), {width: size, height: size});
        const paint = canvas.getContext("2d");
        return Array.from({length: 72}, (_, frame) => {
            paint.clearRect(0, 0, canvas.width, canvas.height);
            for (const [column, facing] of facings.entries()) {
                for (const material of figure.screens) {
                    delete material.userData.waiting;
                    delete material.userData.shownKey;
                    delete material.userData.frame;
                }
                stage.draw(figure, clip, frame / 71 * (clip.frames - 1), facing, cell);
                paint.drawImage(cell, column * size, 0);
                if (labelHeight) {
                    paint.font = "12px sans-serif";
                    paint.fillStyle = "#d2d4e2";
                    paint.textAlign = "center";
                    paint.fillText(facing === 0 ? "Front" : facing === 90 ? "Side" : `${facing}°`, (column + 0.5) * size, size + 16);
                }
            }
            return canvas.toDataURL("image/png");
        });
    }, {facings, size, labelHeight});
    mkdirSync(resolve(out, "frames"), {recursive: true});
    frames.forEach((png, frame) => writeFileSync(resolve(out, "frames", `frame_${String(frame).padStart(3, "0")}.png`), Buffer.from(png.split(",")[1], "base64")));
    writeFileSync(resolve(out, "preview.json"), `${JSON.stringify({voice: "butler", clip: "hat_tip", facings, width: facings.length * size, height: size + labelHeight, frames: frames.length, fps: 24, seconds: 3, transparent: true, fixedCamera: true, errors}, null, 2)}\n`);
    console.log(JSON.stringify({frames: frames.length, errors}));
    if (errors.length) process.exitCode = 1;
} finally {
    await browser.close();
    await server.close();
}
