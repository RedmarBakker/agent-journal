import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {createHash} from "node:crypto";
import {chromium} from "playwright-core";
import {createServer} from "vite";

// Compare the old unconstrained recovery with the grounded locomotion floor guard, preserving 60Hz pose history between captures.
const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/run-transitions");
const source = createHash("sha256").update(readFileSync(resolve(root, "src/figure/figure.js"))).digest("hex");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {strideAtDistance} = await import("/src/figure/gait.js");
        const {tripBetween} = await import("/src/figure/places.js");
        const {legAt} = await import("/src/domain/figureMotion.js");
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch(`/voices/figures/${files.butler}`)).arrayBuffer(), "butler", "/voices/figures/draco/");
        const stage = new Stage(), poseOnly = {drawBody() {}, drawScreen() {}};
        const named = (name) => CLIPS.find((clip) => clip.name === name);
        const canvasOf = (width, height = width) => Object.assign(document.createElement("canvas"), {width, height});
        const cell = canvasOf(192), sheet = canvasOf(144 + 8 * 192, 40 + 4 * 216);
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        paint.fillStyle = "#d2d4e2";
        paint.font = "13px sans-serif";
        paint.fillText("Grounded start and stop · before / after floor correction", 10, 24);
        const ground = Math.min(...["l", "r"].map((side) => figure.rig.heads.get(`foot_${side}`).z));
        const sole = (moves) => Math.min(...["l", "r"].map((side) => figure.rig.heads.get(`foot_${side}`).clone().applyMatrix4(moves.get(`foot_${side}`)).z));
        const frames = [0, 2, 4, 6, 8, 10, 15, 21];
        const leg = tripBetween({x: 0, y: 0}, {x: 300, y: 0}, 112, {pressing: true}).legs.find((each) => !each.hopping);
        const checks = [];
        for (const [row, {from, to, floor}] of [
            {from: "idle", to: "run", floor: false}, {from: "idle", to: "run", floor: true},
            {from: "run", to: "idle", floor: false}, {from: "run", to: "idle", floor: true},
        ].entries()) {
            for (const material of figure.screens) { delete material.userData.waiting; delete material.userData.shownKey; delete material.userData.frame; }
            const source = Stage.prototype.draw.call(poseOnly, figure, named(from), from === "run" ? 0.175 * named(from).frames : 0, 90, cell);
            let previous = source;
            paint.fillStyle = "#d2d4e2";
            paint.fillText(`${from} → ${to}`, 10, 40 + row * 216 + 85);
            paint.fillText(floor ? "After" : "Before", 10, 40 + row * 216 + 108);
            for (let tick = 0; tick <= frames.at(-1); tick++) {
                const elapsed = tick / 60, k = Math.min(elapsed / 0.25, 1);
                const phase = to === "run" ? strideAtDistance(legAt(leg, {x: 0, y: 0}, elapsed * 1000).x, 112, true) : 0;
                const options = {time: 10 + row + elapsed, blend: {from: source, previous, k: k * k * (3 - 2 * k), floor}};
                const column = frames.indexOf(tick);
                previous = column >= 0 ? stage.draw(figure, named(to), phase * named(to).frames, 90, cell, options) : Stage.prototype.draw.call(poseOnly, figure, named(to), phase * named(to).frames, 90, cell, options);
                const offset = sole(previous) - ground;
                checks.push({from, to, floor, elapsed, offset, pixels112: offset * 112 / 5.4});
                if (column < 0) continue;
                const x = 144 + column * 192, y = 40 + row * 216;
                paint.strokeStyle = "#727b8f";
                paint.beginPath();
                paint.moveTo(x, y + (0.5 + 2.4 / 5.4) * 192);
                paint.lineTo(x + 192, y + (0.5 + 2.4 / 5.4) * 192);
                paint.stroke();
                paint.drawImage(cell, x, y);
                paint.fillStyle = "#d2d4e2";
                paint.fillText(`${Math.round(elapsed * 1000)}ms`, x + 70, y + 210);
            }
        }
        return {checks, png: sheet.toDataURL("image/png")};
    });
    mkdirSync(out, {recursive: true});
    writeFileSync(resolve(out, "run_transitions_before_after.png"), Buffer.from(result.png.split(",")[1], "base64"));
    const before = Math.min(...result.checks.filter((check) => !check.floor).map((check) => check.offset));
    const after = Math.min(...result.checks.filter((check) => check.floor).map((check) => check.offset));
    if (after < -1e-8) errors.push(`floor correction left a sole below the floor: ${after}`);
    writeFileSync(resolve(out, "transition_checks.json"), `${JSON.stringify({source, before, after, checks: result.checks, errors}, null, 2)}\n`);
    console.log(JSON.stringify({samples: result.checks.length, before, after, errors}));
    if (errors.length) process.exitCode = 1;
} finally {
    await browser.close();
    await server.close();
}
