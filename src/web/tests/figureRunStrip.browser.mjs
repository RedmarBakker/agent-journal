import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/run");
const sourceHash = createHash("sha256");
for (const file of ["src/figure/figure.js", "src/figure/gait.js", "src/figure/player.js", "src/figure/propTransition.js"]) sourceHash.update(file).update(readFileSync(resolve(root, file)));
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => { if (message.type() === "log") console.log(message.text()); });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const named = (name) => CLIPS.find((clip) => clip.name === name);
        const stage = new Stage();
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const images = [], metrics = [], models = {};
        const canvasOf = (width, height = width) => Object.assign(document.createElement("canvas"), {width, height});
        const backdrop = (canvas) => {
            const paint = canvas.getContext("2d");
            paint.fillStyle = "#15161a";
            paint.fillRect(0, 0, canvas.width, canvas.height);
            paint.fillStyle = "#d2d4e2";
            paint.font = "12px sans-serif";
            return paint;
        };
        const edgePixels = (canvas) => {
            const size = canvas.width, pixels = canvas.getContext("2d").getImageData(0, 0, size, size).data;
            let touched = 0;
            for (let at = 0; at < size; at++) for (const point of [at, (size - 1) * size + at, at * size, at * size + size - 1]) if (pixels[point * 4 + 3] > 32) touched++;
            return touched;
        };
        const all = canvasOf(96 + 8 * 128, 36 + Object.keys(files).length * 2 * 148);
        const paintAll = backdrop(all);
        let allRow = 0;
        for (const [voice, file] of Object.entries(files)) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            models[voice] = figure;
            const sheet = canvasOf(96 + 8 * 160, 36 + 2 * 180);
            const paint = backdrop(sheet);
            paint.fillText(`${voice} · run cycle`, 8, 22);
            for (const [row, facing] of [90, 270].entries()) {
                paint.fillText(`${facing}°`, 8, 36 + row * 180 + 80);
                paintAll.fillText(`${voice} ${facing}°`, 8, 36 + allRow * 148 + 64);
                for (let sample = 0; sample < 8; sample++) {
                    const cell = canvasOf(160);
                    const moves = stage.draw(figure, named("run"), sample / 8 * named("run").frames, facing, cell);
                    const soles = ["l", "r"].map((side) => figure.rig.heads.get(`foot_${side}`).clone().applyMatrix4(moves.get(`foot_${side}`)).z);
                    metrics.push({voice, facing, phase: sample / 8, edges: edgePixels(cell), soles});
                    paint.drawImage(cell, 96 + sample * 160, 36 + row * 180);
                    paintAll.drawImage(cell, 96 + sample * 128, 36 + allRow * 148, 128, 128);
                    paint.fillText(`${sample + 1}/8`, 96 + sample * 160 + 65, 36 + row * 180 + 174);
                }
                allRow++;
            }
            images.push({name: `${voice}_run.png`, png: sheet.toDataURL("image/png")});
            console.log(`${voice}: run both directions rendered`);
        }
        images.push({name: "all_voices_run.png", png: all.toDataURL("image/png")});
        const butler = models.butler;
        for (let frame = 0; frame < 24; frame++) {
            const sheet = canvasOf(2 * 160, 196);
            const paint = backdrop(sheet);
            for (const [column, name] of ["walk", "run"].entries()) {
                paint.fillText(name === "walk" ? "Walk cycle" : "Run cycle", column * 160 + 50, 24);
                const cell = canvasOf(160);
                stage.draw(butler, named(name), frame / 24 * named(name).frames, 90, cell);
                paint.drawImage(cell, column * 160, 36);
            }
            images.push({name: `comparison/frame_${String(frame).padStart(3, "0")}.png`, png: sheet.toDataURL("image/png")});
        }
        return {images, metrics};
    });
    mkdirSync(out, {recursive: true});
    mkdirSync(resolve(out, "comparison"), {recursive: true});
    for (const image of result.images) writeFileSync(resolve(out, image.name), Buffer.from(image.png.split(",")[1], "base64"));
    for (const metric of result.metrics) if (metric.edges) errors.push(`run touches frame edge: ${JSON.stringify(metric)}`);
    writeFileSync(resolve(out, "cycle_checks.json"), `${JSON.stringify({sourceHash: sourceHash.digest("hex"), sampleCount: result.metrics.length, samples: result.metrics, errors}, null, 2)}\n`);
    console.log(JSON.stringify({runSamples: result.metrics.length, errors}));
    if (errors.length) process.exitCode = 1;
} finally {
    await browser.close();
    await server.close();
}
