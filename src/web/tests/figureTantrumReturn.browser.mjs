// Live tantrums can be cancelled from any phase. A hat away from the head fades at its last position before returning; every voice
// settles into the requested pose with its ordinary carried items restored and no transition left keeping the player active.
import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/tantrum");
const voices = (process.env.TANTRUM_VOICES ?? "butler,homie,coach,colleague,squire").split(",");
const render = process.env.TANTRUM_RETURN_RENDER !== "0";
const paths = ["src/figure/figure.js", "src/figure/acts.js", "src/figure/butler.js", "src/figure/homie.js", "src/figure/headphoneClearance.js", "src/figure/player.js", "src/figure/blend.js", "src/figure/propTransition.js"];
const snapshots = new Map(paths.map((path) => [resolve(root, path), readFileSync(resolve(root, path), "utf8")]));
const sourceHashes = Object.fromEntries([...snapshots].map(([path, source]) => [path.slice(root.length + 1), createHash("sha256").update(source).digest("hex")]));
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "tantrum-return-snapshot", enforce: "pre", load: (id) => snapshots.get(id) ?? null}], server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const browserErrors = [];
    page.on("pageerror", (error) => browserErrors.push(error.message));
    page.on("console", (message) => { if (message.type() === "log") console.log(message.text()); });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async ({voices, render}) => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf} = await import("/src/figure/figure.js");
        const {FigurePlayer} = await import("/src/figure/player.js");
        const {BUTLER} = await import("/src/figure/butler.js");
        const {CHANGE_SECONDS} = await import("/src/figure/places.js");
        const {PROP_FADE_SECONDS} = await import("/src/figure/propTransition.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const figures = new Map();
        const clip = CLIPS.find((each) => each.name === "tantrum");
        const idle = CLIPS.find((each) => each.name === "idle");
        const fall = CLIPS.find((each) => each.name === "fall");
        const stage = new Stage();
        stage.camera.updateMatrixWorld(true);
        const projection = stage.camera.projectionMatrix.clone().multiply(stage.camera.matrixWorldInverse);
        const body = stage.drawBody.bind(stage), screen = stage.drawScreen.bind(stage);
        const rendering = (visible) => {
            stage.drawBody = visible ? body : () => {};
            stage.drawScreen = visible ? screen : () => {};
        };
        rendering(false);
        const canvas = Object.assign(document.createElement("canvas"), {width: 144, height: 144});
        const phases = [0.08, 0.15, 0.21, 0.3, 0.5, 0.65, 0.7, 0.72, 0.78, 0.84, 0.9, 0.91, 0.93, 0.98];
        const facings = [0, 90, 180, 270];
        const fade = PROP_FADE_SECONDS;
        const times = [...new Set([...Array.from({length: 61}, (_, i) => i / 120), 0.08, fade - 1e-4, fade, fade + 1e-4, 0.24, 2 * fade - 1e-4, 2 * fade, 2 * fade + 1e-4])].sort((a, b) => a - b);
        const pictures = [0, 0.08, fade, 0.24, 2 * fade, 0.5];
        const picturePhases = [0.7, 0.84, 0.93];
        const sheet = Object.assign(document.createElement("canvas"), {width: canvas.width * pictures.length, height: (canvas.height + 24) * picturePhases.length});
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a"; paint.fillRect(0, 0, sheet.width, sheet.height);
        const checks = {voices, postures: clip.postures, facings, phases, samplesPerSecond: 120, cases: 0, frames: 0, failures: 0, maximumFirstPoseError: 0, maximumFirstHatError: 0, maximumFrozenHatError: 0, maximumRestoringHatError: 0, maximumHandoffGeometryError: 0, maximumFinalPoseError: 0, maximumAlphaError: 0, minimumCameraMargin: Infinity, cameraFrames: 0, cameraFailures: 0, highestHatPoint: -Infinity, staticResets: 0, results: [], player: [], errors: []};
        const fail = (kind, detail) => {
            checks.failures++;
            if (checks.errors.length < 30) {
                checks.errors.push({kind, ...detail});
                console.log(JSON.stringify({failure: {kind, ...detail}}));
            }
        };
        const difference = (a, b) => Math.max(...a.elements.map((value, i) => Math.abs(value - b.elements[i])));
        const poseDifference = (a, b) => Math.max(...[...a].map(([bone, matrix]) => difference(matrix, b.get(bone))));
        const materials = (object) => {
            const found = new Set();
            object.traverse((node) => { for (const material of [node.material ?? []].flat()) found.add(material); });
            return [...found];
        };
        const flags = (material) => [material.opacity, material.transparent, material.depthWrite, material.forceSinglePass, material.uniforms?.alpha?.value ?? 1, Boolean(material.userData.propOpacity)];
        const stateOf = (objects) => objects.map((object) => ({object, visible: object.visible, materials: materials(object).map((material) => ({material, flags: flags(material)}))}));
        const sameState = (state) => state.every(({object, visible, materials}) => object.visible === visible && materials.every(({material, flags: before}) => flags(material).every((value, i) => typeof value === "number" ? Math.abs(value - before[i]) < 1e-8 : value === before[i])));
        const smooth = (value) => { const k = Math.min(Math.max(value, 0), 1); return k * k * (3 - 2 * k); };
        const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2), fromGlb = toGlb.clone().invert();
        const wornAt = (moves) => toGlb.clone().multiply(moves.get("head")).multiply(fromGlb).multiply(new THREE.Matrix4().makeTranslation(0, BUTLER.hat.base, 0));

        for (const voice of voices) {
            const figure = await figureOf(await (await fetch("/voices/figures/" + index[voice])).arrayBuffer(), voice, "/voices/figures/draco/");
            figures.set(voice, figure);
            const hat = figure.propByName.get("top_hat");
            const hatMaterials = materials(hat);
            const hatPoints = [];
            if (voice === "butler") {
                hat.updateMatrixWorld(true);
                hat.traverse((part) => {
                    if (!part.geometry) return;
                    const {position, hullNormal} = part.geometry.attributes;
                    const push = part.material.uniforms?.push?.value ?? 0;
                    const local = hat.matrixWorld.clone().invert().multiply(part.matrixWorld);
                    for (let i = 0; i < position.count; i++) {
                        const point = new THREE.Vector3().fromBufferAttribute(position, i);
                        if (push) point.addScaledVector(new THREE.Vector3().fromBufferAttribute(hullNormal, i), push);
                        hatPoints.push(point.applyMatrix4(local));
                    }
                });
            }
            const worn = figure.stowable.filter((part) => ["butler_top_hat", "butler_top_hat_band"].includes(part.userData.item));
            const ordinaryObjects = [...figure.inHand, ...worn, hat];
            const alpha = () => hatMaterials[0]?.uniforms?.alpha?.value ?? hatMaterials[0]?.opacity ?? 1;
            for (const posture of clip.postures) for (const next of [idle, fall]) for (const facing of facings) for (const u of phases) {
                const label = {voice, posture, next: next.name, facing, u};
                const options = {posture: next === fall ? "stand" : posture, grabbed: next === fall};
                const expected = stage.draw(figure, next, 0, facing, canvas, options);
                const expectedState = stateOf(ordinaryObjects);
                const from = stage.draw(figure, clip, u * (clip.frames - 1), facing, canvas, {posture});
                const initialState = stateOf(ordinaryObjects);
                const initialHat = hat.matrix.clone();
                const held = voice === "butler" && u > 0.12 && u < 0.96;
                const tossed = held && u >= 0.18 && u < 0.91;
                const kind = tossed ? u >= 0.7 ? "pickup" : "toss" : held ? "held" : "worn";
                const item = {...label, kind, frames: 0, failures: checks.failures};
                if (voice === "butler" && (hat.visible !== held || (held ? worn.some((part) => part.visible) : worn.some((part) => !part.visible)) || alpha() !== 1)) fail("normal hat state", label);
                if (tossed !== (figure.hatReturn?.returnMode === "toss")) fail("hat return mode", label);
                let previous = from, wasHeld = hat.visible;
                for (const elapsed of times) {
                    const column = pictures.findIndex((time) => Math.abs(time - elapsed) < 1e-10);
                    const row = picturePhases.indexOf(u);
                    const shown = render && voice === "butler" && posture === "stand" && next === idle && facing === 0 && row >= 0 && column >= 0;
                    rendering(shown);
                    const k = smooth(elapsed / CHANGE_SECONDS);
                    const moves = stage.draw(figure, next, 0, facing, canvas, {...options, time: 10 + elapsed, blend: {from, previous, k}});
                    previous = moves;
                    checks.frames++; item.frames++;
                    if (!elapsed) {
                        const poseError = poseDifference(from, moves);
                        checks.maximumFirstPoseError = Math.max(checks.maximumFirstPoseError, poseError);
                        if (poseError > 1e-8 || !sameState(initialState)) fail("first frame changed", {...label, poseError});
                        if (held) {
                            const hatError = difference(initialHat, hat.matrix);
                            checks.maximumFirstHatError = Math.max(checks.maximumFirstHatError, hatError);
                            if (hatError > 1e-8) fail("first hat transform changed", {...label, hatError});
                        }
                    }
                    if (voice === "butler") {
                        const visibleWorn = worn.filter((part) => part.visible).length;
                        if (hat.visible || visibleWorn) {
                            const placed = hat.visible ? hat.matrix : wornAt(moves);
                            const projected = projection.clone().multiply(placed);
                            let margin = Infinity;
                            for (const point of hatPoints) {
                                const at = point.clone().applyMatrix4(projected);
                                const current = Math.min(1 - Math.abs(at.x), 1 - Math.abs(at.y), 1 - Math.abs(at.z));
                                if (current < checks.minimumCameraMargin) {
                                    checks.minimumCameraMargin = current;
                                    checks.cameraClosest = {...label, elapsed, held: hat.visible, point: at.toArray()};
                                }
                                margin = Math.min(margin, current);
                                checks.highestHatPoint = Math.max(checks.highestHatPoint, point.clone().applyMatrix4(placed).y);
                            }
                            checks.cameraFrames++;
                            if (margin < -1e-8) {
                                checks.cameraFailures++;
                                fail("outlined hat leaves camera", {...label, elapsed, margin});
                            }
                        }
                        if ((hat.visible && visibleWorn) || (visibleWorn && visibleWorn !== worn.length)) fail("double or incomplete hat", {...label, elapsed});
                        if (!tossed && !hat.visible && visibleWorn !== worn.length) fail("missing opaque hat", {...label, elapsed});
                        if (tossed && elapsed < 2 * fade - 1e-8) {
                            if (visibleWorn || !figure.propTransitions.active) fail("toss return stopped early", {...label, elapsed});
                            const expectedAlpha = elapsed < fade ? 1 - smooth(elapsed / fade) : smooth((elapsed - fade) / fade);
                            const error = Math.max(...hatMaterials.flatMap((material) => [Math.abs(material.opacity - expectedAlpha), Math.abs((material.uniforms?.alpha?.value ?? material.opacity) - expectedAlpha)]));
                            checks.maximumAlphaError = Math.max(checks.maximumAlphaError, error);
                            if (error > 1e-8) fail("hat fade changed", {...label, elapsed, error});
                            if (elapsed < fade - 1e-8) {
                                const error = difference(initialHat, hat.matrix);
                                checks.maximumFrozenHatError = Math.max(checks.maximumFrozenHatError, error);
                                if (error > 1e-8) fail("free hat moved before fading", {...label, elapsed, error});
                            } else {
                                const error = difference(wornAt(moves), hat.matrix);
                                checks.maximumRestoringHatError = Math.max(checks.maximumRestoringHatError, error);
                                if (error > 1e-8 || (Math.abs(elapsed - fade) < 1e-8 && hat.visible)) fail("visible hat relocation", {...label, elapsed, error});
                            }
                        }
                        if (!hat.visible && wasHeld && visibleWorn === worn.length) {
                            figure.scene.updateMatrixWorld(true);
                            const crown = hat.getObjectByName("top_hat_crown"), wornCrown = figure.scene.getObjectByName("butler_top_hat");
                            wornCrown.skeleton.update();
                            for (let i = 0; i < crown.geometry.attributes.position.count; i++) {
                                const point = new THREE.Vector3().fromBufferAttribute(crown.geometry.attributes.position, i).applyMatrix4(crown.matrixWorld);
                                const other = wornCrown.getVertexPosition(i, new THREE.Vector3()).applyMatrix4(wornCrown.matrixWorld);
                                checks.maximumHandoffGeometryError = Math.max(checks.maximumHandoffGeometryError, point.distanceTo(other));
                            }
                        }
                        wasHeld = hat.visible;
                    }
                    if (shown) {
                        paint.drawImage(canvas, column * canvas.width, row * (canvas.height + 24));
                        paint.fillStyle = "#d2d4e2"; paint.font = "11px sans-serif";
                        paint.fillText(["Grasp", "Lift", "Placement"][row] + " · " + Math.round(elapsed * 1000) + "ms", column * canvas.width + 8, row * (canvas.height + 24) + canvas.height + 16);
                    }
                }
                rendering(false);
                const finalError = poseDifference(expected, previous);
                checks.maximumFinalPoseError = Math.max(checks.maximumFinalPoseError, finalError);
                if (finalError > 1e-7 || !sameState(expectedState) || figure.hatReturn || figure.hatRecovery || figure.propTransitions.active || figure.propTransitions.present) fail("did not settle", {...label, finalError});
                item.failures = checks.failures - item.failures;
                checks.results.push(item); checks.cases++;
            }
            console.log(JSON.stringify({voice, checkedCases: checks.results.filter((each) => each.voice === voice).length, failures: checks.failures}));
        }

        // Exact static samples must reset a half-finished fade for frame strips and cache generation.
        const butler = figures.get("butler");
        if (butler) {
            const hat = butler.propByName.get("top_hat"), phase = 0.5 * (clip.frames - 1);
            stage.draw(butler, clip, phase, 0, canvas, {posture: "stand"});
            const exact = hat.matrix.clone();
            for (const elapsed of [0.08, 0.24]) {
                stage.draw(butler, idle, 0, 0, canvas, {time: 30});
                stage.draw(butler, idle, 0, 0, canvas, {time: 30 + elapsed});
                stage.draw(butler, clip, phase, 0, canvas, {posture: "stand"});
                checks.staticResets++;
                if (difference(exact, hat.matrix) > 1e-8 || !hat.visible || materials(hat).some((material) => material.opacity !== 1 || material.transparent || material.userData.propOpacity)) fail("static thrown hat reset", {elapsed});
            }
            stage.draw(butler, idle, 0, 0, canvas);
            if (hat.visible || butler.hatReturn || butler.hatRecovery || butler.propTransitions.active || butler.propTransitions.present) fail("static worn reset", {});
        }

        // Exercise the actual player's cache decisions with its clock controlled, while retaining real pose and material updates.
        const oldNow = Object.getOwnPropertyDescriptor(performance, "now");
        let clock = 0;
        Object.defineProperty(performance, "now", {configurable: true, value: () => clock});
        try {
            for (const [voice, figure] of figures) {
                const player = new FigurePlayer(figure, canvas);
                player.stage.drawBody = player.stage.drawScreen = () => {};
                const draw = player.stage.draw.bind(player.stage);
                let calls = 0;
                player.stage.draw = (...args) => { calls++; return draw(...args); };
                clock = 1000; player.show(idle, 0, 0, {posture: "stand"});
                clock = 2000; player.show(clip, 0.5 * (clip.frames - 1), 0, {posture: "stand"});
                clock = 2300; player.show(clip, 0.5 * (clip.frames - 1), 0, {posture: "stand"});
                let afterBody = 0;
                for (let frame = 0; frame <= 25; frame++) {
                    const elapsed = frame * 0.02;
                    const before = calls, active = figure.propTransitions.active;
                    const blending = player.blending();
                    clock = 2400 + elapsed * 1000;
                    player.show(idle, 0, 0, {posture: "stand"});
                    if (voice === "butler" && elapsed >= 0.28 && elapsed <= 0.3) {
                        if (!active || blending || calls === before) fail("cached before hat fade finished", {voice, elapsed, active, blending});
                        else afterBody++;
                    }
                }
                const before = calls;
                clock = 3000; player.show(idle, 0, 0, {posture: "stand"});
                clock = 3100; player.show(idle, 0, 0, {posture: "stand"});
                const stable = calls === before && !player.blending() && !figure.propTransitions.active && !figure.propTransitions.present && !figure.hatReturn && !figure.hatRecovery;
                if (!stable) fail("player stays active after recovery", {voice, extraCalls: calls - before});
                checks.player.push({voice, calls, drawsAfterBodyBlend: afterBody, stable});
                player.stage.renderer.dispose(); player.stage.renderer.forceContextLoss();
                player.stage.screenRenderer.dispose(); player.stage.screenRenderer.forceContextLoss();
            }
        } finally {
            if (oldNow) Object.defineProperty(performance, "now", oldNow);
            else delete performance.now;
        }
        if (checks.maximumHandoffGeometryError > 5e-5) fail("worn handoff geometry", {error: checks.maximumHandoffGeometryError});
        checks.cameraMarginPixelsAt112 = checks.minimumCameraMargin * 56;
        return {checks, png: render && butler ? sheet.toDataURL("image/png") : null};
    }, {voices, render});
    mkdirSync(out, {recursive: true});
    const report = {...result.checks, sourceHashes, browserErrors};
    writeFileSync(resolve(out, "interruptions.json"), JSON.stringify(report, null, 2) + "\n");
    if (result.png) writeFileSync(resolve(out, "interruptions.png"), Buffer.from(result.png.split(",")[1], "base64"));
    console.log(JSON.stringify({out, cases: report.cases, frames: report.frames, failures: report.failures, browserErrors}));
    if (report.failures || browserErrors.length) throw new Error("Tantrum interruption or cache recovery failed");
} finally {
    await browser.close();
    await server.close();
}
