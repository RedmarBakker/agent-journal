import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

// One labeled sequence per voice. Separate sequences let an unchanged performance keep its exact rendered frames.
const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/tantrum");
const clipName = process.env.FIGURE_CLIP ?? process.env.TANTRUM_CLIP ?? "tantrum";
const voices = (process.env.FIGURE_VOICES ?? process.env.TANTRUM_VOICES ?? "butler,homie,coach,colleague,squire").split(",").map((voice) => voice.trim()).filter(Boolean);
const facings = (process.env.FIGURE_FACINGS ?? "0").split(",").map(Number);
const size = Number(process.env.FIGURE_SIZE ?? 192);
const fps = Number(process.env.FIGURE_FPS ?? process.env.TANTRUM_FPS ?? 18);
const labelHeight = 24;
const background = "#252832";
if (!Number.isInteger(size) || size < 32 || !Number.isFinite(fps) || fps <= 0) throw new Error("Preview size and frame rate must be positive");
if (!voices.length || !facings.length || facings.some((facing) => !Number.isFinite(facing))) throw new Error("Preview voices and facings must be valid");
const hash = (text) => createHash("sha256").update(text).digest("hex");
const snapshots = new Map(["src/figure/figure.js", "src/figure/acts.js", "src/figure/butler.js", "src/figure/homie.js", "src/figure/headphoneClearance.js"].map((path) => [resolve(root, path), readFileSync(resolve(root, path), "utf8")]));
const source = snapshots.get(resolve(root, "src/figure/figure.js"));
const sourceHashes = (voice) => {
    const relevant = ["src/figure/figure.js", "src/figure/acts.js"];
    if (voice === "butler") relevant.push("src/figure/butler.js");
    if (voice === "homie") relevant.push("src/figure/homie.js", "src/figure/headphoneClearance.js");
    return Object.fromEntries(relevant.map((path) => [path, hash(snapshots.get(resolve(root, path)))]));
};
const functionSource = (name) => {
    const start = source.indexOf(`function ${name}(`);
    const end = source.indexOf("\n}", start);
    if (start < 0 || end < 0) throw new Error(`Missing pose function ${name}`);
    return source.slice(start, end + 2);
};
const poseBlock = (voice) => {
    if (clipName === "groove") {
        const start = source.indexOf("export const ACTING =");
        const end = source.indexOf("\n};", start);
        if (start < 0 || end < 0) throw new Error("Missing groove gesture constants");
        return source.slice(start, end + 3) + "\n" + functionSource("groove");
    }
    if (clipName !== "tantrum") throw new Error(`Unsupported preview clip ${clipName}`);
    if (voice === "butler") {
        const start = source.indexOf("const BUTLER_TANTRUM =");
        const end = source.indexOf("function fume(", start);
        if (start < 0 || end < 0) throw new Error("Missing Butler tantrum helpers");
        return source.slice(start, end);
    }
    const start = source.indexOf("const tantrumBeat =");
    const end = source.indexOf("function homie_tantrum(", start);
    if (start < 0 || end < 0) throw new Error("Missing tantrum footwork helpers");
    return source.slice(start, end) + "\n" + functionSource(`${voice}_tantrum`);
};
const poseHashes = Object.fromEntries(voices.map((voice) => [voice, {poseBlockSha256: hash(poseBlock(voice)), poseFunctionSha256: hash(functionSource(clipName === "groove" ? "groove" : `${voice}_tantrum`))}]));
const server = await createServer({
    root,
    configFile: false,
    logLevel: "silent",
    plugins: [{name: "tantrum-preview-snapshot", enforce: "pre", load: (id) => snapshots.get(id) ?? null}],
    server: {host: "127.0.0.1", port: 0},
});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => {if (message.text().startsWith("[tantrum-preview]")) console.log(message.text());});
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    for (const voice of voices) {
        const result = await page.evaluate(async ({voice, clipName, facings, size, fps, labelHeight, background}) => {
            const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
            const index = await (await fetch("/voices/figures/figures.json")).json();
            if (!index[voice]) throw new Error(`Unknown voice ${voice}`);
            const figure = await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            const clip = CLIPS.find((each) => each.name === clipName);
            if (!clip) throw new Error(`The production ${clipName} clip is missing`);
            const seconds = clip.frames / clip.fps;
            const count = Math.max(Math.round(seconds * fps), 2);
            const stage = new Stage();
            const canvas = Object.assign(document.createElement("canvas"), {width: facings.length * size, height: size + labelHeight});
            const cell = Object.assign(document.createElement("canvas"), {width: size, height: size});
            const paint = canvas.getContext("2d"), pixels = cell.getContext("2d");
            const edgeFrames = [];
            const occupied = {left: size, top: size, right: -1, bottom: -1};
            const viewBounds = facings.map((facing) => ({facing, edgeFrames: [], occupied: {left: size, top: size, right: -1, bottom: -1}}));
            let firstPixels, endpointMaxChannelDifference = 0;
            // Compile the shaders before comparing the first and last samples of the same resting pose.
            for (const facing of facings) stage.draw(figure, clip, 0, facing, cell, {posture: "stand"});
            const frames = Array.from({length: count}, (_, frame) => {
                paint.fillStyle = background;
                paint.fillRect(0, 0, canvas.width, canvas.height);
                for (const [column, facing] of facings.entries()) {
                    for (const material of figure.screens) {
                        delete material.userData.waiting;
                        delete material.userData.shownKey;
                        delete material.userData.frame;
                    }
                    stage.draw(figure, clip, frame / (count - 1) * (clip.frames - 1), facing, cell, {posture: "stand"});
                    const data = pixels.getImageData(0, 0, size, size).data;
                    let touches = false;
                    for (let y = 0; y < size; y++) {
                        for (let x = 0; x < size; x++) {
                            if (data[(y * size + x) * 4 + 3] < 12) continue;
                            for (const bounds of [occupied, viewBounds[column].occupied]) {
                                bounds.left = Math.min(bounds.left, x);
                                bounds.top = Math.min(bounds.top, y);
                                bounds.right = Math.max(bounds.right, x);
                                bounds.bottom = Math.max(bounds.bottom, y);
                            }
                            if (!x || !y || x === size - 1 || y === size - 1) touches = true;
                        }
                    }
                    if (touches) {
                        if (edgeFrames.at(-1) !== frame) edgeFrames.push(frame);
                        viewBounds[column].edgeFrames.push(frame);
                    }
                    paint.drawImage(cell, column * size, 0);
                    paint.font = "13px sans-serif";
                    paint.fillStyle = "#e0e4ee";
                    paint.textAlign = "center";
                    const name = voice[0].toUpperCase() + voice.slice(1);
                    const view = facing === 0 ? "Front" : facing === 90 ? "Side" : `${facing}°`;
                    paint.fillText(facings.length === 1 ? name : `${name} · ${view}`, (column + 0.5) * size, size + 17);
                }
                if (!frame) firstPixels = paint.getImageData(0, 0, canvas.width, canvas.height).data;
                if (frame === count - 1) {
                    const lastPixels = paint.getImageData(0, 0, canvas.width, canvas.height).data;
                    for (let index = 0; index < firstPixels.length; index++) endpointMaxChannelDifference = Math.max(endpointMaxChannelDifference, Math.abs(firstPixels[index] - lastPixels[index]));
                }
                if (!(frame % Math.max(Math.round(fps), 1))) console.log(`[tantrum-preview] ${voice}/${clipName} ${frame + 1}/${count}`);
                return canvas.toDataURL("image/png");
            });
            stage.renderer.dispose();
            stage.screenRenderer.dispose();
            return {frames, seconds, sourceFrames: clip.frames, sourceFps: clip.fps, edgeFrames, occupied, viewBounds, endpointMaxChannelDifference};
        }, {voice, clipName, facings, size, fps, labelHeight, background});
        const folder = resolve(out, voice);
        mkdirSync(folder, {recursive: true});
        result.frames.forEach((png, frame) => writeFileSync(resolve(folder, `frame_${String(frame).padStart(3, "0")}.png`), Buffer.from(png.split(",")[1], "base64")));
        const metadata = {
            voice, clip: clipName, posture: "stand", ...(facings.length === 1 ? {facing: facings[0]} : {}), facings,
            width: facings.length * size, height: size + labelHeight, cellSize: size, labelHeight, background,
            frames: result.frames.length, fps, seconds: result.seconds, sourceFrames: result.sourceFrames, sourceFps: result.sourceFps,
            fixedCamera: true, exactEndpoints: true, endpointsIdentical: result.frames[0] === result.frames.at(-1),
            endpointMaxChannelDifference: result.endpointMaxChannelDifference,
            edgeFrames: result.edgeFrames, occupied: result.occupied, viewBounds: result.viewBounds, ...poseHashes[voice], sourceHashes: sourceHashes(voice), errors: [...errors],
        };
        writeFileSync(resolve(folder, "preview.json"), JSON.stringify(metadata, null, 2) + "\n");
        console.log(JSON.stringify({voice, folder, frames: result.frames.length, seconds: result.seconds, edgeFrames: result.edgeFrames, endpointsIdentical: metadata.endpointsIdentical}));
        if (result.edgeFrames.length || errors.length) process.exitCode = 1;
    }
} finally {
    await browser.close();
    await server.close();
}
