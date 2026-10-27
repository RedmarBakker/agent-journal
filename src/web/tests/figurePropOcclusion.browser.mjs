// Real-model depth regression and a binoculars strip: node tests/figurePropOcclusion.browser.mjs out.png.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, join, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_PROJECT_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = process.argv[2] ?? join(root, "tests", "strips", "prop-occlusion.png");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE_PATH || process.env.CHROMIUM_PATH || undefined, args: ["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
const failures = [];

try {
    const page = await (await browser.newContext({deviceScaleFactor: 1})).newPage();
    page.on("pageerror", (error) => failures.push(error.message));
    page.on("console", (message) => {
        if (message.type() === "error" && /WebGL|shader|THREE/.test(message.text())) failures.push(message.text());
    });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const manifest = await (await fetch("/voices/figures/figures.json")).json();
        const stage = new Stage();
        const size = 224;
        const label = 28;
        const samples = [{frame: 0, facing: -35}, {frame: 25, facing: 0}, {frame: 50, facing: 35}, {frame: 75, facing: 0}];
        const sheet = document.createElement("canvas");
        sheet.width = size * samples.length;
        sheet.height = (size + label) * Object.keys(manifest).length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        const results = [];
        const checks = [];
        const makeCanvas = () => {
            const canvas = document.createElement("canvas");
            canvas.width = canvas.height = size;
            return canvas;
        };
        const dataOf = (canvas) => canvas.getContext("2d").getImageData(0, 0, size, size).data;
        const screenOnly = (figure) => {
            const canvas = makeCanvas();
            stage.drawScreen(figure, canvas);
            return dataOf(canvas);
        };
        const reference = (figure) => {
            const changed = new Map();
            const substitutes = new Map();
            const outlined = figure.visorHulls.map((hull) => hull.visible);
            const substitute = (material) => {
                if (substitutes.has(material)) return substitutes.get(material);
                const value = figure.screens.includes(material) ? 1 : 0;
                const next = material.clone();
                if (next.isShaderMaterial) next.fragmentShader = `void main() { gl_FragColor = vec4(vec3(${value}.0), 1.0); }`;
                else next.color.setRGB(value, value, value);
                Object.assign(next, {colorWrite: true, visible: material.visible, toneMapped: false, transparent: false, depthTest: true, depthWrite: true});
                substitutes.set(material, next);
                return next;
            };
            let data;
            try {
                for (const hull of figure.visorHulls) hull.visible = false;
                figure.scene.traverse((node) => {
                    if (!node.material) return;
                    changed.set(node, node.material);
                    node.material = Array.isArray(node.material) ? node.material.map(substitute) : substitute(node.material);
                });
                stage.screenRenderer.render(figure.scene, stage.camera);
                const canvas = makeCanvas();
                const source = stage.screenRenderer.domElement;
                stage.halvedOnto(source, 0, 0, source.width, source.height, canvas);
                data = dataOf(canvas);
            } finally {
                for (const [node, material] of changed) node.material = material;
                for (const material of substitutes.values()) material.dispose();
                figure.visorHulls.forEach((hull, index) => (hull.visible = outlined[index]));
            }
            return data;
        };
        const clip = CLIPS.find((each) => each.name === "binoculars");
        for (const [row, [voice, filename]] of Object.entries(manifest).entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${filename}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            for (const [column, {frame, facing}] of samples.entries()) {
                const canvas = makeCanvas();
                stage.draw(figure, clip, frame, facing, canvas);
                paint.drawImage(canvas, column * size, row * (size + label));
                paint.fillStyle = "#b8bac7";
                paint.font = "12px sans-serif";
                paint.fillText(`${voice} · ${frame}% · ${facing}°`, column * size + 10, row * (size + label) + size + 18);
                const prop = figure.propByName.get("binoculars");
                const baseline = screenOnly(figure);
                prop.visible = false;
                const uncovered = screenOnly(figure);
                prop.visible = true;
                const wanted = reference(figure);
                let covered = 0;
                let leaked = 0;
                let visible = 0;
                let missing = 0;
                for (let index = 0; index < baseline.length; index += 4) {
                    if (uncovered[index + 3] > 250 && wanted[index] < 5) {
                        covered++;
                        if (baseline[index + 3] > 20) leaked++;
                    }
                    if (wanted[index] > 250) {
                        visible++;
                        if (baseline[index + 3] < 235) missing++;
                    }
                }
                const key = `${voice} frame ${frame} facing ${facing}`;
                results.push({key, covered, leaked, visible, missing});
                const materials = new Map();
                const ordered = new Map();
                figure.scene.traverse((node) => {
                    if (!node.material) return;
                    ordered.set(node, node.renderOrder);
                    node.renderOrder = figure.screens.includes(node.material) ? -100 : 100;
                    for (const material of [node.material].flat()) materials.set(material, {colorWrite: material.colorWrite, visible: material.visible});
                });
                const before = figure.visorHulls.map((hull) => hull.visible);
                const shuffled = screenOnly(figure);
                checks.push({key, orderIndependent: baseline.every((value, index) => Math.abs(value - shuffled[index]) <= 1), statesRestored: [...materials].every(([material, state]) => material.colorWrite === state.colorWrite && material.visible === state.visible) && figure.visorHulls.every((hull, index) => hull.visible === before[index])});
                for (const [node, order] of ordered) node.renderOrder = order;
            }
        }
        stage.renderer.dispose();
        stage.screenRenderer.dispose();
        return {png: sheet.toDataURL("image/png"), results, checks};
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, Buffer.from(result.png.split(",")[1], "base64"));
    for (const row of result.results) {
        if (row.leaked > 1) failures.push(`${row.key}: ${row.leaked} visor pixels painted through the binoculars`);
        if (row.missing > 1) failures.push(`${row.key}: ${row.missing} unoccluded visor pixels missing`);
    }
    for (const voice of new Set(result.results.map((row) => row.key.split(" ")[0]))) {
        if (result.results.filter((row) => row.key.startsWith(`${voice} `)).every((row) => row.covered < 10)) failures.push(`${voice}: no meaningful screen/prop overlap tested`);
    }
    for (const row of result.checks) {
        if (!row.orderIndependent) failures.push(`${row.key}: visibility changes when props draw after the screen`);
        if (!row.statesRestored) failures.push(`${row.key}: drawScreen changed a material or outline's visibility`);
    }
    writeFileSync(out.replace(/\.png$/i, ".json"), JSON.stringify({results: result.results, checks: result.checks, failures}, null, 2) + "\n");
    console.log(`${result.results.length} real-model occlusion samples checked; strip written to ${out}`);
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
}
