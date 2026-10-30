// The production loader removes the model ears, while Homie's only cups follow its complete removable headset.
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/ears");
const references = new Map([["figure.js", process.env.EAR_FIGURE_SOURCE], ["headphoneClearance.js", process.env.EAR_CLEARANCE_SOURCE]].filter(([, path]) => path).map(([name, path]) => [resolve(root, "src/figure", name), readFileSync(path, "utf8")]));
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "ear-reference", enforce: "pre", load: (id) => references.get(id) ?? null}], server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage(), browserErrors = [];
    page.on("pageerror", (error) => browserErrors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async () => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const stage = new Stage(), figures = new Map();
        const idle = CLIPS.find(({name}) => name === "idle"), groove = CLIPS.find(({name}) => name === "groove");
        const size = 224, label = 24;
        const canvas = Object.assign(document.createElement("canvas"), {width: size, height: size});
        const sheet = Object.assign(document.createElement("canvas"), {width: size * 5, height: (size + label) * 3});
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a"; paint.fillRect(0, 0, sheet.width, sheet.height);
        const report = {voices: [], headphoneSamples: 0, errors: []};
        const picture = (figure, clip, u, facing, column, row, text) => {
            stage.draw(figure, clip, u * (clip.frames - 1), facing, canvas, {posture: "stand"});
            paint.drawImage(canvas, column * size, row * (size + label));
            paint.fillStyle = "#d8dbe6"; paint.font = "12px sans-serif";
            paint.fillText(text, column * size + 8, row * (size + label) + size + 17);
        };
        for (const [column, [voice, file]] of Object.entries(files).entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${file}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            figures.set(voice, figure);
            const ears = [], headphones = [];
            figure.scene.traverse((node) => {
                if (node.name.startsWith("ear_")) ears.push(node.name);
                if (node.name.startsWith("homie_headphones")) headphones.push(node.name);
            });
            const entry = {voice, ears, headphoneParts: headphones.length, cups: figure.headphones?.cups.length ?? 0};
            report.voices.push(entry);
            if (ears.length || (voice === "homie" ? entry.cups !== 2 : headphones.length)) report.errors.push(entry);
            picture(figure, idle, 0, 0, column, 0, `${voice} · front`);
            picture(figure, idle, 0, 90, column, 1, `${voice} · side`);
        }
        const figure = figures.get("homie"), headset = figure.headphones;
        const nearHead = [], loose = [];
        const body = stage.drawBody, screen = stage.drawScreen;
        stage.drawBody = stage.drawScreen = () => {};
        for (let frame = 0; frame < groove.frames; frame++) {
            const u = frame / (groove.frames - 1);
            stage.draw(figure, groove, frame, 0, null, {posture: "stand"});
            for (const cup of headset.cups) {
                if (cup.parent !== headset.root || cup.scale.distanceTo(new THREE.Vector3(1, 1, 1)) > 1e-9) report.errors.push({frame, part: cup.name, reason: "cup detached or scaled"});
            }
            if (u >= 0.4 && u <= 0.6) nearHead.push(headset.cups[0].position.y);
            if (!frame || frame === groove.frames - 1) loose.push(headset.cups[0].position.y);
            report.headphoneSamples++;
        }
        if (Math.min(...nearHead) - Math.max(...loose) < 0.7) report.errors.push({reason: "cups stay at head after lowering", nearHead, loose});
        stage.drawBody = body; stage.drawScreen = screen;
        for (const [column, u] of [0, 0.2, 0.5, 0.8, 1].entries()) picture(figure, groove, u, 20, column, 2, `Homie · headset ${u.toFixed(1)}`);
        return {report, png: sheet.toDataURL("image/png")};
    });
    mkdirSync(out, {recursive: true});
    writeFileSync(resolve(out, "checks.json"), JSON.stringify({...result.report, browserErrors}, null, 2) + "\n");
    writeFileSync(resolve(out, "ears.png"), Buffer.from(result.png.split(",")[1], "base64"));
    console.log(JSON.stringify({...result.report, browserErrors}));
    if ((result.report.errors.length || browserErrors.length) && !process.env.EAR_REPORT_ONLY) throw new Error("Ear removal or headphone lifecycle check failed");
} finally {
    await browser.close();
    await server.close();
}
