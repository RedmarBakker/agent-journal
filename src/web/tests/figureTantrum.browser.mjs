// Render the actual model's tantrum from each requested facing. Dense geometry checks can run without drawing the strip.
import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/tantrum");
const sources = new Map(["src/figure/figure.js", "src/figure/acts.js", "src/figure/butler.js"].map((name) => [resolve(root, name), readFileSync(resolve(root, name), "utf8")]));
const sourceHashes = Object.fromEntries([...sources].map(([path, source]) => [path.slice(root.length + 1), createHash("sha256").update(source).digest("hex")]));
const motionSource = sources.get(resolve(root, "src/figure/figure.js"));
const motionStart = motionSource.indexOf("const BUTLER_TANTRUM =");
const motionBlockSha256 = createHash("sha256").update(motionSource.slice(motionStart, motionSource.indexOf("function fume(", motionStart))).digest("hex");
const options = {
    voices: (process.env.TANTRUM_VOICES ?? "butler").split(","),
    facings: (process.env.TANTRUM_FACINGS ?? "0,90").split(",").map(Number),
    size: Number(process.env.TANTRUM_SIZE ?? 144),
    render: process.env.TANTRUM_RENDER !== "0",
    frames: Number(process.env.TANTRUM_FRAMES ?? 0),
    samples: Number(process.env.TANTRUM_SAMPLES ?? 720),
};
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "tantrum-review-snapshot", enforce: "pre", load: (id) => sources.get(id) ?? null}], server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async (options) => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {ConvexHull} = await import("/node_modules/three/examples/jsm/math/ConvexHull.js");
        const {CLIPS, REACTING, Stage, drawnPose, figureOf} = await import("/src/figure/figure.js");
        const {BUTLER} = await import("/src/figure/butler.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const clip = CLIPS.find((each) => each.name === "tantrum");
        const stage = new Stage();
        const drawBody = stage.drawBody.bind(stage), drawScreen = stage.drawScreen.bind(stage);
        const render = (shown) => {
            stage.drawBody = shown ? drawBody : () => {};
            stage.drawScreen = shown ? drawScreen : () => {};
        };
        const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2), fromGlb = toGlb.clone().invert();
        const support = (moves, bone) => toGlb.clone().multiply(moves.get(bone)).multiply(fromGlb);
        const planesOf = (points) => {
            const hull = new ConvexHull().setFromPoints(points);
            return [...new Map(hull.faces.map(({normal, constant}) => [[...normal.toArray(), constant].map((n) => n.toFixed(6)).join(","), {normal, constant}])).values()];
        };
        const clipped = (triangle, planes) => {
            let polygon = triangle;
            for (const {normal, constant} of planes) {
                const distances = polygon.map((point) => normal.dot(point) - constant);
                if (distances.every((distance) => distance > -1e-7)) return false;
                if (distances.every((distance) => distance <= 0)) continue;
                const next = [];
                for (let i = 0; i < polygon.length; i++) {
                    const a = polygon[i], b = polygon[(i + 1) % polygon.length];
                    const da = distances[i], db = distances[(i + 1) % polygon.length];
                    if (da <= 0) next.push(a);
                    if ((da <= 0) !== (db <= 0)) next.push(a.clone().lerp(b, da / (da - db)));
                }
                polygon = next;
                if (polygon.length < 3) return false;
            }
            return polygon.slice(2).some((point, i) => polygon[i + 1].clone().sub(polygon[0]).cross(point.clone().sub(polygon[0])).lengthSq() > 1e-14);
        };
        const times = [0, 0.14, 0.24, 0.34, 0.43, 0.54, 0.65, 0.7, 0.74, 0.78, 0.82, 0.86, 0.9, 0.94, 0.97, 1];
        const {size, facings} = options;
        const rowHeight = size + 22;
        const canvas = Object.assign(document.createElement("canvas"), {width: size, height: size});
        const sheet = Object.assign(document.createElement("canvas"), {width: size * 8, height: rowHeight * 2 * facings.length * options.voices.length});
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#20232b"; paint.fillRect(0, 0, sheet.width, sheet.height);
        const frames = [], meshes = {}, geometry = [];
        for (const [voiceIndex, voice] of options.voices.entries()) {
            const figure = await figureOf(await (await fetch(`/voices/figures/${index[voice]}`)).arrayBuffer(), voice, "/voices/figures/draco/");
            meshes[voice] = [];
            figure.scene.traverse((node) => {if (node.isSkinnedMesh && node.name) meshes[voice].push(node.name);});
            if (voice === "butler" && options.samples > 0) {
                render(false);
                figure.scene.updateMatrixWorld(true);
                const all = [];
                figure.scene.traverse((node) => {if (node.isSkinnedMesh && node.name) all.push(node);});
                for (const skeleton of new Set(all.map((node) => node.skeleton))) skeleton.update();
                const shapes = [
                    {name: "head", bone: "head", parts: all.filter((node) => node.name === "head_shell")},
                    ...["l", "r"].map((side) => ({name: `shoe_${side}`, bone: `foot_${side}`, parts: all.filter((node) => node.name.startsWith("butler_shoes__") && node.name.endsWith(`_${side}`))})),
                ].map((shape) => {
                    const points = [], expanded = [], sole = [], anchors = [];
                    for (const part of shape.parts) {
                        const normalMatrix = new THREE.Matrix3().getNormalMatrix(part.matrixWorld);
                        const unique = new Map();
                        for (let i = 0; i < part.geometry.attributes.position.count; i++) {
                            const point = part.getVertexPosition(i, new THREE.Vector3()).applyMatrix4(part.matrixWorld);
                            const key = point.toArray().map((n) => n.toFixed(7)).join(",");
                            if (unique.has(key)) continue;
                            unique.set(key, true);
                            points.push(point);
                            if (part.name.includes("__sole_")) sole.push(point);
                            const normal = new THREE.Vector3().fromBufferAttribute(part.geometry.attributes.hullNormal, i).applyMatrix3(normalMatrix).normalize();
                            expanded.push(point.clone().addScaledVector(normal, 0.036));
                        }
                        anchors.push({part, point: part.getVertexPosition(0, new THREE.Vector3()).applyMatrix4(part.matrixWorld)});
                    }
                    return {...shape, points, expanded, sole, anchors, planes: planesOf(points), outlinePlanes: planesOf(expanded), box: new THREE.Box3().setFromPoints(expanded)};
                });
                const hat = figure.propByName.get("top_hat");
                hat.updateMatrixWorld(true);
                const hatPoints = [], hatTriangles = [], outlined = [];
                hat.traverse((part) => {
                    if (!part.geometry) return;
                    const local = hat.matrixWorld.clone().invert().multiply(part.matrixWorld);
                    const {position, hullNormal} = part.geometry.attributes;
                    const push = part.material.uniforms?.push?.value ?? 0;
                    if (push) {
                        for (let i = 0; i < position.count; i++) outlined.push(new THREE.Vector3().fromBufferAttribute(position, i).addScaledVector(new THREE.Vector3().fromBufferAttribute(hullNormal, i).normalize(), push).applyMatrix4(local));
                        return;
                    }
                    const offset = hatPoints.length;
                    for (let i = 0; i < position.count; i++) hatPoints.push(new THREE.Vector3().fromBufferAttribute(position, i).applyMatrix4(local));
                    const indices = part.geometry.index?.array ?? Array.from({length: position.count}, (_, i) => i);
                    for (let i = 0; i < indices.length; i += 3) hatTriangles.push([indices[i] + offset, indices[i + 1] + offset, indices[i + 2] + offset]);
                });
                const worn = figure.stowable.filter((part) => ["butler_top_hat", "butler_top_hat_band"].includes(part.userData.item));
                const hand = figure.stance.busy.has("r") ? "l" : "r";
                const gripAngle = THREE.MathUtils.degToRad(REACTING.hatGripAngle);
                const brimRadius = BUTLER.hat.crown + BUTLER.hat.brim;
                const brimContact = new THREE.Vector3((hand === "r" ? -1 : 1) * brimRadius * Math.cos(gripAngle), BUTLER.hat.curl * Math.cos(gripAngle) ** 2 + BUTLER.hat.thick / 2, brimRadius * Math.sin(gripAngle));
                stage.camera.updateMatrixWorld(true);
                const camera = stage.camera.projectionMatrix.clone().multiply(stage.camera.matrixWorldInverse);
                const triangleBox = new THREE.Box3();
                for (const facing of facings) {
                    const measured = {voice, facing, poses: 0, headHits: 0, headOutlineHits: 0, shoeHits: 0, minimumSole: Infinity, minimumHat: Infinity, minimumCameraMargin: Infinity, maximumRigidError: 0, visibilityFailures: 0, gripSamples: 0, gripDwellSamples: 0, maximumGripError: 0, maximumGroundedDisplacement: 0, missingHandSupport: 0, failures: []};
                    const contacts = {head: [], headOutline: [], shoe_l: [], shoe_r: []};
                    stage.draw(figure, clip, 0.4 * (clip.frames - 1), facing, null);
                    figure.scene.updateMatrixWorld(true);
                    const grounded = hat.matrixWorld.clone();
                    for (let sample = 0; sample <= options.samples; sample++) {
                        const u = sample / options.samples;
                        const moves = stage.draw(figure, clip, u * (clip.frames - 1), facing, null);
                        figure.scene.updateMatrixWorld(true);
                        for (const skeleton of new Set(all.map((node) => node.skeleton))) skeleton.update();
                        const world = hat.visible ? hat.matrixWorld.clone() : support(moves, "head").multiply(new THREE.Matrix4().makeTranslation(0, BUTLER.hat.base, 0));
                        if (u >= 0.4 && u <= 0.72) {
                            measured.maximumGroundedDisplacement = Math.max(measured.maximumGroundedDisplacement, ...world.elements.map((value, i) => Math.abs(value - grounded.elements[i])));
                        }
                        if (u >= 0.7 && u <= 0.96) {
                            const {pose} = drawnPose(figure.rig, figure.stance, clip, u * (clip.frames - 1), facing);
                            const fingers = pose.grip(hand, [REACTING.hatFingers, 0, 0]).applyMatrix4(moves.get(`hand_${hand}`)).applyMatrix4(toGlb);
                            measured.maximumGripError = Math.max(measured.maximumGripError, fingers.distanceTo(brimContact.clone().applyMatrix4(world)));
                            measured.gripSamples++;
                            if (u <= 0.72) measured.gripDwellSamples++;
                            const held = pose.props.get("top_hat");
                            if (u > 0.7 + 1e-8 && u < 0.91 - 1e-8 && (held?.bone !== `hand_${hand}` || held?.frame !== `hand_${hand}`)) measured.missingHandSupport++;
                        }
                        const projected = camera.clone().multiply(world);
                        for (const point of outlined) {
                            const at = point.clone().applyMatrix4(projected);
                            const margin = Math.min(1 - Math.abs(at.x), 1 - Math.abs(at.y), 1 - Math.abs(at.z));
                            if (margin < measured.minimumCameraMargin) {
                                measured.minimumCameraMargin = margin;
                                measured.cameraWorst = {u, point: at.toArray()};
                            }
                        }
                        measured.minimumHat = Math.min(measured.minimumHat, ...hatPoints.map((point) => point.clone().applyMatrix4(world).y));
                        if (hat.visible ? worn.some((part) => part.visible) : worn.some((part) => !part.visible)) measured.visibilityFailures++;
                        for (const shape of shapes) {
                            const carried = support(moves, shape.bone);
                            for (const {part, point} of shape.anchors) {
                                const actual = part.getVertexPosition(0, new THREE.Vector3()).applyMatrix4(part.matrixWorld);
                                measured.maximumRigidError = Math.max(measured.maximumRigidError, actual.distanceTo(point.clone().applyMatrix4(carried)));
                            }
                            for (const point of shape.sole) {
                                const height = point.clone().applyMatrix4(carried).y;
                                if (height < measured.minimumSole) {
                                    measured.minimumSole = height;
                                    measured.soleWorst = {u, shape: shape.name};
                                }
                            }
                            const relative = carried.clone().invert().multiply(world);
                            const points = hatPoints.map((point) => point.clone().applyMatrix4(relative));
                            if (!new THREE.Box3().setFromPoints(points).intersectsBox(shape.box)) continue;
                            let hit = false, outlineHit = false;
                            for (const indices of hatTriangles) {
                                const triangle = indices.map((i) => points[i]);
                                if (!triangleBox.setFromPoints(triangle).intersectsBox(shape.box)) continue;
                                if (!hit && clipped(triangle, shape.planes)) hit = true;
                                if (shape.name === "head" && !outlineHit && clipped(triangle, shape.outlinePlanes)) outlineHit = true;
                                if (hit && (shape.name !== "head" || outlineHit)) break;
                            }
                            if (shape.name === "head") {
                                if (hit) {measured.headHits++; contacts.head.push(u);}
                                if (outlineHit) {measured.headOutlineHits++; contacts.headOutline.push(u);}
                            } else if (hit) {
                                contacts[shape.name].push(u);
                                measured.shoeHits++;
                            }
                            if ((hit || outlineHit) && measured.failures.length < 24) measured.failures.push({u, shape: shape.name, hit, outlineHit});
                        }
                        measured.poses++;
                    }
                    measured.minimumCameraPixelsAt112 = measured.minimumCameraMargin * 56;
                    measured.contactRanges = Object.fromEntries(Object.entries(contacts).map(([name, phases]) => {
                        const ranges = [];
                        for (const u of phases) {
                            const last = ranges.at(-1);
                            if (last && u - last[1] <= 1.01 / options.samples) last[1] = u;
                            else ranges.push([u, u]);
                        }
                        return [name, ranges];
                    }));
                    geometry.push(measured);
                }
            }
            render(true);
            if (options.render) {
                for (const [view, facing] of facings.entries()) {
                    for (const [sample, u] of times.entries()) {
                        stage.draw(figure, clip, u * (clip.frames - 1), facing, canvas);
                        const row = (voiceIndex * facings.length + view) * 2 + Math.floor(sample / 8), column = sample % 8;
                        paint.drawImage(canvas, column * size, row * rowHeight);
                        paint.font = "11px sans-serif"; paint.fillStyle = "#d2d4e2";
                        paint.fillText(`${voice} ${facing}° · ${u.toFixed(2)}`, column * size + 5, row * rowHeight + size + 15);
                    }
                }
            }
            for (let frame = 0; frame < options.frames; frame++) {
                for (const facing of facings) {
                    stage.draw(figure, clip, frame / (options.frames - 1) * (clip.frames - 1), facing, canvas);
                    frames.push({voice, facing, frame, png: canvas.toDataURL("image/png")});
                }
            }
        }
        return {png: options.render ? sheet.toDataURL("image/png") : null, frames, checks: {clip: clip.name, frames: clip.frames, fps: clip.fps, views: options.voices.length * facings.length, renderedSamples: options.render ? times.length * options.voices.length * facings.length : 0, meshes, geometry}};
    }, options);
    mkdirSync(out, {recursive: true});
    if (result.png) writeFileSync(resolve(out, "tantrum.png"), Buffer.from(result.png.split(",")[1], "base64"));
    for (const {voice, facing, frame, png} of result.frames) {
        const folder = resolve(out, "frames", `${voice}_${facing}`);
        mkdirSync(folder, {recursive: true});
        writeFileSync(resolve(folder, `frame_${String(frame).padStart(3, "0")}.png`), Buffer.from(png.split(",")[1], "base64"));
    }
    result.checks.sourceSha256 = sourceHashes["src/figure/figure.js"];
    result.checks.sourceHashes = sourceHashes;
    result.checks.motionBlockSha256 = motionBlockSha256;
    result.checks.errors = errors;
    writeFileSync(resolve(out, "checks.json"), JSON.stringify(result.checks, null, 2) + "\n");
    console.log(JSON.stringify({out, ...result.checks, meshes: undefined}));
    if (errors.length) throw new Error("Tantrum rendering raised browser errors");
    if (!process.env.TANTRUM_REPORT_ONLY && result.checks.geometry.some((each) => each.headHits || each.headOutlineHits || each.shoeHits || each.minimumSole < -0.002 || each.minimumHat < -0.002 || each.minimumCameraMargin < 0 || each.maximumRigidError > 1e-4 || each.visibilityFailures || !each.gripSamples || !each.gripDwellSamples || each.maximumGripError > 1e-5 || each.maximumGroundedDisplacement > 1e-5 || each.missingHandSupport)) throw new Error("Tantrum geometry check failed");
} finally {
    await browser.close();
    await server.close();
}
