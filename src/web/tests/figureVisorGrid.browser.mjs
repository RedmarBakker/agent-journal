// Needs a browser, so it is not in the default run: node src/web/tests/figureVisorGrid.browser.mjs
// The visor's pixels drawn as a small screen's: every voice's figure drawn idle in a real browser at the chat's size and twice it, on a
// screen of two device pixels to a page pixel, and along the brightest row and column of each lit eye a dark gap of at least one device
// pixel lies between every two neighbouring lit visor pixels, while the eyes are still drawn lit.
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = fileURLToPath(new URL("..", import.meta.url));
const server = await createServer({root, logLevel: "silent", server: {port: 0}});
await server.listen();
const browser = await chromium.launch();
const failures = [];
const expect = (holds, what) => holds || failures.push(what);

try {
    const page = await (await browser.newContext({deviceScaleFactor: 2})).newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const drawn = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const stage = new Stage();
        const results = [];
        for (const voice of Object.keys(index)) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            for (const size of [112, 224]) {
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = size * devicePixelRatio;
                stage.draw(figure, CLIPS.find((clip) => clip.name === "idle"), 0, 0, canvas, {});
                const {data, width} = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height);
                // how bright each device pixel is, its channels' mean, 0 where nothing is drawn
                const light = (x, y) => (data[(y * width + x) * 4 + 3] > 200 ? (data[(y * width + x) * 4] + data[(y * width + x) * 4 + 1] + data[(y * width + x) * 4 + 2]) / 3 : 0);
                // the band of the picture the visor lies in
                const band = {top: Math.round(width * 0.22), bottom: Math.round(width * 0.46), left: Math.round(width * 0.28), right: Math.round(width * 0.72)};
                const rows = Array.from({length: band.bottom - band.top}, (_, y) => Array.from({length: band.right - band.left}, (_, x) => light(band.left + x, band.top + y)));
                results.push({voice, size, rows});
            }
        }
        return results;
    });
    for (const {voice, size, rows: band} of drawn) {
        // the visor's glass, near black: its box in the band, and the lines of device pixels across it, inside its rim
        const glass = band.flatMap((line, y) => line.flatMap((value, x) => (value > 0 && value < 30 ? [{x, y}] : [])));
        const box = {left: Math.min(...glass.map((at) => at.x)) + 3, right: Math.max(...glass.map((at) => at.x)) - 3, top: Math.min(...glass.map((at) => at.y)) + 3, bottom: Math.max(...glass.map((at) => at.y)) - 3};
        const rows = band.slice(box.top, box.bottom + 1).map((line) => line.slice(box.left, box.right + 1));
        const columns = rows[0].map((_, x) => rows.map((line) => line[x]));
        for (const [way, lines] of [["row", rows], ["column", columns]]) {
            // the line through the middle of the eyes, as bright as the brightest and the most lit of those: the runs of lit device pixels along it, each a visor pixel
            const runsOf = (line) => {
                const peak = Math.max(...line);
                const lit = line.map((value) => value >= peak * 0.6);
                const runs = [];
                lit.forEach((on, index) => (on && !lit[index - 1] ? runs.push({from: index, to: index}) : on && (runs.at(-1).to = index)));
                return {peak, runs};
            };
            const total = (line) => line.reduce((sum, value) => sum + value, 0);
            const best = lines.map((line) => ({line, ...runsOf(line)})).filter((each, _, all) => each.peak >= 0.95 * Math.max(...all.map((other) => other.peak))).sort((a, b) => total(b.line) - total(a.line))[0];
            const label = `${voice} at ${size} along a ${way}`;
            expect(best, `${label}: the eyes drawn lit`);
            if (!best) continue;
            expect(best.peak > 150, `${label}: the eyes lit, at ${Math.round(best.peak)}`);
            // neighbouring lit pixels, as close as one visor pixel apart, each with a dark device pixel between them
            const pitch = Math.min(...best.runs.slice(1).map((run, index) => run.from - best.runs[index].from));
            expect(best.runs.length >= 3, `${label}: lit pixels to tell apart, ${best.runs.length}`);
            for (const [index, run] of best.runs.slice(1).entries()) {
                const before = best.runs[index];
                if (run.from - before.from > pitch * 1.5) continue;
                const between = best.line.slice(before.to + 1, run.from);
                const dimmer = Math.min(Math.max(...best.line.slice(before.from, before.to + 1)), Math.max(...best.line.slice(run.from, run.to + 1)));
                expect(between.length >= 1 && Math.min(...between) <= dimmer * 0.6, `${label}: a dark gap between the pixels at ${before.to} and ${run.from} (${between.map(Math.round)} against ${Math.round(dimmer)})`);
            }
        }
    }
} finally {
    await browser.close();
    await server.close();
}

if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
console.log("the visor's pixels each read on their own at both sizes");
