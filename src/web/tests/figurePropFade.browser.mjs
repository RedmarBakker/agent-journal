import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

// Actual WebGL colour and depth checks: a translucent prop must blend over a visor in front and vanish behind it, for either material
// creation order. The fully opaque endpoint returns to the normal depth occlusion pass.
const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/prop-fade");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(server.resolvedUrls.local[0]);
    const checks = await page.evaluate(async () => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {Stage} = await import("/src/figure/figure.js");
        const {fadeProp, restorePropOpacity} = await import("/src/figure/propTransition.js");
        const stage = new Stage();
        const checks = [];
        for (const reverse of [false, true]) {
            const materials = [new THREE.MeshBasicMaterial(), new THREE.MeshBasicMaterial()];
            const screen = new THREE.Mesh(new THREE.PlaneGeometry(2, 1.4), materials[Number(reverse)]);
            const prop = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 1), materials[Number(!reverse)]);
            screen.material.color.setHex(0xffffff);
            prop.material.color.setHex(0xff0000);
            screen.position.set(0, 2.4, 0);
            const scene = new THREE.Scene();
            scene.add(screen, prop);
            const figure = {scene, screens: [screen.material], visorHulls: []};
            for (const depth of [0.3, -0.3]) {
                prop.position.set(0, 2.4, depth);
                for (const alpha of [1, 0.75, 0.5, 0.25, 0, 0.25, 0.5, 0.75, 1]) {
                    restorePropOpacity(prop);
                    fadeProp(prop, alpha);
                    const saved = materials.map((material) => [material.colorWrite, material.depthWrite, material.visible]);
                    const canvas = document.createElement("canvas");
                    canvas.width = canvas.height = 128;
                    stage.drawBody(figure, canvas);
                    stage.drawScreen(figure, canvas);
                    const pixel = [...canvas.getContext("2d").getImageData(64, 64, 1, 1).data];
                    const restored = materials.every((material, index) => saved[index].every((value, field) => value === [material.colorWrite, material.depthWrite, material.visible][field]));
                    checks.push({reverse, depth, alpha, pixel, restored});
                }
            }
            for (const mesh of [screen, prop]) { mesh.geometry.dispose(); mesh.material.dispose(); }
        }
        return checks;
    });
    mkdirSync(out, {recursive: true});
    for (const check of checks) {
        const [red, green, blue, alpha] = check.pixel;
        const expected = check.depth > 0 ? Math.round(255 * (1 - check.alpha)) : 255;
        if (red < 250 || alpha < 250 || Math.abs(green - expected) > 3 || Math.abs(blue - expected) > 3 || !check.restored) errors.push(`translucent prop compositing failed: ${JSON.stringify(check)}`);
    }
    const report = `${JSON.stringify({checks, errors}, null, 2)}\n`;
    writeFileSync(`${out}/checks.json`, report);
    writeFileSync(`${out}/compositing_checks.json`, report);
    console.log(JSON.stringify({checks: checks.length, failures: errors}));
    if (errors.length) process.exitCode = 1;
} finally {
    await browser.close();
    await server.close();
}
