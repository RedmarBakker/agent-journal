// Needs a browser, so it is not in the default run: node src/web/tests/figureRepentStrip.browser.mjs [where the strip is written, default src/web/tests/strips/repent-strip.png]
// A strip of the confession act in a real browser: the figure standing, dropping onto both knees turned to the sin's mark on its left, the
// big cross coming up before it into both hands, held, lowered and the figure standing again; one cell for each moment, written as one PNG.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, join} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = fileURLToPath(new URL("..", import.meta.url));
const out = process.argv[2] ?? join(root, "tests", "strips", "repent-strip.png");
const server = await createServer({root, logLevel: "silent", server: {port: 0}});
await server.listen();
const browser = await chromium.launch();
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {ACTS} = await import("/src/figure/acts.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const voice = Object.keys(index)[0];
        const figure = await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "repent");
        const act = ACTS.repent;
        const SIZE = 224;
        const moments = [act.stand[0], act.stand[1], (act.kneel[0] + act.kneel[1]) / 2, act.kneel[1], act.out[1], (act.hold[0] + act.hold[1]) / 2, act.down[1], 0.99];
        const sheet = document.createElement("canvas");
        sheet.width = SIZE * moments.length;
        sheet.height = SIZE;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#1b1d21";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const drawn = [];
        for (const [index, u] of moments.entries()) {
            const canvas = document.createElement("canvas");
            canvas.width = canvas.height = SIZE;
            const frame = Math.min(Math.floor(u * clip.frames), clip.frames - 1);
            stage.draw(figure, clip, frame, 0, canvas, {at: {x: -0.6, y: 0.4, faces: true, behind: true, mood: "admiring", amount: 1}});
            paint.drawImage(canvas, index * SIZE, 0);
            drawn.push(frame);
        }
        return {png: sheet.toDataURL("image/png"), drawn, cells: moments.length};
    });
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
