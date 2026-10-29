// Integration checks for a fitted persistent headset: normal clip handoffs, rotation covariance, deterministic frame order,
// adjacent poses and a representative warmed production draw. Collision checks live in figureHeadphones.browser.mjs.
import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/headphone-fit");
const paths = ["src/figure/figure.js", "src/figure/homie.js", "src/figure/headphoneClearance.js"];
const snapshots = new Map(paths.map((path) => [resolve(root, path), readFileSync(path.endsWith("headphoneClearance.js") && process.env.HEADPHONE_CLEARANCE_SOURCE || path.endsWith("homie.js") && process.env.HEADPHONE_HOMIE_SOURCE || resolve(root, path), "utf8")]));
const sourceHashes = Object.fromEntries([...snapshots].map(([path, source]) => [path.slice(root.length + 1), createHash("sha256").update(source).digest("hex")]));
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "headphone-integration-snapshot", enforce: "pre", load: (id) => snapshots.get(id) ?? null}], server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage(), browserErrors = [];
    page.on("pageerror", (error) => browserErrors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async ({renderPictures, benchmark, benchmarkPoseOnly, motionWindows, samplesPerSecond}) => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf, drawnPose} = await import("/src/figure/figure.js");
        const {fittedHeadphonesAt, headphonesAt} = await import("/src/figure/homie.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch("/voices/figures/" + index.homie)).arrayBuffer(), "homie", "/voices/figures/draco/");
        const stage = new Stage(), body = stage.drawBody.bind(stage), screen = stage.drawScreen.bind(stage);
        const render = (on) => { stage.drawBody = on ? body : () => {}; stage.drawScreen = on ? screen : () => {}; };
        render(false);
        const canvas = Object.assign(document.createElement("canvas"), {width: 224, height: 224});
        const headset = figure.headphones, groove = CLIPS.find(({name}) => name === "groove"), idle = CLIPS.find(({name}) => name === "idle");
        const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2), fromGlb = toGlb.clone().invert();
        const report = {normalHandoffs: [], facingCovariance: [], frameOrderChecks: [], motion: [], drawCost: [], rawMotionThresholdPasses: true, motionWarnings: [], errors: []};
        const shape = () => {
            headset.root.updateMatrixWorld(true);
            return {cups: headset.cups.map((cup) => [...cup.matrixWorld.elements]), band: [...headset.band.geometry.attributes.position.array]};
        };
        const arrayDifference = (a, b) => a.length !== b.length || ![...a, ...b].every(Number.isFinite) ? Infinity : Math.max(0, ...a.map((value, i) => Math.abs(value - b[i])));
        const shapeDifference = (a, b) => Math.max(arrayDifference(a.band, b.band), ...a.cups.map((cup, i) => arrayDifference(cup, b.cups[i])));
        const opaque = () => {
            let yes = headset.root.visible;
            headset.root.traverse((node) => { if (node.material && (node.material.opacity !== 1 || node.material.transparent || !node.material.depthWrite)) yes = false; });
            return yes;
        };
        for (const posture of groove.postures) for (const facing of [0, 90]) {
            const fromIdle = stage.draw(figure, idle, 0, facing, canvas, {posture}), idleShape = shape();
            stage.draw(figure, groove, 0, facing, canvas, {posture, time: 1, blend: {from: fromIdle, previous: fromIdle, k: 0}});
            const start = {posture, facing, direction: "idle to groove", error: shapeDifference(idleShape, shape()), opaque: opaque()};
            const fromGroove = stage.draw(figure, groove, groove.frames - 1, facing, canvas, {posture}), grooveShape = shape();
            stage.draw(figure, idle, 0, facing, canvas, {posture, time: 2, blend: {from: fromGroove, previous: fromGroove, k: 0}});
            const finish = {posture, facing, direction: "groove to idle", error: shapeDifference(grooveShape, shape()), opaque: opaque()};
            report.normalHandoffs.push(start, finish);
            for (const check of [start, finish]) if (check.error > 5e-7 || !check.opaque || headset.returning) report.errors.push({kind: "normal handoff", ...check});
        }
        const targets = [{clip: "idle", u: 0.5}, {clip: "tantrum", u: 0.25}, {clip: "groove", u: 0.17}, {clip: "groove", u: 0.48}, {clip: "groove", u: 11 / 12}, {clip: "rummage", u: 0.85}];
        for (const target of targets) {
            const clip = CLIPS.find(({name}) => name === target.clip);
            const moves = stage.draw(figure, clip, target.u * (clip.frames - 1), 0, canvas, {posture: "stand"}), originalShape = shape();
            const original = headset.previous;
            stage.draw(figure, idle, 20, 90, canvas, {posture: "lounge"});
            stage.draw(figure, clip, target.u * (clip.frames - 1), 0, canvas, {posture: "stand"});
            const error = shapeDifference(originalShape, shape());
            report.frameOrderChecks.push({...target, error});
            if (error > 5e-7) report.errors.push({kind: "frame order", ...target, error});
            for (const facing of [30, 90, 180, 270]) {
                const rotation = new THREE.Matrix4().makeRotationY(facing * Math.PI / 180);
                const turn = fromGlb.clone().multiply(rotation).multiply(toGlb);
                const rotated = new Map([...moves].map(([bone, matrix]) => [bone, turn.clone().multiply(matrix)]));
                const fitted = fittedHeadphonesAt(headset, clip === groove ? target.u : null, rotated);
                const bandError = original.band.length !== fitted.band.length ? Infinity : Math.max(...original.band.map((point, i) => point.clone().applyMatrix4(rotation).distanceTo(fitted.band[i])));
                const cupError = Math.max(...original.cups.map((cup, i) => cup.at.clone().applyMatrix4(rotation).distanceTo(fitted.cups[i].at)));
                report.facingCovariance.push({...target, facing, bandError, cupError});
                if (bandError > 2e-6 || cupError > 2e-6) report.errors.push({kind: "facing covariance", ...target, facing, bandError, cupError});
            }
        }
        const sampled = (points) => {
            const distances = [0];
            for (let i = 1; i < points.length; i++) distances.push(distances.at(-1) + points[i].distanceTo(points[i - 1]));
            return Array.from({length: 81}, (_, i) => {
                const distance = distances.at(-1) * i / 80;
                let segment = 1;
                while (segment < distances.length - 1 && distances[segment] < distance) segment++;
                const size = distances[segment] - distances[segment - 1];
                return points[segment - 1].clone().lerp(points[segment], size ? (distance - distances[segment - 1]) / size : 0);
            });
        };
        const windows = motionWindows ?? [{clip: "groove", a: 0, b: 1}, {clip: "tantrum", a: 0.1, b: 0.5}, {clip: "rummage", a: 0.7, b: 0.95}];
        for (const window of windows) {
            const clip = CLIPS.find(({name}) => name === window.clip), count = Math.ceil((window.b - window.a) * (clip.frames - 1) / clip.fps * samplesPerSecond);
            const check = {...window, samples: count + 1, samplesPerSecond, maximumBandStep: 0, maximumCupStep: 0, worstBandPhase: null, worstCupPhase: null, maximumUnresolved: 0};
            let previous = null;
            for (let i = 0; i <= count; i++) {
                const u = window.a + (window.b - window.a) * i / count;
                const {pose, turned} = drawnPose(figure.rig, figure.stance, clip, u * (clip.frames - 1), 0, {posture: "stand"});
                const moves = pose.moves(turned), state = fittedHeadphonesAt(headset, clip === groove ? u : null, moves), raw = headphonesAt(clip === groove ? u : null, moves), points = sampled(state.band);
                check.maximumUnresolved = Math.max(check.maximumUnresolved, state.unresolved ?? 0);
                if (previous) {
                    const step = Math.max(...points.map((point, index) => point.distanceTo(previous.points[index])));
                    if (step > check.maximumBandStep) { check.maximumBandStep = step; check.worstBandPhase = u; }
                    const cupStep = Math.max(...state.cups.map((cup, index) => cup.at.distanceTo(previous.state.cups[index].at)));
                    if (cupStep > check.maximumCupStep) { check.maximumCupStep = cupStep; check.worstCupPhase = u; check.rawCupStepAtWorst = Math.max(...raw.cups.map((cup, index) => cup.at.distanceTo(previous.raw.cups[index].at))); check.cupCorrectionStepAtWorst = Math.max(...state.cups.map((cup, index) => cup.at.clone().sub(raw.cups[index].at).distanceTo(previous.state.cups[index].at.clone().sub(previous.raw.cups[index].at)))); }
                }
                previous = {points, state, raw};
            }
            report.motion.push(check);
            // A raw control-point speed limit is a diagnostic, not a visibility assertion: sleeves can conceal a fitted route change,
            // and rapid authored body motion needs a denser sample to distinguish speed from a discontinuity.
            if (check.maximumBandStep > 0.12 || check.maximumCupStep > 0.08) { report.rawMotionThresholdPasses = false; report.motionWarnings.push({...check}); }
            if (check.maximumUnresolved) report.errors.push({kind: "unresolved band segment", ...check});
        }
        render(true);
        const size = canvas.width, label = 24, times = [0.75, 0.8, 0.825, 0.85, 0.875, 0.9];
        const sheet = Object.assign(document.createElement("canvas"), {width: size * times.length, height: (size + label) * 2});
        const paint = sheet.getContext("2d"); paint.fillStyle = "#252832"; paint.fillRect(0, 0, sheet.width, sheet.height);
        const rummage = CLIPS.find(({name}) => name === "rummage");
        for (const [row, facing] of (renderPictures ? [0, 90] : []).entries()) for (const [column, u] of times.entries()) {
            stage.draw(figure, rummage, u * (rummage.frames - 1), facing, canvas, {posture: "stand"});
            paint.drawImage(canvas, column * size, row * (size + label));
            paint.fillStyle = "#e0e4ee"; paint.font = "12px sans-serif";
            paint.fillText(`Rummage ${facing}° · ${u.toFixed(3)}`, column * size + 8, row * (size + label) + size + 17);
        }
        const colliderState = headset.colliders;
        for (const clip of benchmark ? [idle, groove, rummage] : []) for (const fitting of [true, false]) {
            headset.colliders = fitting ? colliderState : null;
            render(!benchmarkPoseOnly);
            for (let i = 0; i < 10; i++) stage.draw(figure, clip, (0.4 + i / 100) * (clip.frames - 1), 0, canvas, {posture: "stand"});
            for (const visible of benchmarkPoseOnly ? [false] : [false, true]) {
                render(visible);
                const times = [];
                for (let i = 0; i < 48; i++) {
                    const began = performance.now();
                    stage.draw(figure, clip, (0.42 + i / 240) * (clip.frames - 1), 0, canvas, {posture: "stand"});
                    times.push(performance.now() - began);
                }
                const ordered = [...times].sort((a, b) => a - b);
                report.drawCost.push({clip: clip.name, fitting, rendering: visible, canvasPixels: size, samples: times.length, warmupSamples: 10, averageMilliseconds: times.reduce((sum, value) => sum + value, 0) / times.length, medianMilliseconds: ordered[Math.floor(ordered.length / 2)], percentile95Milliseconds: ordered[Math.floor(ordered.length * 0.95)], maximumMilliseconds: ordered.at(-1)});
            }
        }
        headset.colliders = colliderState;
        report.passes = !report.errors.length;
        return {report, png: renderPictures ? sheet.toDataURL("image/png") : null};
    }, {renderPictures: process.env.HEADPHONE_FIT_RENDER !== "0", benchmark: process.env.HEADPHONE_FIT_BENCHMARK === "1", benchmarkPoseOnly: process.env.HEADPHONE_FIT_BENCHMARK_POSE_ONLY === "1", motionWindows: process.env.HEADPHONE_FIT_WINDOWS ? JSON.parse(process.env.HEADPHONE_FIT_WINDOWS) : null, samplesPerSecond: Number(process.env.HEADPHONE_FIT_HZ ?? 120)});
    mkdirSync(out, {recursive: true});
    writeFileSync(resolve(out, "integration.json"), JSON.stringify({...result.report, sourceHashes, browserErrors}, null, 2) + "\n");
    if (result.png) writeFileSync(resolve(out, "free-cup-motion.png"), Buffer.from(result.png.split(",")[1], "base64"));
    console.log(JSON.stringify(result.report));
    if ((!result.report.passes || browserErrors.length) && !process.env.HEADPHONE_REPORT_ONLY) throw new Error("Headphone integration check failed");
} finally {
    await browser.close();
    await server.close();
}
