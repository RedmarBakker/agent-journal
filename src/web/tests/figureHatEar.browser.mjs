// The hat gesture retains its original side-head clearance after the ears are removed. The source ears supply the old reserve only;
// none is rendered. Clipping actual glove, cuff and sleeve triangles catches crossings between sampled vertices too.
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/hat-ear");
const plugins = process.env.HAT_SOURCE ? [{name: "hat-source-probe", enforce: "pre", load: (id) => id.endsWith("/src/figure/figure.js") ? readFileSync(process.env.HAT_SOURCE, "utf8") : null}] : [];
const server = await createServer({root, plugins, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    page.on("console", (message) => {if (message.type() === "log") console.log(message.text());});
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const variants = process.env.HAT_EAR_VARIANTS ? JSON.parse(readFileSync(process.env.HAT_EAR_VARIANTS, "utf8")) : [null];
    const result = await page.evaluate(async ({samples, render, variants, postures, failFast, transitions, yaws, approaches, clipName}) => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {ConvexHull} = await import("/node_modules/three/examples/jsm/math/ConvexHull.js");
        const {GLTFLoader} = await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
        const {DRACOLoader} = await import("/node_modules/three/examples/jsm/loaders/DRACOLoader.js");
        const {CLIPS, HAND, REACTING, Stage, figureOf} = await import("/src/figure/figure.js");
        const {BUTLER} = await import("/src/figure/butler.js");
        const {partOf} = await import("/src/figure/acts.js");
        const {CHANGE_SECONDS} = await import("/src/figure/places.js");
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const bytes = await (await fetch(`/voices/figures/${files.butler}`)).arrayBuffer();
        const figure = await figureOf(bytes, "butler", "/voices/figures/draco/");
        const decoder = new DRACOLoader().setDecoderPath("/voices/figures/draco/");
        const source = (await new GLTFLoader().setDRACOLoader(decoder).parseAsync(bytes, "")).scene;
        source.updateMatrixWorld(true);
        decoder.dispose();
        const stage = new Stage();
        const body = stage.drawBody.bind(stage), screen = stage.drawScreen.bind(stage);
        stage.drawBody = stage.drawScreen = () => {};
        const clip = CLIPS.find((each) => each.name === clipName);
        const side = figure.stance.busy.has("r") ? "l" : "r";
        const all = [];
        figure.scene.traverse((node) => {if (node.isSkinnedMesh && node.name) all.push(node);});
        const skeletons = new Set(all.map((node) => node.skeleton));
        if (all.some((node) => node.name.startsWith("ear_"))) throw new Error("The loaded butler still has ears");
        const ears = [];
        source.traverse((node) => { if (node.isSkinnedMesh && node.name.startsWith("ear_") && node.name.endsWith(`_${side}`)) ears.push(node); });
        const arms = all.filter((node) => node.name.endsWith(`_${side}`) && /hand_shell|wrist_joint|elbow_joint|__cuff_|__sleeve_/.test(node.name));
        const update = () => {
            figure.scene.updateMatrixWorld(true);
            for (const skeleton of skeletons) skeleton.update();
        };
        update();
        const earPoints = ears.flatMap((mesh) => Array.from({length: mesh.geometry.attributes.position.count}, (_, i) => mesh.getVertexPosition(i, new THREE.Vector3()).applyMatrix4(mesh.matrixWorld)));
        const glove = arms.find((mesh) => mesh.name === `hand_shell_${side}`);
        const glovePoints = Array.from({length: glove.geometry.attributes.position.count}, (_, i) => glove.getVertexPosition(i, new THREE.Vector3()).applyMatrix4(glove.matrixWorld));
        const gloveIndices = glove.geometry.index.array;
        const hull = new ConvexHull().setFromPoints(earPoints);
        const planes = [...new Map(hull.faces.map(({normal, constant}) => [[...normal.toArray(), constant].map((each) => each.toFixed(6)).join(","), {normal, constant}])).values()];
        const earBox = new THREE.Box3().setFromPoints(earPoints);
        const outline = 0.036;
        const nearBox = earBox.clone().expandByScalar(0.12);
        const paddedBox = earBox.clone().expandByScalar(outline);
        const signed = (at) => {
            let distance = -Infinity;
            for (const {normal, constant} of planes) distance = Math.max(distance, normal.dot(at) - constant);
            return distance;
        };
        const meshes = arms.map((mesh) => {
            const vertices = [], unique = new Map(), remap = [];
            const {position, skinIndex, skinWeight} = mesh.geometry.attributes;
            for (let i = 0; i < position.count; i++) {
                const key = [...new THREE.Vector3().fromBufferAttribute(position, i).toArray(), ...new THREE.Vector4().fromBufferAttribute(skinIndex, i).toArray(), ...new THREE.Vector4().fromBufferAttribute(skinWeight, i).toArray()].map((each) => each.toFixed(6)).join(",");
                if (!unique.has(key)) {unique.set(key, vertices.length); vertices.push(i);}
                remap[i] = unique.get(key);
            }
            const indices = mesh.geometry.index?.array ?? Array.from({length: position.count}, (_, i) => i);
            const triangles = [];
            for (let i = 0; i < indices.length; i += 3) triangles.push([remap[indices[i]], remap[indices[i + 1]], remap[indices[i + 2]]]);
            return {mesh, vertices, triangles};
        });
        console.log(JSON.stringify({earPlanes: planes.length, meshes: meshes.map(({mesh, vertices, triangles}) => ({name: mesh.name, vertices: vertices.length, triangles: triangles.length}))}));
        const clipped = (triangle, padding) => {
            let polygon = triangle;
            for (const {normal, constant} of planes) {
                let inside = false, outside = false;
                for (const point of polygon) {
                    if (normal.dot(point) - constant <= padding) inside = true;
                    else outside = true;
                }
                if (!inside) return false;
                if (!outside) continue;
                const next = [];
                for (let i = 0; i < polygon.length; i++) {
                    const a = polygon[i], b = polygon[(i + 1) % polygon.length];
                    const da = normal.dot(a) - constant - padding, db = normal.dot(b) - constant - padding;
                    if (da <= 0) next.push(a);
                    if ((da <= 0) !== (db <= 0)) next.push(a.clone().lerp(b, da / (da - db)));
                }
                polygon = next;
                if (polygon.length < 3) return false;
            }
            return polygon.slice(2).some((vertex, i) => polygon[i + 1].clone().sub(polygon[0]).cross(vertex.clone().sub(polygon[0])).lengthSq() > 1e-16);
        };
        const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2), fromGlb = toGlb.clone().invert();
        const angle = THREE.MathUtils.degToRad(REACTING.hatGripAngle ?? 0), radius = BUTLER.hat.crown + BUTLER.hat.brim;
        const contact = new THREE.Vector3((side === "r" ? -1 : 1) * radius * Math.cos(angle), BUTLER.hat.curl * Math.cos(angle) ** 2 + BUTLER.hat.thick / 2, radius * Math.sin(angle));
        const gloveContacts = new Map();
        const gloveContact = (fingers) => {
            if (gloveContacts.has(fingers)) return gloveContacts.get(fingers);
            const at = figure.rig.heads.get(`hand_${side}`).clone().add(new THREE.Vector3((side === "r" ? -1 : 1) * (HAND.grip + fingers), HAND.forward, 0)).applyMatrix4(toGlb);
            const triangle = new THREE.Triangle(), closest = new THREE.Vector3();
            const result = {at: at.toArray(), distance: Infinity, nearest: null};
            let angle = 0;
            for (let i = 0; i < gloveIndices.length; i += 3) {
                triangle.set(glovePoints[gloveIndices[i]], glovePoints[gloveIndices[i + 1]], glovePoints[gloveIndices[i + 2]]).closestPointToPoint(at, closest);
                const distance = closest.distanceTo(at);
                if (distance < result.distance) Object.assign(result, {distance, nearest: closest.toArray()});
                const a = triangle.a.clone().sub(at), b = triangle.b.clone().sub(at), c = triangle.c.clone().sub(at);
                angle += 2 * Math.atan2(a.dot(b.clone().cross(c)), a.length() * b.length() * c.length() + a.dot(b) * c.length() + b.dot(c) * a.length() + c.dot(a) * b.length());
            }
            result.inside = Math.abs(angle) > Math.PI * 2;
            gloveContacts.set(fingers, result);
            return result;
        };
        const triangleBox = new THREE.Box3();
        const checks = {clip: clip.name, samples, poses: 0, outline, earMeshes: ears.map((mesh) => mesh.name), armMeshes: arms.map((mesh) => mesh.name), earBounds: {min: earBox.min.toArray(), max: earBox.max.toArray()}, earPlanes: planes.length, reacting: Object.fromEntries(Object.entries(REACTING).filter(([name]) => name.startsWith("hat"))), results: []};
        const cases = variants.flatMap((variant) => (postures ?? clip.postures).flatMap((posture) => yaws.flatMap((facing) => transitions
            ? [0.18, 0.33, 0.5, 0.8].flatMap((sourcePhase) => ["idle", "fall"].map((target) => ({variant, posture, facing, transition: {sourcePhase, target}})))
            : [{variant, posture, facing}])));
        for (const {variant, posture, facing, transition} of cases) {
            if (variant) Object.assign(REACTING, variant.reacting);
            const from = transition ? stage.draw(figure, clip, transition.sourcePhase * (clip.frames - 1), facing, null, {posture}) : null;
            const target = transition ? CLIPS.find((each) => each.name === transition.target) : null;
            const frameCount = transition ? Math.round(CHANGE_SECONDS * 60) : samples;
            let previous = from;
            const summary = {variant, posture, facing, transition, testedFrames: 0, complete: false, minimumVertexMargin: 0.12, collidingFrames: 0, outlineFrames: 0, worst: null, firstCollision: null, lastCollision: null, highestHat: -Infinity, maximumLift: 0, maximumTargetError: 0, targetWorst: null, gloveContact: gloveContact(REACTING.hatFingers), meshes: Object.fromEntries(meshes.map(({mesh}) => [mesh.name, {minimumVertexMargin: 0.12, collidingFrames: 0, outlineFrames: 0}]))};
            for (let sample = 0; sample <= frameCount; sample++) {
                const u = sample / frameCount, frame = u * (clip.frames - 1);
                if (approaches && clip.name === "hat_tip" && !transition && u > 0.22 && u < 0.84 && Math.abs(u - 0.5) > 1e-9) continue;
                const moves = transition
                    ? stage.draw(figure, target, 0, facing, null, {posture: transition.target === "fall" ? "stand" : posture, grabbed: transition.target === "fall", time: 10 + sample / 60, blend: {from, previous, k: u * u * (3 - 2 * u)}})
                    : stage.draw(figure, clip, frame, facing, null, {posture});
                previous = moves;
                update();
                const head = toGlb.clone().multiply(moves.get("head")).multiply(fromGlb), inverse = head.clone().invert();
                let collisions = 0, outlined = 0;
                for (const {mesh, vertices, triangles} of meshes) {
                    if (!mesh.visible) continue;
                    const measured = summary.meshes[mesh.name];
                    const points = vertices.map((i) => mesh.getVertexPosition(i, new THREE.Vector3()).applyMatrix4(mesh.matrixWorld).applyMatrix4(inverse));
                    const bounds = new THREE.Box3().setFromPoints(points);
                    if (!bounds.intersectsBox(nearBox)) continue;
                    const margins = points.map((vertex) => nearBox.containsPoint(vertex) ? signed(vertex) : Infinity);
                    for (const [index, vertex] of points.entries()) {
                        const margin = margins[index];
                        measured.minimumVertexMargin = Math.min(measured.minimumVertexMargin, margin);
                        if (margin < summary.minimumVertexMargin) {
                            summary.minimumVertexMargin = margin;
                            summary.worst = {u, frame, elapsedMs: transition ? sample / 60 * 1000 : undefined, mesh: mesh.name, margin, point: vertex.toArray(), wrist: new THREE.Vector3().copy(figure.rig.heads.get(`hand_${side}`)).applyMatrix4(moves.get(`hand_${side}`)).applyMatrix4(toGlb).applyMatrix4(inverse).toArray()};
                        }
                    }
                    if (!bounds.intersectsBox(paddedBox)) continue;
                    let meshCollisions = 0, meshOutlined = 0;
                    for (const indices of triangles) {
                        const triangle = indices.map((i) => points[i]);
                        triangleBox.setFromPoints(triangle);
                        if (!triangleBox.intersectsBox(paddedBox) || (!indices.some((i) => margins[i] < outline) && !clipped(triangle, outline))) continue;
                        meshOutlined++;
                        if (triangleBox.intersectsBox(earBox) && (indices.some((i) => margins[i] < 0) || clipped(triangle, 0))) meshCollisions++;
                    }
                    if (meshCollisions) measured.collidingFrames++;
                    if (meshOutlined) measured.outlineFrames++;
                    collisions += meshCollisions;
                    outlined += meshOutlined;
                }
                if (collisions) {
                    summary.collidingFrames++;
                    summary.firstCollision ??= u;
                    summary.lastCollision = u;
                }
                if (outlined) summary.outlineFrames++;
                const hat = figure.propByName.get("top_hat");
                if (hat.visible) {
                    summary.highestHat = Math.max(summary.highestHat, new THREE.Box3().setFromObject(hat, true).max.y);
                }
                if (hat.visible && clip.name === "hat_tip") {
                    const lifted = partOf(u, [0.22, 0.32]) * (1 - partOf(u, [0.74, 0.84]));
                    const actual = contact.clone().applyMatrix4(hat.matrix).applyMatrix4(inverse);
                    const expected = contact.clone().add(new THREE.Vector3(0, BUTLER.hat.base + REACTING.hatLift * lifted, 0));
                    summary.maximumLift = Math.max(summary.maximumLift, actual.y - contact.y - BUTLER.hat.base);
                    const error = actual.distanceTo(expected);
                    if (!transition && error > summary.maximumTargetError) {
                        summary.maximumTargetError = error;
                        summary.targetWorst = {u, error, actual: actual.toArray(), expected: expected.toArray()};
                    }
                }
                checks.poses++;
                summary.testedFrames++;
                summary.complete = sample === frameCount;
                if (failFast && outlined) break;
            }
            checks.results.push(summary);
            console.log(JSON.stringify(summary));
        }
        let png = null;
        if (render) {
            stage.drawBody = body; stage.drawScreen = screen;
            const size = 160, rowHeight = size + 24, times = [0.1, 0.18, 0.3, 0.5, 0.78, 0.92];
            const sheet = document.createElement("canvas"); sheet.width = (times.length + 1) * size; sheet.height = 4 * rowHeight;
            const paint = sheet.getContext("2d"); paint.fillStyle = "#15161a"; paint.fillRect(0, 0, sheet.width, sheet.height);
            const canvas = document.createElement("canvas"); canvas.width = canvas.height = size;
            for (const [postureIndex, posture] of clip.postures.entries()) {
                const worst = checks.results.find((each) => each.posture === posture)?.worst?.u ?? 0.5;
                for (const [view, facing] of [0, 90].entries()) {
                    const row = postureIndex * 2 + view;
                    for (const [column, u] of [...times, worst].entries()) {
                        stage.draw(figure, clip, u * (clip.frames - 1), facing, canvas, {posture});
                        paint.drawImage(canvas, column * size, row * rowHeight);
                        paint.font = "11px sans-serif"; paint.fillStyle = "#c0c3d5";
                        paint.fillText(`${posture} ${facing}° · ${u.toFixed(3)}`, column * size + 8, row * rowHeight + size + 15);
                    }
                }
            }
            png = sheet.toDataURL("image/png");
        }
        return {checks, png};
    }, {samples: Number(process.env.HAT_EAR_SAMPLES ?? 360), render: process.env.HAT_EAR_RENDER !== "0" && variants.length === 1 && !process.env.HAT_EAR_TRANSITIONS, variants, postures: process.env.HAT_EAR_POSTURES?.split(","), failFast: Boolean(process.env.HAT_EAR_FAIL_FAST), transitions: Boolean(process.env.HAT_EAR_TRANSITIONS), yaws: (process.env.HAT_EAR_YAWS ?? "0").split(",").map(Number), approaches: Boolean(process.env.HAT_EAR_APPROACHES), clipName: process.env.HAT_EAR_CLIP ?? "hat_tip"});
    mkdirSync(out, {recursive: true});
    writeFileSync(resolve(out, "checks.json"), `${JSON.stringify(result.checks, null, 2)}\n`);
    if (result.png) writeFileSync(resolve(out, "hat_ear.png"), Buffer.from(result.png.split(",")[1], "base64"));
    console.log(JSON.stringify({out, poses: result.checks.poses, results: result.checks.results}));
    if (!process.env.HAT_EAR_REPORT_ONLY && result.checks.results.some((each) => each.collidingFrames || each.outlineFrames)) throw new Error("The glove or forearm crosses the ear envelope or its outline reserve");
} finally {
    await browser.close();
    await server.close();
}
