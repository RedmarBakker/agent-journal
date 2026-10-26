// Render reproducible review strips and recover the test rig from the supplied models.
import {existsSync, mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve, join} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? join(root, "review", "strips"));
const wanted = process.env.FIGURE_CLIPS?.split(",");
const fixtureOnly = process.argv.includes("--fixture-only");
const server = await createServer({root, configFile: false, logLevel: "error", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH, args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
mkdirSync(out, {recursive: true});

try {
    const page = await browser.newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const fixture = await page.evaluate(async () => {
        const module = await import("/src/figure/figure.js");
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const figures = new Map();
        for (const [voice, file] of Object.entries(files)) {
            figures.set(voice, await module.figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/"));
        }
        window.review = {module, figures, stage: new module.Stage()};
        const rig = figures.values().next().value.rig;
        const vector = (at) => at.toArray().map((n) => Math.round(n * 1e6) / 1e6);
        return {
            rig: {order: rig.order, parents: Object.fromEntries(rig.parents), heads: Object.fromEntries([...rig.heads].map(([name, at]) => [name, vector(at)])), along: Object.fromEntries([...rig.along].map(([name, at]) => [name, vector(at)])), eyes: rig.eyes.map(vector)},
            stances: Object.fromEntries([...figures].map(([voice, figure]) => [voice, Object.fromEntries(Object.entries(figure.stance).map(([key, value]) => [key, value instanceof Set ? [...value] : value]))])),
        };
    });
    writeFileSync(join(out, "figureRig.json"), JSON.stringify(fixture, null, 4) + "\n");
    console.log(`Loaded ${Object.keys(fixture.stances).length} models; fixture written.`);
    if (!fixtureOnly) {
        const clips = await page.evaluate(() => window.review.module.CLIPS.map(({name}) => name));
        const manifest = [];
        for (const name of clips.filter((name) => !wanted || wanted.includes(name))) {
            const strip = await page.evaluate((name) => {
                const {module, figures, stage} = window.review;
                const clip = module.CLIPS.find((each) => each.name === name);
                const voice = clip.voices?.[0] ?? ({enter: "colleague", squire_chase: "squire"}[name] ?? "butler");
                const figure = figures.get(voice);
                const facing = ["bug_shot", "bug_smash", "work"].includes(name) ? 0 : 25;
                const postures = [clip.postures[0], ...(clip.postures.includes("sit") && clip.postures[0] !== "sit" ? ["sit"] : [])];
                const size = 224, columns = 8, label = 30;
                const sheet = document.createElement("canvas");
                sheet.width = columns * size;
                sheet.height = postures.length * (size + label);
                const paint = sheet.getContext("2d");
                paint.fillStyle = "#15161a";
                paint.fillRect(0, 0, sheet.width, sheet.height);
                const moments = [];
                for (const [row, posture] of postures.entries()) {
                    for (let column = 0; column < columns; column++) {
                        const frame = (clip.frames - 1) * column / (columns - 1);
                        const canvas = document.createElement("canvas");
                        canvas.width = canvas.height = size;
                        const options = {posture, stride: column / (columns - 1), sky: {shade: 0.5, back: 0.35}, target: name === "bug_shot" ? {x: 1.6, y: 0.4} : null};
                        for (const material of figure.screens) {
                            delete material.userData.waiting;
                            delete material.userData.shownKey;
                            delete material.userData.frame;
                        }
                        stage.draw(figure, clip, frame, facing, canvas, options);
                        paint.drawImage(canvas, column * size, row * (size + label) + label);
                        paint.fillStyle = "#d8d9e2";
                        paint.font = "12px sans-serif";
                        paint.fillText(`${name} / ${voice} / ${posture} / ${frame.toFixed(1)}`, column * size + 7, row * (size + label) + 20);
                        moments.push({frame, posture});
                    }
                }
                return {png: sheet.toDataURL("image/png"), name, voice, facing, pixels: size, moments};
            }, name);
            writeFileSync(join(out, `${name}.png`), Buffer.from(strip.png.split(",")[1], "base64"));
            const {png, ...record} = strip;
            manifest.push(record);
            console.log(`${manifest.length}: ${name}`);
        }
        const manifestPath = join(out, "manifest.json");
        const previous = wanted && existsSync(manifestPath) ? JSON.parse(readFileSync(manifestPath, "utf8")) : [];
        const records = new Map([...previous, ...manifest].map((record) => [record.name, {facing: 25, pixels: 224, ...record}]));
        writeFileSync(manifestPath, JSON.stringify(clips.filter((name) => records.has(name)).map((name) => records.get(name)), null, 4) + "\n");
    }
} finally {
    await browser.close();
    await server.close();
}
