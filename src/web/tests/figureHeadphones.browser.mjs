// Actual model checks for the loose headset and its two-hand music gesture.
import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = resolve(process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url)));
const out = resolve(process.argv[2] ?? "tests/strips/headphones");
const sources = ["src/figure/homie.js", "src/figure/headphoneClearance.js", "src/figure/figure.js"];
const snapshots = new Map(sources.map((name) => [resolve(root, name), readFileSync(name.endsWith("headphoneClearance.js") && process.env.HEADPHONE_CLEARANCE_SOURCE || name.endsWith("homie.js") && process.env.HEADPHONE_HOMIE_SOURCE || resolve(root, name), "utf8")]));
const sourceHashes = Object.fromEntries([...snapshots].map(([name, source]) => [name.slice(root.length + 1), createHash("sha256").update(source).digest("hex")]));
const options = {samples: Number(process.env.HEADPHONE_SAMPLES ?? 120), times: process.env.HEADPHONE_TIMES?.split(",").map(Number), render: process.env.HEADPHONE_RENDER !== "0", clips: (process.env.HEADPHONE_CLIPS ?? "idle,tantrum,groove,look_left,look_right,yawn,wave,shaka,fire,walk,run").split(","), postures: process.env.HEADPHONE_POSTURES?.split(","), outlines: process.env.HEADPHONE_OUTLINES !== "0", band: process.env.HEADPHONE_BAND !== "0"};
const server = await createServer({root, configFile: false, logLevel: "silent", plugins: [{name: "headphone-fit-snapshot", enforce: "pre", load: (id) => snapshots.get(id) ?? null}], server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => { if (message.type() === "log") console.log(message.text()); });
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async (options) => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {ConvexHull} = await import("/node_modules/three/examples/jsm/math/ConvexHull.js");
        const {figureOf, CLIPS, Stage, drawnPose} = await import("/src/figure/figure.js");
        const {headphoneContacts, headphoneGrip, headphonesAt} = await import("/src/figure/homie.js");
        const index = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch(`/voices/figures/${index.homie}`)).arrayBuffer(), "homie", "/voices/figures/draco/");
        const stage = new Stage(), drawBody = stage.drawBody.bind(stage), drawScreen = stage.drawScreen.bind(stage);
        stage.drawBody = stage.drawScreen = () => {};
        stage.camera.updateMatrixWorld(true);
        const projection = stage.camera.projectionMatrix.clone().multiply(stage.camera.matrixWorldInverse);
        const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
        const all = [];
        figure.scene.traverse((node) => { if (node.isSkinnedMesh && node.name) all.push(node); });
        const skeletons = new Set(all.map((node) => node.skeleton));
        const obstacles = all.filter((node) => node.name === "head_shell" || node.name.startsWith("ear_") || node.name.startsWith("homie_backwards_cap__") || ["homie_hoodie__body", "homie_hoodie__folded_hood", "homie_hoodie__sleeve_l", "homie_hoodie__sleeve_r"].includes(node.name));
        const planeHull = (points) => {
            const hull = new ConvexHull().setFromPoints(points);
            const planes = [...new Map(hull.faces.map(({normal, constant}) => [[...normal.toArray(), constant].map((value) => value.toFixed(6)).join(","), {normal, constant}])).values()];
            return {planes, box: new THREE.Box3().setFromPoints(points)};
        };
        const trianglesIn = (mesh, skinned = false, outlined = options.outlines) => {
            const position = mesh.geometry.attributes.position;
            const outline = mesh.userData.hull ?? mesh.children.find((node) => node.material?.uniforms?.push);
            const push = outlined ? outline?.material.uniforms.push.value ?? 0 : 0;
            const points = Array.from({length: position.count}, (_, i) => {
                const point = new THREE.Vector3().fromBufferAttribute(position, i);
                if (push) point.addScaledVector(new THREE.Vector3().fromBufferAttribute(mesh.geometry.attributes.hullNormal, i), push);
                if (skinned) mesh.applyBoneTransform(i, point);
                return point.applyMatrix4(mesh.matrixWorld);
            });
            const indices = mesh.geometry.index?.array ?? Array.from({length: position.count}, (_, i) => i);
            const triangles = [];
            for (let i = 0; i < indices.length; i += 3) triangles.push([points[indices[i]], points[indices[i + 1]], points[indices[i + 2]]]);
            return {triangles, box: new THREE.Box3().setFromPoints(points), points};
        };
        const clipped = (triangle, planes) => {
            let polygon = triangle;
            for (const {normal, constant} of planes) {
                const distances = polygon.map((point) => normal.dot(point) - constant);
                if (distances.every((distance) => distance > -1e-6)) return false;
                if (distances.every((distance) => distance <= 0)) continue;
                const next = [];
                for (let i = 0; i < polygon.length; i++) {
                    const a = polygon[i], b = polygon[(i + 1) % polygon.length], da = distances[i], db = distances[(i + 1) % polygon.length];
                    if (da <= 0) next.push(a);
                    if ((da <= 0) !== (db <= 0)) next.push(a.clone().lerp(b, da / (da - db)));
                }
                polygon = next;
                if (polygon.length < 3) return false;
            }
            return polygon.slice(2).some((point, i) => polygon[i + 1].clone().sub(polygon[0]).cross(point.clone().sub(polygon[0])).lengthSq() > 1e-14) && polygon.reduce((sum, point) => sum.add(point), new THREE.Vector3()).divideScalar(polygon.length);
        };
        const clips = options.clips.includes("all") ? CLIPS.filter((clip) => !clip.voices || clip.voices.includes("homie")) : CLIPS.filter((clip) => options.clips.includes(clip.name));
        const report = {voice: "homie", outlinedGeometry: options.outlines, includesBand: options.band, samples: 0, collisions: 0, outlineOnlyNeckOcclusions: 0, gripSamples: 0, maximumGripError: 0, maximumSurfaceContactError: 0, maximumCupScaleError: 0, maximumFreeCupShift: 0, largestFreeCupShift: null, maximumBandNodes: 0, maximumBandShift: 0, largestBandShift: null, maximumUnresolvedBandSegments: 0, poseMilliseconds: 0, maximumPoseMilliseconds: 0, minimumCameraMargin: Infinity, results: [], errors: [], removedLegacyParts: all.every((mesh) => !mesh.name.startsWith("homie_headphones__"))};
        for (const clip of clips) for (const posture of clip.postures) {
            if (options.postures && !options.postures.includes(posture)) continue;
            const entry = {clip: clip.name, posture, samples: 0, collisions: 0, outlineOnlyNeckOcclusions: 0, contacts: [], neckOcclusions: []};
            for (const u of options.times ?? Array.from({length: options.samples + 1}, (_, sample) => sample / options.samples)) {
                const began = performance.now();
                const moves = stage.draw(figure, clip, u * (clip.frames - 1), 0, null, {posture});
                const elapsed = performance.now() - began;
                report.poseMilliseconds += elapsed; report.maximumPoseMilliseconds = Math.max(report.maximumPoseMilliseconds, elapsed);
                report.maximumBandNodes = Math.max(report.maximumBandNodes, figure.headphones.previous.band.length);
                const bandShift = figure.headphones.previous.maximumBandShift ?? 0;
                if (bandShift > report.maximumBandShift) { report.maximumBandShift = bandShift; report.largestBandShift = {clip: clip.name, posture, u}; }
                report.maximumUnresolvedBandSegments = Math.max(report.maximumUnresolvedBandSegments, figure.headphones.previous.unresolved ?? 0);
                const authored = headphonesAt(clip.name === "groove" ? u : null, moves);
                for (let index = 0; index < 2; index++) {
                    const shift = figure.headphones.cups[index].position.distanceTo(authored.cups[index].at);
                    if (shift > report.maximumFreeCupShift) {
                        report.maximumFreeCupShift = shift;
                        report.largestFreeCupShift = {clip: clip.name, posture, u, side: index ? "r" : "l"};
                    }
                }
                figure.scene.updateMatrixWorld(true);
                for (const skeleton of skeletons) skeleton.update();
                const parts = [];
                figure.headphones.root.traverse((mesh) => {
                    if (!mesh.geometry || !mesh.name || !options.band && mesh === figure.headphones.band) return;
                    const part = {name: mesh.name, mesh, ...trianglesIn(mesh)};
                    // Cups are convex. The flexible tube is a chain of convex ring pairs, so bent sleeves keep their actual concave shape.
                    part.volumes = mesh === figure.headphones.band ? Array.from({length: mesh.geometry.parameters.tubularSegments}, (_, i) => planeHull(part.points.slice(i * 9, (i + 2) * 9))) : [planeHull(part.points)];
                    parts.push(part);
                });
                const headphoneBox = new THREE.Box3();
                for (const part of parts) headphoneBox.union(part.box);
                if (["idle", "groove", "tantrum"].includes(clip.name)) for (const part of parts) for (const point of part.points) {
                    const pixel = point.clone().applyMatrix4(projection);
                    report.minimumCameraMargin = Math.min(report.minimumCameraMargin, (1 - Math.abs(pixel.x)) / 2, (1 - Math.abs(pixel.y)) / 2);
                }
                for (const cup of figure.headphones.cups) report.maximumCupScaleError = Math.max(report.maximumCupScaleError, ...cup.scale.toArray().map((value) => Math.abs(value - 1)));
                if (clip.name === "groove" && headphoneGrip(u) > 1 - 1e-9) {
                    const {pose} = drawnPose(figure.rig, figure.stance, clip, u * (clip.frames - 1), 0, {posture});
                    const contacts = headphoneContacts(headphonesAt(u, moves));
                    for (const [index, side] of ["l", "r"].entries()) {
                        const fingers = pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`)).applyMatrix4(toGlb);
                        report.maximumGripError = Math.max(report.maximumGripError, fingers.distanceTo(contacts[index].at));
                        const cup = figure.headphones.cups[index].getObjectByName(`homie_headphones_${side}_cup`);
                        const surface = trianglesIn(cup, false, false), nearest = new THREE.Vector3();
                        report.maximumSurfaceContactError = Math.max(report.maximumSurfaceContactError, Math.min(...surface.triangles.map((triangle) => new THREE.Triangle(...triangle).closestPointToPoint(fingers, nearest).distanceTo(fingers))));
                        report.gripSamples++;
                    }
                }
                for (const obstacle of obstacles) {
                    const {triangles, box} = trianglesIn(obstacle, true);
                    if (!box.intersectsBox(headphoneBox)) continue;
                    const candidates = parts.filter((part) => box.intersectsBox(part.box));
                    if (!candidates.length) continue;
                    const triangleBox = new THREE.Box3();
                    for (const part of candidates) {
                        const volumes = part.volumes.filter((volume) => volume.box.intersectsBox(box));
                        let contact;
                        const collision = triangles.some((triangle) => {
                            triangleBox.setFromPoints(triangle);
                            return volumes.some((volume) => triangleBox.intersectsBox(volume.box) && (contact = clipped(triangle, volume.planes)));
                        });
                        if (collision) {
                            // Existing head/hoodie outline shells overlap at this narrow neckline. A thin band may be occluded there,
                            // but its actual surface must still clear both bodies. Shoulder/sleeve and cup tests retain full outlines.
                            if (options.outlines && part.mesh === figure.headphones.band && ["head_shell", "homie_hoodie__body", "homie_hoodie__folded_hood"].includes(obstacle.name)) {
                                const actual = trianglesIn(part.mesh, false, false);
                                const actualVolumes = Array.from({length: part.mesh.geometry.parameters.tubularSegments}, (_, i) => planeHull(actual.points.slice(i * 9, (i + 2) * 9)));
                                const body = trianglesIn(obstacle, true, false);
                                const actualCollision = body.triangles.some((triangle) => {
                                    triangleBox.setFromPoints(triangle);
                                    return actualVolumes.some((volume) => triangleBox.intersectsBox(volume.box) && clipped(triangle, volume.planes));
                                });
                                if (!actualCollision) {
                                    entry.outlineOnlyNeckOcclusions++; report.outlineOnlyNeckOcclusions++;
                                    if (entry.neckOcclusions.length < 12) entry.neckOcclusions.push({u, body: obstacle.name, at: contact.toArray()});
                                    continue;
                                }
                            }
                            entry.collisions++; report.collisions++;
                            if (entry.contacts.length < 30) entry.contacts.push({u, accessory: part.name, body: obstacle.name, at: contact.toArray()});
                        }
                    }
                }
                entry.samples++; report.samples++;
            }
            report.results.push(entry);
            console.log(JSON.stringify(entry));
        }
        let png = null;
        if (options.render) {
            stage.drawBody = drawBody; stage.drawScreen = drawScreen;
            const size = 224, label = 24;
            const times = [0, 0.1, 0.17, 0.24, 0.34, 0.48, 0.74, 1];
            const canvas = Object.assign(document.createElement("canvas"), {width: size, height: size});
            const sheet = Object.assign(document.createElement("canvas"), {width: size * times.length, height: (size + label) * 2});
            const paint = sheet.getContext("2d"); paint.fillStyle = "#252832"; paint.fillRect(0, 0, sheet.width, sheet.height);
            const clip = CLIPS.find((each) => each.name === "groove");
            for (const [row, facing] of [0, 90].entries()) for (const [column, u] of times.entries()) {
                stage.draw(figure, clip, u * (clip.frames - 1), facing, canvas, {posture: "stand"});
                paint.drawImage(canvas, column * size, row * (size + label));
                paint.font = "12px sans-serif"; paint.fillStyle = "#e0e4ee";
                paint.fillText(`${facing}° · ${u.toFixed(2)}`, column * size + 8, row * (size + label) + size + 17);
            }
            png = sheet.toDataURL("image/png");
        }
        report.passes = !report.collisions && report.removedLegacyParts && report.maximumGripError < 2e-5 && report.maximumSurfaceContactError < 2e-5 && report.maximumCupScaleError < 1e-9 && report.minimumCameraMargin > 0.01;
        return {report, png};
    }, options);
    mkdirSync(out, {recursive: true});
    writeFileSync(resolve(out, "checks.json"), JSON.stringify({...result.report, sourceHashes, browserErrors: errors}, null, 2) + "\n");
    if (result.png) writeFileSync(resolve(out, "jam-strip.png"), Buffer.from(result.png.split(",")[1], "base64"));
    if ((!result.report.passes || errors.length) && !process.env.HEADPHONE_REPORT_ONLY) throw new Error("Headphone clearance check failed");
} finally {
    await browser.close();
    await server.close();
}
