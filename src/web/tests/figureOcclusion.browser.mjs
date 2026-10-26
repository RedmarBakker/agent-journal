import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

// Real depth-buffer checks, followed by the actual five avatars with face-level props. The fixture creates the screen before the
// occluder as well as after it: visibility must depend on distance, never on material creation or draw order.
const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/occlusion");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
const failures = [];
try {
    const page = await browser.newPage();
    page.on("pageerror", (error) => failures.push(error.message));
    page.on("console", (message) => { if (message.type() === "log") console.log(message.text()); });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async ({size}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const THREE = await import("/node_modules/three/build/three.module.js");
        const stage = new Stage();
        const checks = [];
        for (const reverse of [false, true]) {
            const materials = [new THREE.MeshBasicMaterial({color: 0xffffff}), new THREE.MeshBasicMaterial({color: 0x333333})];
            const screen = new THREE.Mesh(new THREE.PlaneGeometry(2, 1.4), materials[Number(reverse)]);
            const box = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1, 0.2), materials[Number(!reverse)]);
            screen.position.set(0, 2.4, 0);
            box.position.set(0, 2.4, 0.3);
            const scene = new THREE.Scene();
            scene.add(screen, box);
            const figure = {scene, screens: [screen.material], visorHulls: []};
            const alpha = (x = 0) => {
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = 128;
                stage.drawScreen(figure, canvas);
                const at = new THREE.Vector3(x, 2.4, 0).project(stage.camera);
                return canvas.getContext("2d").getImageData(Math.round((at.x + 1) * 64), Math.round((1 - at.y) * 64), 1, 1).data[3];
            };
            const blocked = alpha();
            const exposed = alpha(0.8);
            box.visible = false;
            const removed = alpha();
            box.visible = true;
            box.position.z = -0.3;
            const behind = alpha();
            checks.push({reverse, blocked, exposed, removed, behind, restored: materials.every((material) => material.colorWrite) && stage.screenRenderer.autoClear});
            for (const mesh of [screen, box]) { mesh.geometry.dispose(); mesh.material.dispose(); }
        }
        const entries = Object.entries(await (await fetch("/voices/figures/figures.json")).json());
        const cases = [
            {name: "binoculars", u: 0.5, label: "Binoculars"},
            {name: "phone_call", u: 0.6, label: "Telephone"},
            {name: "read", u: 0.4, label: "Book"},
            {name: "yawn", u: 0.5, label: "Hand at face"},
            {name: "bug_shot", u: 0.36, label: "Shouldered rifle", target: {x: 2.2, y: 0.3, back: 0}},
            {name: "idle", u: 0, label: "Back of head", facing: 180},
        ];
        const left = 82, header = 36, rowHeight = size + 12;
        const sheet = document.createElement("canvas");
        sheet.width = left + size * cases.length;
        sheet.height = header + rowHeight * entries.length;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a";
        paint.fillRect(0, 0, sheet.width, sheet.height);
        paint.font = "12px sans-serif";
        paint.fillStyle = "#d2d4e2";
        for (const [column, each] of cases.entries()) paint.fillText(each.label, left + column * size + 8, 23);
        const rears = [];
        for (const [row, [voice, file]] of entries.entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            paint.fillStyle = "#aaadbf";
            paint.fillText(voice, 8, header + row * rowHeight + size / 2);
            for (const [column, each] of cases.entries()) {
                const canvas = document.createElement("canvas");
                canvas.width = canvas.height = size;
                const clip = CLIPS.find((entry) => entry.name === each.name);
                stage.draw(figure, clip, each.u * clip.frames, each.facing ?? 0, canvas, {target: each.target ?? null});
                paint.drawImage(canvas, left + column * size, header + row * rowHeight);
                if (each.facing === 180) {
                    const visor = document.createElement("canvas");
                    visor.width = visor.height = size;
                    stage.drawScreen(figure, visor);
                    const data = visor.getContext("2d").getImageData(0, 0, size, size).data;
                    rears.push({voice, opaquePixels: Array.from({length: size * size}, (_, index) => data[index * 4 + 3]).filter((alpha) => alpha > 16).length});
                }
            }
            console.log(`${voice}: face props and rear view checked`);
        }
        return {png: sheet.toDataURL("image/png"), checks, rears};
    }, {size: Number(process.env.FIGURE_SIZE ?? 144)});
    mkdirSync(out, {recursive: true});
    writeFileSync(`${out}/visor_occlusion.png`, Buffer.from(result.png.split(",")[1], "base64"));
    const {png, ...checks} = result;
    writeFileSync(`${out}/checks.json`, `${JSON.stringify(checks, null, 2)}\n`);
    for (const check of result.checks) {
        if (check.blocked > 0 || check.exposed < 240 || check.removed < 240 || check.behind < 240 || !check.restored) failures.push(`depth-order fixture failed: ${JSON.stringify(check)}`);
    }
    for (const rear of result.rears) if (rear.opaquePixels > 0) failures.push(`visor visible through ${rear.voice}'s back of head: ${rear.opaquePixels} pixels`);
    console.log(JSON.stringify(checks));
    console.log(`${out}/visor_occlusion.png`);
} finally {
    await browser.close();
    await server.close();
}
if (failures.length) {
    console.error(failures.join("\n"));
    if (process.env.FIGURE_EXPECT_OCCLUSION !== "0") process.exitCode = 1;
}
