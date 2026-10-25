// Needs a browser, so it is not in the default run: node src/web/tests/figureSeatStrip.browser.mjs [where the strip is written, default src/web/tests/strips/seat-strip.png]
// A strip of the figure seated on a chat bubble's edge in a real browser, beside it standing: seated facing the viewer, turned a little
// either way and on the ledge, its thighs forward over the edge and apart, its knees bent over it and its shins hanging, so it reads as
// sitting; one cell for each, written as one PNG.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, join} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = fileURLToPath(new URL("..", import.meta.url));
const out = process.argv[2] ?? join(root, "tests", "strips", "seat-strip.png");
const server = await createServer({root, logLevel: "silent", server: {port: 0}});
await server.listen();
const browser = await chromium.launch();
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {CLIPS, GROUND, Stage, figureOf} = await import("/src/figure/figure.js");
        const {POSTURES} = await import("/src/figure/places.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const voice = Object.keys(index)[0];
        const figure = await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
        const stage = new Stage();
        const SIZE = 256;
        const cells = [
            {clip: "idle", posture: "stand", facing: 0},
            {clip: "idle", posture: "sit", facing: 0},
            {clip: "idle", posture: "sit", facing: -20},
            {clip: "idle", posture: "sit", facing: 20},
            {clip: "ledge_sit", posture: "sit", facing: 0},
        ];
        const sheet = document.createElement("canvas");
        sheet.width = SIZE * cells.length;
        sheet.height = SIZE;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#1b1d21";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const drawn = [];
        for (const [place, cell] of cells.entries()) {
            // the bubble it rests on: its top edge the line the figure's picture puts its seat or its feet on
            const line = (1 - GROUND - POSTURES[cell.posture].drop) * SIZE;
            paint.fillStyle = "#3a3f4b";
            paint.beginPath();
            paint.roundRect(place * SIZE + SIZE * 0.08, line, SIZE * 0.84, SIZE - line + 12, 12);
            paint.fill();
            const clip = CLIPS.find((each) => each.name === cell.clip);
            const canvas = document.createElement("canvas");
            canvas.width = canvas.height = SIZE;
            stage.draw(figure, clip, 0, cell.facing, canvas, {posture: cell.posture});
            paint.drawImage(canvas, place * SIZE, 0);
            // how far down the cell the figure's pixels reach below the line, and how wide they spread there, seated
            const pixels = canvas.getContext("2d").getImageData(0, 0, SIZE, SIZE).data;
            let lowest = 0;
            let spread = 0;
            for (let y = Math.ceil(line); y < SIZE; y++) {
                const row = [];
                for (let x = 0; x < SIZE; x++) if (pixels[(y * SIZE + x) * 4 + 3] > 64) row.push(x);
                if (row.length) lowest = y;
                if (row.length && y < line + SIZE * 0.08) spread = Math.max(spread, row[row.length - 1] - row[0]);
            }
            drawn.push({...cell, below: (lowest - line) / SIZE, spread: spread / SIZE});
        }
        return {png: sheet.toDataURL("image/png"), drawn};
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(strip.png.split(",")[1], "base64"));
    for (const cell of strip.drawn.filter((each) => each.posture === "sit")) {
        // seated, the legs hang well below the edge, the knees apart just under it
        if (cell.below < 0.1) failures.push(`${cell.clip} turned ${cell.facing}: the legs reach only ${cell.below.toFixed(2)} of the picture below the edge`);
        if (cell.spread < 0.12) failures.push(`${cell.clip} turned ${cell.facing}: the knees span only ${cell.spread.toFixed(2)} of the picture just under the edge`);
    }
    console.log(`strip written to ${out}`, JSON.stringify(strip.drawn));
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
