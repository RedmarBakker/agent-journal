// A music gesture can be interrupted while the headset is being lifted, worn or lowered. The one visible headset retires in place,
// returns at the neck, restores its materials and lets the live player settle, including after a previously cached groove frame.
import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/headphones");
const render = process.env.HEADPHONE_RETURN_RENDER !== "0";
const playerOnly = process.env.HEADPHONE_RETURN_PLAYER_ONLY === "1";
const smoke = process.env.HEADPHONE_RETURN_SMOKE === "1";
const paths = ["src/figure/figure.js", "src/figure/homie.js", "src/figure/headphoneClearance.js", "src/figure/butler.js", "src/figure/acts.js", "src/figure/player.js", "src/figure/blend.js", "src/figure/places.js", "src/figure/frame.js", "src/figure/propTransition.js"];
const snapshots = new Map(paths.map((path) => [resolve(root, path), readFileSync(resolve(root, path), "utf8")]));
const sourceHashes = Object.fromEntries([...snapshots].map(([path, source]) => [path.slice(root.length + 1), createHash("sha256").update(source).digest("hex")]));
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "headphone-return-snapshot", enforce: "pre", load: (id) => snapshots.get(id) ?? null}], server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const browserErrors = [];
    page.on("pageerror", (error) => browserErrors.push(error.message));
    page.on("console", (message) => { if (message.type() === "log") console.log(message.text()); });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async ({render, playerOnly, smoke}) => {
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {FigurePlayer} = await import("/src/figure/player.js");
        const {fittedHeadphonesAt} = await import("/src/figure/homie.js");
        const {CHANGE_SECONDS} = await import("/src/figure/places.js");
        const {PROP_FADE_SECONDS} = await import("/src/figure/propTransition.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch("/voices/figures/" + index.homie)).arrayBuffer(), "homie", "/voices/figures/draco/");
        const headset = figure.headphones;
        const clip = CLIPS.find((each) => each.name === "groove");
        const idle = CLIPS.find((each) => each.name === "idle");
        const fall = CLIPS.find((each) => each.name === "fall");
        const stage = new Stage();
        const body = stage.drawBody.bind(stage), screen = stage.drawScreen.bind(stage);
        const rendering = (visible) => {
            stage.drawBody = visible ? body : () => {};
            stage.drawScreen = visible ? screen : () => {};
        };
        rendering(false);
        const canvas = Object.assign(document.createElement("canvas"), {width: 176, height: 176});
        // The hands already control the headset before it lifts, and still control it just after lowering. Those grasp/release
        // phases retain their fitted placement through cancellation too; only the ungripped endpoints use the ordinary neck state.
        const phases = [{u: 0.08, name: "before lift", raised: true}, {u: 0.22, name: "put-on", raised: true}, {u: 0.5, name: "worn", raised: true}, {u: 0.8, name: "take-off", raised: true}, {u: 0.96, name: "after lowering", raised: true}].filter((phase) => !smoke || ["put-on", "worn"].includes(phase.name));
        const postures = smoke ? ["stand"] : clip.postures, facings = smoke ? [0] : [0, 90], nexts = smoke ? [idle] : [idle, fall];
        const fade = PROP_FADE_SECONDS;
        const times = [...new Set([...Array.from({length: 61}, (_, i) => i / 120), 0.08, fade - 1e-4, fade, fade + 1e-4, 0.24, 2 * fade - 1e-4, 2 * fade, 2 * fade + 1e-4])].sort((a, b) => a - b);
        const pictures = [0, 0.08, fade, 0.24, 2 * fade, 0.5];
        const picturePhases = ["put-on", "worn", "take-off"];
        const sheet = Object.assign(document.createElement("canvas"), {width: canvas.width * pictures.length, height: (canvas.height + 24) * picturePhases.length});
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a"; paint.fillRect(0, 0, sheet.width, sheet.height);
        const checks = {voice: "homie", scope: smoke ? "smoke" : playerOnly ? "player" : "complete", postures, facings, phases, samplesPerSecond: 120, cases: 0, frames: 0, failures: 0, maximumFirstPoseError: 0, maximumFirstHeadsetError: 0, maximumFrozenHeadsetError: 0, maximumNeckPlacementError: 0, maximumFinalPoseError: 0, maximumFinalHeadsetError: 0, maximumAlphaError: 0, minimumBandVertices: Infinity, maximumBandVertices: 0, materialChecks: 0, singleHeadsetChecks: 0, staticResets: 0, results: [], player: [], errors: []};
        const fail = (kind, detail) => {
            checks.failures++;
            if (checks.errors.length < 40) {
                checks.errors.push({kind, ...detail});
                console.log(JSON.stringify({failure: {kind, ...detail}}));
            }
        };
        const maximumDifference = (values) => values.every(Number.isFinite) ? Math.max(0, ...values) : Infinity;
        const arrayDifference = (a, b) => {
            if (a.length !== b.length) return Infinity;
            let maximum = 0;
            for (let i = 0; i < a.length; i++) {
                if (!Number.isFinite(a[i]) || !Number.isFinite(b[i])) return Infinity;
                maximum = Math.max(maximum, Math.abs(a[i] - b[i]));
            }
            return maximum;
        };
        const matrixDifference = (a, b) => arrayDifference(a.elements, b.elements);
        const poseDifference = (a, b) => Math.max(...[...a].map(([bone, matrix]) => matrixDifference(matrix, b.get(bone))));
        const shape = () => {
            headset.root.updateMatrixWorld(true);
            return {cups: headset.cups.map((cup) => cup.matrixWorld.clone()), bandMatrix: headset.band.matrixWorld.clone(), band: Float32Array.from(headset.band.geometry.attributes.position.array)};
        };
        // An adaptive band may have a different number of vertices. A length mismatch or non-finite coordinate must fail, never
        // turn the maximum into NaN and silently bypass the error threshold.
        const shapeDifference = (a, b) => a.cups.length !== b.cups.length ? Infinity : maximumDifference([...a.cups.map((cup, i) => matrixDifference(cup, b.cups[i])), matrixDifference(a.bandMatrix, b.bandMatrix), arrayDifference(a.band, b.band)]);
        const stateDifference = (a, b) => a.cups.length !== b.cups.length || a.band.length !== b.band.length ? Infinity : maximumDifference([...a.cups.flatMap((cup, i) => [cup.at.distanceTo(b.cups[i].at), 1 - Math.abs(cup.turn.dot(b.cups[i].turn))]), ...a.band.map((point, i) => point.distanceTo(b.band[i]))]);
        const materials = new Set();
        headset.root.traverse((node) => { for (const material of [node.material ?? []].flat()) materials.add(material); });
        const flags = (material) => [material.opacity, material.transparent, material.depthWrite, material.forceSinglePass, material.uniforms?.alpha?.value ?? 1, Boolean(material.userData.propOpacity)];
        const materialState = () => [...materials].map((material) => ({material, flags: flags(material)}));
        const sameMaterials = (state) => state.every(({material, flags: before}) => flags(material).every((value, i) => typeof value === "number" ? Math.abs(value - before[i]) < 1e-8 : value === before[i]));
        const smooth = (value) => { const k = Math.min(Math.max(value, 0), 1); return k * k * (3 - 2 * k); };
        const singleHeadset = () => {
            let roots = 0, legacy = 0;
            figure.scene.traverse((node) => {
                if (node.name === "homie_headphones") roots++;
                if (node.name.startsWith("homie_headphones__") && node.visible) legacy++;
            });
            return roots === 1 && !legacy && headset.root.children.length === 3 && headset.cups.length === 2 && headset.cups.every((cup) => cup.parent === headset.root) && headset.band.parent === headset.root;
        };
        const optionsFor = (next, posture) => ({posture: next === fall ? "stand" : posture, grabbed: next === fall, airborne: next === fall});
        const measure = (label, elapsed, moves, initial, baseline) => {
            checks.frames++;
            const actual = shape();
            checks.minimumBandVertices = Math.min(checks.minimumBandVertices, actual.band.length / 3);
            checks.maximumBandVertices = Math.max(checks.maximumBandVertices, actual.band.length / 3);
            if (!elapsed) {
                const poseError = poseDifference(initial.moves, moves), error = shapeDifference(initial.shape, actual);
                checks.maximumFirstPoseError = Math.max(checks.maximumFirstPoseError, poseError);
                checks.maximumFirstHeadsetError = Math.max(checks.maximumFirstHeadsetError, error);
                if (poseError > 1e-8 || error > 5e-7 || !sameMaterials(initial.materials) || !headset.root.visible) fail("first frame changed", {...label, poseError, error});
            }
            checks.singleHeadsetChecks++;
            if (!singleHeadset()) fail("duplicate or incomplete headset", {...label, elapsed});
            const expectedAlpha = label.raised ? elapsed < fade ? 1 - smooth(elapsed / fade) : smooth((elapsed - fade) / fade) : 1;
            const error = Math.max(...baseline.materials.flatMap(({material, flags: before}) => [Math.abs(material.opacity - before[0] * expectedAlpha), Math.abs((material.uniforms?.alpha?.value ?? 1) - before[4] * expectedAlpha)]));
            checks.maximumAlphaError = Math.max(checks.maximumAlphaError, error);
            if (error > 1e-8) fail("headset fade changed", {...label, elapsed, error, alpha: [...materials][0].opacity});
            checks.materialChecks++;
            if (expectedAlpha < 1 - 1e-8 && [...materials].some((material) => !material.transparent || material.depthWrite || !material.forceSinglePass || !material.userData.propOpacity)) fail("fade material flags", {...label, elapsed});
            if (Math.abs(elapsed - fade) < 1e-8 && label.raised && headset.root.visible) fail("visible headset relocation", {...label, elapsed});
            if (label.raised && elapsed < fade - 1e-8) {
                const error = shapeDifference(initial.shape, actual);
                checks.maximumFrozenHeadsetError = Math.max(checks.maximumFrozenHeadsetError, error);
                if (error > 5e-7) fail("free headset moved before fading", {...label, elapsed, error});
            } else if (!label.raised || elapsed > fade + 1e-8) {
                const error = stateDifference(headset.previous, fittedHeadphonesAt(headset, null, moves));
                checks.maximumNeckPlacementError = Math.max(checks.maximumNeckPlacementError, error);
                if (error > 1e-8) fail("headset did not follow neck", {...label, elapsed, error});
            }
            if (label.raised && elapsed < 2 * fade - 1e-8 && (!headset.returning || !figure.propTransitions.active)) fail("recovery stopped early", {...label, elapsed});
            if (elapsed > 2 * fade + 1e-8 && (headset.returning || headset.raised || figure.propTransitions.active || !sameMaterials(baseline.materials) || !headset.root.visible)) fail("recovery state not cleaned", {...label, elapsed});
        };
        const finish = (label, moves, baseline) => {
            const poseError = poseDifference(baseline.moves, moves), error = shapeDifference(baseline.shape, shape());
            checks.maximumFinalPoseError = Math.max(checks.maximumFinalPoseError, poseError);
            checks.maximumFinalHeadsetError = Math.max(checks.maximumFinalHeadsetError, error);
            if (poseError > 1e-7 || error > 5e-7 || headset.returning || headset.raised || figure.propTransitions.active || !sameMaterials(baseline.materials)) fail("did not settle", {...label, poseError, error});
            checks.cases++;
        };
        for (const posture of playerOnly ? [] : postures) for (const next of nexts) for (const facing of facings) for (const phase of phases) {
            const label = {mode: "stage", posture, next: next.name, facing, ...phase};
            const options = optionsFor(next, posture);
            const baselineMoves = stage.draw(figure, next, 0, facing, canvas, options);
            const baseline = {moves: baselineMoves, shape: shape(), materials: materialState()};
            const from = stage.draw(figure, clip, phase.u * (clip.frames - 1), facing, canvas, {posture});
            const initial = {moves: from, shape: shape(), materials: materialState()};
            const before = checks.failures;
            let previous = from;
            for (const elapsed of times) {
                const column = pictures.findIndex((time) => Math.abs(time - elapsed) < 1e-10), row = picturePhases.indexOf(phase.name);
                const shown = render && posture === "stand" && next === idle && facing === 0 && row >= 0 && column >= 0;
                rendering(shown);
                previous = stage.draw(figure, next, 0, facing, canvas, {...options, time: 10 + elapsed, blend: {from, previous, k: smooth(elapsed / CHANGE_SECONDS)}});
                measure(label, elapsed, previous, initial, baseline);
                if (shown) {
                    paint.drawImage(canvas, column * canvas.width, row * (canvas.height + 24));
                    paint.fillStyle = "#d2d4e2"; paint.font = "12px sans-serif";
                    paint.fillText(phase.name + " · " + Math.round(elapsed * 1000) + "ms", column * canvas.width + 8, row * (canvas.height + 24) + canvas.height + 17);
                }
            }
            rendering(false);
            finish(label, previous, baseline);
            checks.results.push({...label, frames: times.length, failures: checks.failures - before});
        }
        console.log(JSON.stringify({stageCases: checks.cases, frames: checks.frames, failures: checks.failures}));

        // Static strip samples must erase either half of a live fade before rendering the exact requested gesture again.
        for (const elapsed of playerOnly || smoke ? [] : [0.08, 0.24]) {
            stage.draw(figure, clip, 0.5 * (clip.frames - 1), 0, canvas, {posture: "stand"});
            const exact = shape(), authored = materialState();
            stage.draw(figure, idle, 0, 0, canvas, {posture: "stand", time: 30});
            stage.draw(figure, idle, 0, 0, canvas, {posture: "stand", time: 30 + elapsed});
            stage.draw(figure, clip, 0.5 * (clip.frames - 1), 0, canvas, {posture: "stand"});
            checks.staticResets++;
            if (shapeDifference(exact, shape()) > 5e-7 || headset.returning || !headset.raised || !headset.root.visible || !sameMaterials(authored) || figure.propTransitions.active) fail("static raised reset", {elapsed});
            stage.draw(figure, idle, 0, 0, canvas, {posture: "stand"});
            if (headset.returning || headset.raised || !headset.root.visible || !sameMaterials(authored) || figure.propTransitions.active) fail("static neck reset", {elapsed});
        }

        // Real FigurePlayer calls exercise its cache rather than simulating it. On a second play, an integer frame may be copied from
        // the prior groove; the first interruption must still preserve the headset that was pictured in that frame.
        const oldNow = Object.getOwnPropertyDescriptor(performance, "now");
        let clock = 0;
        Object.defineProperty(performance, "now", {configurable: true, value: () => clock});
        try {
            for (const posture of smoke ? [] : postures) {
                const player = new FigurePlayer(figure, canvas);
                player.stage.drawBody = player.stage.drawScreen = () => {};
                const draw = player.stage.draw.bind(player.stage);
                let calls = 0;
                player.stage.draw = (...args) => { calls++; return draw(...args); };
                for (const next of [idle, fall]) for (const phase of phases.filter((phase) => ["put-on", "worn", "take-off"].includes(phase.name))) {
                    const frame = Math.round(phase.u * (clip.frames - 1));
                    const options = optionsFor(next, posture);
                    const baselineMoves = stage.draw(figure, next, 0, 0, canvas, options);
                    const baseline = {moves: baselineMoves, shape: shape(), materials: materialState()};
                    let reference;
                    for (const replay of [false, true]) {
                        const began = clock + 1000;
                        for (let step = 0; step <= 30; step++) {
                            clock = began + step * 500 / 30;
                            player.show(idle, 0, 0, {posture});
                        }
                        for (let step = 0; step <= 30; step++) {
                            clock = began + 1000 + step * 500 / 30;
                            player.show(clip, replay ? 0 : frame, 0, {posture});
                        }
                        const beforeFrame = calls;
                        clock = began + 1600; player.show(clip, frame, 0, {posture});
                        const cached = replay && calls === beforeFrame;
                        if (!replay) reference = {moves: player.moves, shape: shape(), materials: materialState()};
                        const initial = {moves: player.moves, shape: cached ? reference.shape : shape(), materials: cached ? reference.materials : materialState()};
                        const label = {mode: replay ? "replayed player" : "live player", posture, next: next.name, facing: 0, ...phase, u: frame / (clip.frames - 1)};
                        const before = checks.failures;
                        let afterBody = 0;
                        for (const elapsed of times) {
                            const count = calls;
                            clock = began + 1700 + elapsed * 1000;
                            player.show(next, 0, 0, options);
                            measure(label, elapsed, player.moves, initial, baseline);
                            if (elapsed >= CHANGE_SECONDS + 0.03 && elapsed < 2 * fade - 1e-8) {
                                if (player.blending() || calls === count || !figure.propTransitions.active) fail("cached before headphone fade finished", {...label, elapsed, blending: player.blending(), drew: calls !== count, active: figure.propTransitions.active});
                                else afterBody++;
                            }
                        }
                        finish(label, player.moves, baseline);
                        const settledCalls = calls;
                        clock += 100; player.show(next, 0, 0, options);
                        clock += 100; player.show(next, 0, 0, options);
                        const stable = calls === settledCalls && !player.blending() && !headset.returning && !headset.raised && !figure.propTransitions.active;
                        if (!stable) fail("player stays active after recovery", {...label, extraCalls: calls - settledCalls});
                        checks.player.push({...label, cached, drawsAfterBodyBlend: afterBody, stable, frames: times.length, failures: checks.failures - before});
                    }
                }
                player.stage.renderer.dispose(); player.stage.renderer.forceContextLoss();
                player.stage.screenRenderer.dispose(); player.stage.screenRenderer.forceContextLoss();
            }
        } finally {
            if (oldNow) Object.defineProperty(performance, "now", oldNow);
            else delete performance.now;
        }
        return {checks, png: render && !playerOnly && !smoke ? sheet.toDataURL("image/png") : null};
    }, {render, playerOnly, smoke});
    mkdirSync(out, {recursive: true});
    const report = {...result.checks, sourceHashes, browserErrors};
    writeFileSync(resolve(out, "interruptions.json"), JSON.stringify(report, null, 2) + "\n");
    if (result.png) writeFileSync(resolve(out, "interruptions.png"), Buffer.from(result.png.split(",")[1], "base64"));
    console.log(JSON.stringify({out, cases: report.cases, frames: report.frames, failures: report.failures, browserErrors}));
    if (report.failures || browserErrors.length) throw new Error("Headphone interruption or cache recovery failed");
} finally {
    await browser.close();
    await server.close();
}
