import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/combat");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});

try {
    const page = await browser.newPage({deviceScaleFactor: 1});
    page.on("pageerror", (error) => console.error(error));
    page.on("console", (message) => {if (message.type() === "log") console.log(message.text());});
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strips = await page.evaluate(async ({voices, pixels}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {ACTS, smashAt, smashPlan} = await import("/src/figure/acts.js");
        const all = await (await fetch("/voices/figures/figures.json")).json();
        const index = Object.fromEntries(Object.entries(all).filter(([name]) => !voices.length || voices.includes(name)));
        const stage = new Stage();
        const size = pixels;
        const label = 28;
        const header = 36;
        const margin = 76;
        const moments = {
            bug_shot: [0, 0.11, 0.165, 0.22, 0.32, 0.335, 0.35, 0.411, 0.43, 0.9],
            bug_smash: [0.16, 0.26, 0.4, 0.46, 0.58, 0.66, 0.7, 0.72, 0.755, 0.95],
            work: [0, 0.08, 0.24, 0.3, 0.34, 0.4, 0.432, 0.46, 0.75, 0.999],
        };
        const sheets = Object.fromEntries(Object.keys(moments).map((name) => {
            const sheet = document.createElement("canvas");
            sheet.width = margin + moments[name].length * size;
            sheet.height = header + Object.keys(index).length * (size + label);
            const paint = sheet.getContext("2d");
            paint.fillStyle = "#15161a";
            paint.fillRect(0, 0, sheet.width, sheet.height);
            paint.fillStyle = "#e8e7ef";
            paint.font = "bold 17px sans-serif";
            paint.fillText(name, 12, 24);
            return [name, sheet];
        }));
        for (const [row, [voice, file]] of Object.entries(index).entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            for (const [name, times] of Object.entries(moments)) {
                const clip = CLIPS.find((entry) => entry.name === name);
                const sheet = sheets[name];
                const paint = sheet.getContext("2d");
                const y = header + row * (size + label);
                paint.fillStyle = "#aaadbf";
                paint.font = "13px sans-serif";
                paint.fillText(voice, 8, y + size * 0.48);
                for (const [column, u] of times.entries()) {
                    const canvas = document.createElement("canvas");
                    canvas.width = canvas.height = size;
                    const frame = u * clip.frames;
                    let options = {};
                    if (name === "bug_shot") options = {target: {x: 2.2, y: 0.35}};
                    if (name === "bug_smash") {
                        const plan = smashPlan(340, {left: 0, right: 1000}, 112);
                        const at = smashAt(plan, u, 112);
                        options = {walkWay: at.way, stride: at.steps};
                    }
                    for (const material of figure.screens) {
                        delete material.userData.waiting;
                        delete material.userData.shownKey;
                        delete material.userData.frame;
                    }
                    stage.draw(figure, clip, frame, 0, canvas, options);
                    const x = margin + column * size;
                    paint.strokeStyle = "#333643";
                    paint.beginPath();
                    paint.moveTo(x + 8, y + size * 0.9444);
                    paint.lineTo(x + size - 8, y + size * 0.9444);
                    paint.stroke();
                    paint.drawImage(canvas, x, y);
                    paint.fillStyle = "#aaadbf";
                    paint.font = "12px monospace";
                    paint.fillText(`${u.toFixed(3)}`, x + 60, y + size + 16);
                }
                console.log(`${voice}: ${name} rendered`);
            }
            if (voice === "butler") {
                const targets = [0.15, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85];
                const clip = CLIPS.find((entry) => entry.name === "bug_shot");
                const sheet = document.createElement("canvas");
                sheet.width = margin + targets.length * size;
                sheet.height = header + size + label;
                const paint = sheet.getContext("2d");
                paint.fillStyle = "#15161a";
                paint.fillRect(0, 0, sheet.width, sheet.height);
                paint.fillStyle = "#e8e7ef";
                paint.font = "bold 17px sans-serif";
                paint.fillText("bug_shot · target crossing · u=0.36, y=0.275", 12, 24);
                for (const [column, x] of targets.entries()) {
                    const canvas = document.createElement("canvas");
                    canvas.width = canvas.height = size;
                    for (const material of figure.screens) {
                        delete material.userData.waiting;
                        delete material.userData.shownKey;
                        delete material.userData.frame;
                    }
                    stage.draw(figure, clip, clip.frames * 0.36, 0, canvas, {target: {x, y: 0.275}});
                    paint.drawImage(canvas, margin + column * size, header);
                    paint.fillStyle = "#aaadbf";
                    paint.font = "12px monospace";
                    paint.fillText(`x=${x.toFixed(2)}`, margin + column * size + 48, header + size + 16);
                }
                sheets.bug_shot_crossing = sheet;
            }
        }
        return Object.entries(sheets).map(([name, sheet]) => ({name, png: sheet.toDataURL("image/png")}));
    }, {voices: (process.env.FIGURE_VOICES ?? "").split(",").filter(Boolean), pixels: Number(process.env.FIGURE_SIZE ?? 176)});
    for (const strip of strips) {
        const path = `${out}/${strip.name}.png`;
        mkdirSync(dirname(path), {recursive: true});
        writeFileSync(path, Buffer.from(strip.png.split(",")[1], "base64"));
        console.log(path);
    }
} finally {
    await browser.close();
    await server.close();
}
