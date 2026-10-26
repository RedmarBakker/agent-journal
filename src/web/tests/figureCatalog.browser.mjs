// Review every authored clip at representative moments, using the production Stage and one supported voice per clip.
// Vue/page effects are reviewed by their own component tests and targeted browser strips; these sheets cover bodies and 3D props.
import {existsSync, mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {dirname, join, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {createHash} from "node:crypto";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/catalog");
const size = Number(process.env.FIGURE_SIZE ?? 112);
const rows = Number(process.env.FIGURE_ROWS ?? 10);
const samples = process.env.FIGURE_SAMPLES === "4" ? 4 : 2;
const previous = existsSync(join(out, "catalog.json")) ? JSON.parse(readFileSync(join(out, "catalog.json"), "utf8")) : null;
const first = Number(process.env.FIGURE_START ?? previous?.pages.reduce((sum, page) => sum + page.clips.length, 0) ?? 0);
const until = Number(process.env.FIGURE_END ?? Infinity);
const selectedPages = process.env.FIGURE_PAGES?.split(",").map(Number);
const selectedClips = process.env.FIGURE_CLIPS?.split(",").filter(Boolean);
const sourceFiles = ["src/figure/figure.js", "src/figure/acts.js", "src/figure/looks.js", "src/figure/frame.js", "src/figure/blend.js"];
const sourceContents = sourceFiles.map((name) => ({name, bytes: readFileSync(join(root, name))}));
const sourceHash = createHash("sha256");
for (const {name, bytes} of sourceContents) sourceHash.update(name).update(bytes);
const sourceSnapshot = sourceHash.digest("hex");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
const manifest = previous ?? {size, rowsPerPage: rows, omitted: ["press (disabled compaction option)"], scope: "Production bodies and 3D props; separate Vue/page effects have their own targeted checks.", pages: [], errors: []};
try {
    const page = await browser.newPage({deviceScaleFactor: 1});
    page.on("console", (message) => {if (message.type() === "log") console.log(message.text());});
    page.on("pageerror", (error) => manifest.errors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const count = await page.evaluate(async () => {
        const {CLIPS, Stage, figureOf, supportsClip} = await import("/src/figure/figure.js");
        const {throwsFor} = await import("/src/figure/acts.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const voices = Object.keys(index);
        const models = {};
        for (const voice of voices) models[voice] = await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
        const clips = CLIPS.filter((clip) => clip.name !== "press").map((clip, i) => {
            const eligible = (clip.voices ?? voices).filter((voice) => supportsClip(clip.name, models[voice].stance));
            if (!eligible.length) throw new Error(`No supported voice for ${clip.name}`);
            return {clip, voice: eligible[i % eligible.length]};
        });
        window.catalog = {clips, models, stage: new Stage(), throws: throwsFor(() => 0.42)};
        return clips.length;
    });
    manifest.totalClips = count;
    delete manifest.samplesPerClip;
    manifest.defaultSamples = samples;
    manifest.voiceSelection = "clip.voices and supportsClip stance eligibility; shared clips rotate eligible voices";
    manifest.sourceSnapshots ??= {};
    manifest.sourceSnapshots[sourceSnapshot] = {files: sourceFiles, directory: `source-snapshots/${sourceSnapshot}`, capturedAt: new Date().toISOString()};
    mkdirSync(out, {recursive: true});
    for (const {name, bytes} of sourceContents) {
        const path = join(out, "source-snapshots", sourceSnapshot, name);
        mkdirSync(dirname(path), {recursive: true});
        writeFileSync(path, bytes);
    }
    const starts = selectedPages?.map((number) => (number - 1) * rows) ?? Array.from({length: Math.max(0, Math.ceil((Math.min(count, until) - first) / rows))}, (_, index) => first + index * rows);
    for (const start of starts) {
        const filename = `catalog-${String(Math.floor(start / rows) + 1).padStart(2, "0")}.png`;
        const saved = manifest.pages.find((page) => page.filename === filename);
        const reuse = selectedClips && saved && existsSync(join(out, filename)) ? {png: `data:image/png;base64,${readFileSync(join(out, filename)).toString("base64")}`, clips: saved.clips} : null;
        const capturedAt = new Date().toISOString();
        const result = await page.evaluate(async ({start, rows, size, samples, selectedClips, reuse, capturedAt, sourceSnapshot}) => {
            const {clips, models, stage, throws: thrown} = window.catalog;
            const selected = clips.slice(start, start + rows);
            const label = 166;
            const rowHeight = size + 24;
            const header = 36;
            const sheet = document.createElement("canvas");
            sheet.width = label + samples * size;
            sheet.height = header + selected.length * rowHeight;
            const paint = sheet.getContext("2d");
            paint.fillStyle = "#15161a";
            paint.fillRect(0, 0, sheet.width, sheet.height);
            if (reuse) {
                const previous = new Image();
                previous.src = reuse.png;
                await previous.decode();
                if (previous.width !== sheet.width || previous.height !== sheet.height) throw new Error("Clip refresh requires the original page size and sample count");
                paint.drawImage(previous, 0, 0);
            }
            paint.fillStyle = "#e8e7ef";
            paint.font = "bold 15px sans-serif";
            paint.fillText(`Animation catalog · ${start + 1}–${start + selected.length} of ${clips.length}`, 10, 23);
            const metadata = [];
            for (const [row, {clip, voice}] of selected.entries()) {
                const previous = reuse?.clips.find((entry) => entry.name === clip.name);
                if (previous && !selectedClips.includes(clip.name)) {
                    metadata.push(previous);
                    continue;
                }
                const figure = models[voice];
                const posture = clip.postures[0];
                const facing = ["walk", "push", "ladder_climb", "stumble"].includes(clip.name) ? 90 : 0;
                const moments = clip.intro && clip.outro ? [
                    clip.intro * 0.8 / clip.frames,
                    (clip.intro + (clip.frames - clip.intro - clip.outro) * 0.25) / clip.frames,
                    (clip.intro + (clip.frames - clip.intro - clip.outro) * 0.75) / clip.frames,
                    (clip.frames - clip.outro * 0.4) / clip.frames,
                ] : [0.15, 0.4, 0.65, 0.9];
                const times = samples === 4 ? moments : [moments[1], moments[2]];
                const y = header + row * rowHeight;
                paint.fillStyle = "#15161a";
                paint.fillRect(0, y, sheet.width, rowHeight);
                paint.fillStyle = "#e8e7ef";
                paint.font = "bold 12px monospace";
                paint.fillText(clip.name, 9, y + size * 0.4);
                paint.fillStyle = "#a7a9bb";
                paint.font = "11px sans-serif";
                paint.fillText(`${voice} · ${posture}`, 9, y + size * 0.4 + 18);
                const edges = [];
                for (const [column, u] of times.entries()) {
                    const cell = document.createElement("canvas");
                    cell.width = cell.height = size;
                    const options = {posture, stride: u, phoneWay: 1};
                    if (clip.name === "bug_shot") options.target = {x: 2.2, y: 0.35, back: 0};
                    if (clip.name === "rummage") Object.assign(options, {throws: thrown, leanWay: 1});
                    if (clip.name === "lean") options.leanWay = 1;
                    if (clip.name === "watch") options.sky = {shade: 0.8, back: 0.5};
                    if (clip.name === "glass_bubble") options.at = {x: 0.85, y: 0.15, behind: true};
                    for (const material of figure.screens) {
                        delete material.userData.waiting;
                        delete material.userData.shownKey;
                        delete material.userData.frame;
                    }
                    stage.draw(figure, clip, u * clip.frames, facing, cell, options);
                    const pixels = cell.getContext("2d").getImageData(0, 0, size, size).data;
                    let touched = 0;
                    for (let at = 0; at < size; at++) {
                        for (const point of [at, (size - 1) * size + at, at * size, at * size + size - 1]) if (pixels[point * 4 + 3] > 32) touched++;
                    }
                    edges.push(touched);
                    paint.drawImage(cell, label + column * size, y);
                    paint.fillStyle = "#a7a9bb";
                    paint.font = "11px monospace";
                    paint.fillText(`u=${u.toFixed(3)}`, label + column * size + 24, y + size + 14);
                }
                paint.strokeStyle = "#30333f";
                paint.beginPath();
                paint.moveTo(8, y + rowHeight - 1);
                paint.lineTo(sheet.width - 8, y + rowHeight - 1);
                paint.stroke();
                metadata.push({name: clip.name, voice, posture, facing, times, edgePixels: edges, capturedAt, sourceSnapshot});
                console.log(`catalog: ${start + row + 1}/${clips.length} ${clip.name}`);
            }
            return {png: sheet.toDataURL("image/png"), clips: metadata};
        }, {start, rows, size, samples, selectedClips, reuse, capturedAt, sourceSnapshot});
        writeFileSync(join(out, filename), Buffer.from(result.png.split(",")[1], "base64"));
        manifest.pages = [...manifest.pages.filter((page) => page.filename !== filename), {filename, clips: result.clips}].sort((a, b) => a.filename.localeCompare(b.filename));
        writeFileSync(join(out, "catalog.json"), JSON.stringify(manifest, null, 2) + "\n");
        console.log(`Saved ${join(out, filename)}`);
    }
    if (manifest.errors.length) throw new Error(manifest.errors.join("\n"));
} finally {
    await browser.close();
    await server.close();
}
