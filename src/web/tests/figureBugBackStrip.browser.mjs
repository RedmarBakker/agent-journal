// Needs a browser, so it is not in the default run: node src/web/tests/figureBugBackStrip.browser.mjs [where the strip is written]
// A strip of the bug shot's figure in a real browser: facing a bug nearly straight above, backing away from it with its legs stepping
// backward, then shooting from where it stands, and facing a bug at an easy angle, shooting without a step. Written as one PNG, a frame
// to a cell; the angle of each shot is read back and must be within the limit.
import {writeFileSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = fileURLToPath(new URL("..", import.meta.url));
const out = process.argv[2] ?? join(tmpdir(), "bug-back-strip.png");
const server = await createServer({root, logLevel: "silent", server: {port: 0}});
await server.listen();
const browser = await chromium.launch();
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const strip = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {ACTS, backAt, backPlan, bugShotTimes, wallBugAt} = await import("/src/figure/acts.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const voice = Object.keys(index)[0];
        const figure = await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "bug_shot");
        const act = ACTS.bug_shot;
        const SIZE = 160;
        const WORLD = {left: 0, top: 0, right: 900, bottom: 700};
        const at = {x: 450, y: 350, left: 0, right: 900};
        const cases = [{name: "above", bug: {wall: "top", along: 0.5, way: 0}}, {name: "easy", bug: {wall: "left", along: 0.5, way: 0}}];
        const cells = [];
        const results = [];
        for (const {name, bug} of cases) {
            const plan = backPlan([bug], WORLD, at, SIZE);
            const spot = wallBugAt(bug, WORLD, bugShotTimes(0).shot);
            const times = bugShotTimes(0);
            for (const raw of [times.walk, (times.walk + times.aim) / 2, times.aim, times.shot * act.fps + 2]) {
                const placed = backAt(plan, raw, SIZE);
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = SIZE;
                const frame = Math.min(Math.round(act.turn[0] * act.frames + (raw - times.walk) * 0), act.frames - 1);
                stage.draw(figure, clip, Math.round(act.splat * act.frames), 0, canvas, {stride: placed.way ? -placed.steps : 0, walkWay: placed.way, target: {x: (spot.x - (placed.x - SIZE / 2)) / SIZE, y: (spot.y - (at.y - SIZE * 0.4)) / SIZE}});
                cells.push(canvas);
                results.push({name, x: placed.x, angle: (Math.atan2(Math.abs(spot.y - at.y), Math.abs(spot.x - placed.x)) * 180) / Math.PI, way: placed.way, frame});
            }
        }
        const sheet = document.createElement("canvas");
        sheet.width = SIZE * cells.length;
        sheet.height = SIZE;
        cells.forEach((cell, at) => sheet.getContext("2d").drawImage(cell, at * SIZE, 0));
        return {png: sheet.toDataURL("image/png"), results, limit: act.back.limit};
    });
    writeFileSync(out, Buffer.from(strip.png.split(",")[1], "base64"));
    for (const [at, result] of strip.results.entries()) {
        const shooting = at % 4 === 3;
        if (shooting && result.angle > strip.limit + 0.01) failures.push(`${result.name}: shot at ${result.angle.toFixed(1)} degrees, over the limit ${strip.limit}`);
        if (result.name === "easy" && result.way !== 0) failures.push("a bug at an easy angle was stepped back from");
        if (result.name === "above" && !strip.results.some((each) => each.name === "above" && each.way !== 0)) failures.push("a bug straight above was not stepped back from");
    }
    console.log(`strip written to ${out}`);
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
