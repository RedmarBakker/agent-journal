// A raised hat survives interruption as one opaque object, straightens clear of the head, and meets the worn mesh before the swap.
import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/hat-return");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async () => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf, REACTING} = await import("/src/figure/figure.js");
        const {BUTLER} = await import("/src/figure/butler.js");
        const {CHANGE_SECONDS} = await import("/src/figure/places.js");
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch(`/voices/figures/${files.butler}`)).arrayBuffer(), "butler", "/voices/figures/draco/");
        const stage = new Stage();
        stage.camera.updateMatrixWorld(true);
        const drawBody = stage.drawBody.bind(stage), drawScreen = stage.drawScreen.bind(stage);
        const render = (visible) => {
            stage.drawBody = visible ? drawBody : () => {};
            stage.drawScreen = visible ? drawScreen : () => {};
        };
        render(false);
        const tip = CLIPS.find((clip) => clip.name === "hat_tip");
        const idle = CLIPS.find((clip) => clip.name === "idle");
        const fall = CLIPS.find((clip) => clip.name === "fall");
        const hat = figure.propByName.get("top_hat");
        const worn = figure.stowable.filter((part) => ["butler_top_hat", "butler_top_hat_band"].includes(part.userData.item));
        const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
        const fromGlb = toGlb.clone().invert();
        const support = (moves) => toGlb.clone().multiply(moves.get("head")).multiply(fromGlb);
        const localOf = (moves) => support(moves).invert().multiply(hat.matrix);
        const difference = (a, b) => Math.max(...a.elements.map((value, i) => Math.abs(value - b.elements[i])));
        const smooth = (value) => value * value * (3 - 2 * value);
        const shell = figure.scene.getObjectByName("head_shell");
        const head = Array.from({length: shell.geometry.attributes.position.count}, (_, i) => new THREE.Vector3().fromBufferAttribute(shell.geometry.attributes.position, i).applyMatrix4(shell.matrixWorld));
        const indices = shell.geometry.index.array;
        const edges = new Set();
        for (let i = 0; i < indices.length; i += 3) {
            for (const [a, b] of [[indices[i], indices[i + 1]], [indices[i + 1], indices[i + 2]], [indices[i + 2], indices[i]]]) edges.add(`${Math.min(a, b)},${Math.max(a, b)}`);
        }
        const pairs = [...edges].map((edge) => edge.split(",").map(Number));
        const checks = {interruptions: 0, frames: 0, firstFrameError: 0, missingHeldFirstFrames: 0, singleOpaqueFailures: 0, minimumCrownClearance: Infinity, brimPivotError: 0, minimumCameraMargin: Infinity, highestPoint: -Infinity, maximumArmLengthError: 0, inactiveReturnFrames: 0, handoffError: 0, handoffGeometryError: 0, settledFailures: 0, staticError: 0};
        checks.poseSettings = Object.fromEntries(Object.entries(REACTING).filter(([name]) => name.startsWith("hat")));
        const angle = THREE.MathUtils.degToRad(REACTING.hatGripAngle);
        const radius = BUTLER.hat.crown + BUTLER.hat.brim;
        const brim = new THREE.Vector3(-radius * Math.cos(angle), BUTLER.hat.curl * Math.cos(angle) ** 2 + BUTLER.hat.thick / 2, radius * Math.sin(angle));
        // Measure the actual shaded meshes and their shader-expanded outlines against all six camera planes.
        hat.updateMatrixWorld(true);
        const hatPoints = [];
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
        const cameraBounds = (sample, placed) => {
            const projected = stage.camera.projectionMatrix.clone().multiply(stage.camera.matrixWorldInverse).multiply(placed);
            for (const point of hatPoints) {
                const at = point.clone().applyMatrix4(projected);
                const margin = Math.min(1 - Math.abs(at.x), 1 - Math.abs(at.y), 1 - Math.abs(at.z));
                if (margin < checks.minimumCameraMargin) {
                    checks.minimumCameraMargin = margin;
                    checks.cameraClosest = {...sample, point: at.toArray()};
                }
                checks.highestPoint = Math.max(checks.highestPoint, point.clone().applyMatrix4(placed).y);
            }
        };
        const size = 160, rowHeight = size + 22, columns = 7, samplesPerSecond = 120;
        const sheet = document.createElement("canvas"); sheet.width = columns * size; sheet.height = 4 * rowHeight;
        const paint = sheet.getContext("2d"); paint.fillStyle = "#15161a"; paint.fillRect(0, 0, sheet.width, sheet.height);
        const canvas = document.createElement("canvas"); canvas.width = canvas.height = size;
        const clearance = (local, sample) => {
            const inverse = local.clone().invert();
            const points = head.map((point) => point.clone().applyMatrix4(inverse));
            const above = points.filter((point) => point.y >= 0);
            for (const [a, b] of pairs) {
                const from = points[a], to = points[b];
                if ((from.y < 0) === (to.y < 0)) continue;
                above.push(from.clone().lerp(to, -from.y / (to.y - from.y)));
            }
            for (const point of above) {
                const margin = Math.min(BUTLER.hat.crown - Math.hypot(point.x, point.z), BUTLER.hat.height - point.y);
                if (margin < checks.minimumCrownClearance) {
                    checks.minimumCrownClearance = margin;
                    checks.closest = {...sample, point: point.toArray(), local: local.elements};
                }
            }
        };
        for (const [postureIndex, posture] of ["stand", "sit"].entries()) {
            for (const [nextIndex, next] of [idle, fall].entries()) {
                for (const facing of [0, 90, 180, 270]) {
                    for (const u of [0.220001, 0.25, 0.28, 0.32, 0.34, 0.4, 0.46, 0.5, 0.6, 0.67, 0.72, 0.74, 0.78, 0.82, 0.839999]) {
                        const row = postureIndex * 2 + nextIndex;
                        render(false);
                        const from = stage.draw(figure, tip, u * (tip.frames - 1), facing, canvas, {posture});
                        const before = hat.matrix.clone();
                        const initial = localOf(from);
                        const initialContact = brim.clone().applyMatrix4(initial);
                        let previous = from;
                        let wasHeld = hat.visible;
                        for (let frame = 0; frame <= 48; frame++) {
                            const elapsed = frame / samplesPerSecond;
                            const k = smooth(Math.min(elapsed / CHANGE_SECONDS, 1));
                            render(!facing && u === 0.5 && frame % 8 === 0);
                            const moves = stage.draw(figure, next, 0, facing, canvas, {posture: next === fall ? "stand" : posture, grabbed: next === fall, time: 10 + elapsed, blend: {from, previous, k}});
                            previous = moves;
                            for (const side of ["l", "r"]) {
                                for (const [a, b] of [[`upper_arm_${side}`, `forearm_${side}`], [`forearm_${side}`, `hand_${side}`]]) {
                                    const rest = figure.rig.heads.get(a).distanceTo(figure.rig.heads.get(b));
                                    const length = figure.rig.heads.get(a).clone().applyMatrix4(moves.get(a)).distanceTo(figure.rig.heads.get(b).clone().applyMatrix4(moves.get(b)));
                                    checks.maximumArmLengthError = Math.max(checks.maximumArmLengthError, Math.abs(length - rest));
                                }
                            }
                            checks.frames++;
                            if (!frame) {
                                checks.interruptions++;
                                checks.firstFrameError = Math.max(checks.firstFrameError, difference(before, hat.matrix));
                                if (!hat.visible) checks.missingHeldFirstFrames++;
                            }
                            const visibleWorn = worn.filter((part) => part.visible).length;
                            let opaque = true;
                            hat.traverse((part) => {
                                for (const material of [part.material ?? []].flat()) opaque &&= !material.transparent && material.opacity === 1 && (material.uniforms?.alpha?.value ?? 1) === 1;
                            });
                            if (!opaque || (hat.visible ? visibleWorn !== 0 : visibleWorn !== worn.length)) checks.singleOpaqueFailures++;
                            const local = localOf(moves);
                            if (hat.visible) {
                                if (!figure.propTransitions.active) checks.inactiveReturnFrames++;
                                const at = new THREE.Vector3(), turn = new THREE.Quaternion(), scale = new THREE.Vector3();
                                local.decompose(at, turn, scale);
                                // The upright hat seats around the authored head shell. While tilted, its crown and outline must clear it.
                                if (turn.angleTo(new THREE.Quaternion()) > 1e-6) {
                                    clearance(local, {posture, next: next.name, u, elapsed});
                                    checks.brimPivotError = Math.max(checks.brimPivotError, brim.clone().applyMatrix4(local).distanceTo(initialContact));
                                }
                            } else if (wasHeld) {
                                checks.handoffError = Math.max(checks.handoffError, difference(local, new THREE.Matrix4().makeTranslation(0, BUTLER.hat.base, 0)));
                                figure.scene.updateMatrixWorld(true);
                                const crown = hat.getObjectByName("top_hat_crown");
                                const wornCrown = figure.scene.getObjectByName("butler_top_hat");
                                wornCrown.skeleton.update();
                                for (let i = 0; i < crown.geometry.attributes.position.count; i++) {
                                    const heldPoint = new THREE.Vector3().fromBufferAttribute(crown.geometry.attributes.position, i).applyMatrix4(crown.matrixWorld);
                                    const wornPoint = wornCrown.applyBoneTransform(i, new THREE.Vector3().fromBufferAttribute(wornCrown.geometry.attributes.position, i)).applyMatrix4(wornCrown.matrixWorld);
                                    checks.handoffGeometryError = Math.max(checks.handoffGeometryError, heldPoint.distanceTo(wornPoint));
                                }
                            }
                            // The identical worn geometry keeps moving with the head after handoff; its camera check continues
                            // through the entire body blend instead of reading the now-hidden held prop's stale transform.
                            const placed = hat.visible ? hat.matrix : support(moves).multiply(new THREE.Matrix4().makeTranslation(0, BUTLER.hat.base, 0));
                            cameraBounds({posture, next: next.name, facing, u, elapsed, held: hat.visible}, placed);
                            wasHeld = hat.visible;
                            if (!facing && u === 0.5 && frame % 8 === 0) {
                                const column = frame / 8;
                                paint.drawImage(canvas, column * size, row * rowHeight);
                                paint.font = "11px sans-serif"; paint.fillStyle = "#c0c3d5";
                                paint.fillText(`${posture} → ${next.name} · ${Math.round(elapsed * 1000)}ms`, column * size + 6, row * rowHeight + size + 15);
                            }
                        }
                        if (hat.visible || figure.propTransitions.active || figure.propTransitions.present || figure.hatRecovery) checks.settledFailures++;
                    }
                }
            }
        }
        render(false);
        // No-clock samples must replace any return with their exact requested state, regardless of the samples preceding them.
        const sample = () => {
            stage.draw(figure, tip, 0.5 * (tip.frames - 1), 0, canvas);
            return hat.matrix.clone();
        };
        const staticHat = sample();
        stage.draw(figure, idle, 0, 0, canvas, {time: 30});
        stage.draw(figure, idle, 0, 0, canvas, {time: 30.1});
        checks.staticError = difference(staticHat, sample());
        stage.draw(figure, idle, 0, 0, canvas);
        checks.staticWorn = !hat.visible && worn.every((part) => part.visible) && !figure.propTransitions.active && !figure.hatRecovery;
        checks.cameraMarginPixelsAt112 = checks.minimumCameraMargin * 56;
        checks.samplesPerSecond = samplesPerSecond;
        return {checks, png: sheet.toDataURL("image/png")};
    });
    mkdirSync(out, {recursive: true});
    writeFileSync(resolve(out, "hat_return.png"), Buffer.from(result.png.split(",")[1], "base64"));
    writeFileSync(resolve(out, "checks.json"), `${JSON.stringify(result.checks, null, 2)}\n`);
    console.log(JSON.stringify({out, ...result.checks}));
    const checks = result.checks;
    // The worn GLB's float geometry and skin weights leave a few 1e-5 units of error even at the identical rigid transform.
    if (checks.firstFrameError > 1e-8 || checks.missingHeldFirstFrames || checks.singleOpaqueFailures || checks.minimumCrownClearance < 0.036 || checks.brimPivotError > 1e-6 || checks.minimumCameraMargin * 56 < 0.5 || checks.maximumArmLengthError > 1e-6 || checks.inactiveReturnFrames || checks.handoffError > 1e-5 || checks.handoffGeometryError > 5e-5 || checks.settledFailures || checks.staticError > 1e-8 || !checks.staticWorn) throw new Error("Hat interruption continuity failed");
} finally {
    await browser.close();
    await server.close();
}
