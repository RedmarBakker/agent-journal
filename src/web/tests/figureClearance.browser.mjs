// Exact posed-mesh bounds, including held items and the generated hat/halo. Uses Stage's production posing and visibility path with
// raster passes disabled, so dense sampling stays fast. FIGURE_ROOT can point at a baseline checkout.
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/clearance.json");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    page.on("console", (message) => {if (message.type() === "log") console.log(message.text());});
    page.on("pageerror", (error) => console.error(error));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async () => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const stage = new Stage();
        stage.drawBody = () => {};
        stage.drawScreen = () => {};
        const point = new THREE.Vector3();
        const results = [];
        for (const [voice, file] of Object.entries(index)) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            const skeletons = new Set();
            figure.scene.traverse((node) => {if (node.isSkinnedMesh) skeletons.add(node.skeleton);});
            for (const name of ["halo", "squire_chase", "hat_tip"]) {
                const clip = CLIPS.find((each) => each.name === name);
                if (clip.voices && !clip.voices.includes(voice)) continue;
                const bounds = {left: {value: Infinity}, right: {value: -Infinity}, bottom: {value: Infinity}, top: {value: -Infinity}};
                for (let sample = 0; sample <= 120; sample++) {
                    const frame = (clip.frames - 1) * sample / 120;
                    stage.draw(figure, clip, frame, 0, null, {posture: "stand"});
                    figure.scene.updateMatrixWorld(true);
                    for (const skeleton of skeletons) skeleton.update();
                    figure.scene.traverseVisible((node) => {
                        if (!node.isMesh || !node.geometry?.attributes.position) return;
                        for (let vertex = 0; vertex < node.geometry.attributes.position.count; vertex++) {
                            node.getVertexPosition(vertex, point).applyMatrix4(node.matrixWorld);
                            const mesh = node.name || node.userData.item;
                            if (point.x < bounds.left.value) bounds.left = {value: point.x, frame, mesh};
                            if (point.x > bounds.right.value) bounds.right = {value: point.x, frame, mesh};
                            if (point.y < bounds.bottom.value) bounds.bottom = {value: point.y, frame, mesh};
                            if (point.y > bounds.top.value) bounds.top = {value: point.y, frame, mesh};
                        }
                    });
                }
                results.push({voice, name, bounds});
                console.log(`${voice}: ${name} mesh bounds sampled`);
            }
        }
        return results;
    });
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, JSON.stringify(result, null, 4));
    console.log(JSON.stringify(result, null, 2));
    if (!process.env.CLEARANCE_REPORT_ONLY) {
        const {FRAMED} = await import(new URL("src/figure/frame.js", `file://${root}/`).href);
        const half = FRAMED.height / 2, margin = 0.07;
        for (const {voice, name, bounds} of result) {
            if (bounds.left.value < -half + margin || bounds.right.value > half - margin || bounds.bottom.value < FRAMED.middle - half + margin || bounds.top.value > FRAMED.middle + half - margin) {
                throw new Error(`${voice} ${name} crosses the production camera's outline reserve: ${JSON.stringify(bounds)}`);
            }
        }
    }
} finally {
    await browser.close();
    await server.close();
}
