import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/prop-lifecycle");
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
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const load = async (voice) => figureOf(await (await fetch(`/voices/figures/${files[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
        const stage = new Stage();
        const figure = await load("butler");
        const named = (name) => CLIPS.find((clip) => clip.name === name);
        const cell = 160, left = 96, top = 30;
        const cases = [
            {name: "read", key: "book", posture: "stand", prop: figure.book},
            {name: "type", key: "laptop", posture: "sit", prop: figure.laptop},
            {name: "binoculars", key: "prop:binoculars", posture: "stand", prop: figure.propByName.get("binoculars")},
            {name: "bug_shot", key: "prop:rifle", posture: "stand", prop: figure.propByName.get("rifle"), u: 0.36, target: {x: 2.2, y: 0.3, back: 0}},
        ];
        const steps = [0, 0.04, 0.08, 0.12, 0.16, 0.25];
        const sheet = document.createElement("canvas");
        sheet.width = left + cell * steps.length;
        sheet.height = top + cell * cases.length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        paint.fillStyle = "#d2d4e2";
        paint.font = "12px sans-serif";
        steps.forEach((step, column) => paint.fillText(`${Math.round(step * 1000)} ms`, left + column * cell + 8, 20));
        const checks = [];
        for (const [row, each] of cases.entries()) {
            const canvas = document.createElement("canvas");
            canvas.width = canvas.height = cell;
            const clip = named(each.name);
            const before = stage.draw(figure, clip, (each.u ?? 0.4) * clip.frames, 0, canvas, {posture: each.posture, target: each.target ?? null});
            const scale = new THREE.Vector3().setFromMatrixScale(each.prop.matrix);
            paint.fillStyle = "#d2d4e2";
            paint.fillText(each.name, 8, top + row * cell + cell / 2);
            let previous = before;
            for (const [column, elapsed] of steps.entries()) {
                const k = Math.min(elapsed / 0.25, 1);
                previous = stage.draw(figure, named("idle"), 0, 0, canvas, {time: 1 + elapsed, blend: {from: before, previous, k: k * k * (3 - 2 * k), plant: each.posture === "sit"}});
                const entry = figure.propTransitions.props.entries.get(each.key);
                checks.push({name: each.name, elapsed, alpha: entry?.alpha ?? 0, visible: each.prop.visible, scaleError: new THREE.Vector3().setFromMatrixScale(each.prop.matrix).distanceTo(scale)});
                paint.drawImage(canvas, left + column * cell, top + row * cell);
            }
            stage.draw(figure, clip, (each.u ?? 0.4) * clip.frames, 0, canvas, {posture: each.posture, target: each.target ?? null});
            checks.push({name: each.name, static: true, alpha: figure.propTransitions.props.entries.get(each.key)?.alpha ?? 0, visible: each.prop.visible});
            console.log(`${each.name}: live retirement and static reset checked`);
        }
        const squire = await load("squire");
        const canvas = document.createElement("canvas");
        canvas.width = canvas.height = cell;
        stage.draw(squire, named("idle"), 0, 0, canvas);
        const carrying = [];
        for (const elapsed of [0, 0.08, 0.16, 0.24, 0.32]) {
            stage.draw(squire, named("read"), 0.4 * named("read").frames, 0, canvas, {time: 10 + elapsed});
            carrying.push({phase: "enter", elapsed, book: squire.propTransitions.props.entries.get("book")?.alpha ?? 0, carried: Math.max(0, ...[...squire.propTransitions.carrying.entries.values()].map((entry) => entry.alpha))});
        }
        for (const elapsed of [0, 0.08, 0.16, 0.24, 0.32]) {
            stage.draw(squire, named("idle"), 0, 0, canvas, {time: 11 + elapsed});
            carrying.push({phase: "leave", elapsed, book: squire.propTransitions.props.entries.get("book")?.alpha ?? 0, carried: Math.max(0, ...[...squire.propTransitions.carrying.entries.values()].map((entry) => entry.alpha))});
        }
        return {checks, carrying, png: sheet.toDataURL("image/png")};
    });
    mkdirSync(out, {recursive: true});
    writeFileSync(`${out}/prop_retirement.png`, Buffer.from(result.png.split(",")[1], "base64"));
    for (const check of result.checks) {
        const expected = check.static || check.elapsed === 0 ? 1 : check.elapsed >= 0.16 ? 0 : check.elapsed === 0.08 ? 0.5 : null;
        if (expected !== null && Math.abs(check.alpha - expected) > 1e-7) errors.push(`unexpected opacity: ${JSON.stringify(check)}`);
        if (check.elapsed >= 0.16 && check.visible) errors.push(`prop did not retire: ${JSON.stringify(check)}`);
        if (check.scaleError > 1e-7) errors.push(`retiring prop changed size: ${JSON.stringify(check)}`);
    }
    for (const check of result.carrying) if (check.book > 1e-7 && check.carried > 1e-7) errors.push(`two carried props overlap: ${JSON.stringify(check)}`);
    writeFileSync(`${out}/lifecycle_checks.json`, `${JSON.stringify({checks: result.checks, carrying: result.carrying, errors}, null, 2)}\n`);
    console.log(JSON.stringify({checks: result.checks.length + result.carrying.length, failures: errors}));
    if (errors.length) process.exitCode = 1;
} finally {
    await browser.close();
    await server.close();
}
