// Render the call from its actual models, including the seat and either side of the handset.
import {createHash} from "node:crypto";
import {existsSync, mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.argv[3] ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/phone-call.png");
const paths = ["src/figure/figure.js", "src/figure/acts.js", "src/figure/perches.js", "src/figure/phonePlacement.js", "src/figure/ears.js"].filter((path) => existsSync(resolve(process.env.PHONE_SOURCE_ROOT ?? root, path)));
const snapshots = new Map(paths.map((path) => [resolve(root, path), readFileSync(resolve(process.env.PHONE_SOURCE_ROOT ?? root, path), "utf8")]));
const sourceHashes = Object.fromEntries([...snapshots].map(([path, source]) => [path.slice(root.length + 1), createHash("sha256").update(source).digest("hex")]));
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "phone-source-snapshot", enforce: "pre", load: (id) => snapshots.get(id) ?? null}], define: {__DEMO__: false}, server: {port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || undefined, args: ["--no-sandbox", "--enable-unsafe-swiftshader"]});

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => { if (message.type() === "log" && message.text().startsWith("Phone strip:")) console.log(message.text()); });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async ({requestedRows, requestedMoments, size}) => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {POSTURES} = await import("/src/figure/places.js");
        const {FRAMED} = await import("/src/figure/frame.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const clip = CLIPS.find((each) => each.name === "phone_call");
        const stage = new Stage();
        const rows = requestedRows ?? [
            ["butler", "stand", 0, 1], ["butler", "sit", 0, -1], ["butler", "sit", 70, -1],
            ["butler", "composed", 0, 1], ["homie", "stand", 25, 1], ["coach", "sit", 0, 1],
            ["colleague", "composed", 25, -1], ["squire", "stand", -25, 1],
        ];
        const heading = 30;
        const moments = requestedMoments ?? [0, 0.15, 0.2, 0.24, 0.3, 0.36, 0.42, 0.48, 0.6, 0.76, 0.8, 0.84, 0.9, 1];
        const sheet = document.createElement("canvas");
        sheet.width = size * moments.length;
        sheet.height = (size + heading) * rows.length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#1b1d21";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const figures = new Map();
        for (const [row, [voice, posture, facing, phoneWay, leanWay = 0]] of rows.entries()) {
            if (!figures.has(voice)) figures.set(voice, await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/"));
            paint.fillStyle = "#d8dde8";
            paint.font = "15px sans-serif";
            paint.fillText(`${voice} · ${posture} · ${facing}° · phone ${phoneWay < 0 ? "left" : "right"}${leanWay ? ` · lean ${leanWay}` : ""}`, 12, row * (size + heading) + 21);
            for (const [column, u] of moments.entries()) {
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = size;
                const figure = figures.get(voice);
                for (const material of figure.screens) {
                    delete material.userData.waiting;
                    delete material.userData.shownKey;
                    delete material.userData.frame;
                }
                stage.draw(figure, clip, u * (clip.frames - 1), facing, canvas, {posture, phoneWay, leanWay});
                // The page's supporting surface is a guide behind the transparent figure, at the same height as its seat or feet.
                const surface = posture === "stand" ? 0 : POSTURES[posture].drop * FRAMED.height;
                const floor = stage.pictured(new THREE.Vector3(0, 0, surface)).y * size;
                paint.fillStyle = "#3a414b";
                paint.fillRect(column * size + 8, row * (size + heading) + heading + floor, size - 16, 1);
                paint.drawImage(canvas, column * size, row * (size + heading) + heading);
                paint.fillStyle = "#8e98aa";
                paint.fillText(`${Math.round(u * 100)}%`, column * size + 8, (row + 1) * (size + heading) - 9);
            }
            console.log(`Phone strip: ${voice} ${posture} ${facing}° phone ${phoneWay}`);
        }
        return {png: sheet.toDataURL("image/png"), rows, moments};
    }, {requestedRows: process.env.PHONE_STRIP_ROWS ? JSON.parse(process.env.PHONE_STRIP_ROWS) : null, requestedMoments: process.env.PHONE_STRIP_MOMENTS ? JSON.parse(process.env.PHONE_STRIP_MOMENTS) : null, size: Number(process.env.PHONE_STRIP_SIZE ?? 256)});
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.png.split(",")[1], "base64"));
    writeFileSync(out.replace(/\.png$/, ".json"), JSON.stringify({rows: strip.rows, moments: strip.moments, sourceHashes, errors}, null, 2) + "\n");
    if (errors.length) throw new Error(errors.join("\n"));
    console.log(`Phone strip written to ${out}`);
} finally {
    await browser.close();
    await server.close();
}
