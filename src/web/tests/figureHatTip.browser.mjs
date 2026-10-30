// The actual Butler head must fit inside the lifted crown throughout the tip. Clip triangles at the brim plane as well as checking
// vertices, so a triangle crossing that plane cannot hide an intersection between sampled vertices.
import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {chromium} from "playwright-core";
import {createServer} from "vite";

const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const out = resolve(process.argv[2] ?? "tests/strips/hat-tip");
const server = await createServer({root, configFile: false, logLevel: "silent", server: {host: "127.0.0.1", port: 0}});
await server.listen();
const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}), args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]});
try {
    const page = await browser.newPage();
    await page.goto(new URL("voices/figures/figures.json", server.resolvedUrls.local[0]).href);
    const result = await page.evaluate(async () => {
        const THREE = await import("/node_modules/three/build/three.module.js");
        const {CLIPS, Stage, figureOf, drawnPose, moveProps, REACTING} = await import("/src/figure/figure.js");
        const {BUTLER, topHatGeometry} = await import("/src/figure/butler.js");
        const {FRAMED} = await import("/src/figure/frame.js");
        const files = await (await fetch("/voices/figures/figures.json")).json();
        const figure = await figureOf(await (await fetch(`/voices/figures/${files.butler}`)).arrayBuffer(), "butler", "/voices/figures/draco/");
        const stage = new Stage();
        const clip = CLIPS.find((each) => each.name === "hat_tip");
        const shell = figure.scene.getObjectByName("head_shell");
        const head = Array.from({length: shell.geometry.attributes.position.count}, (_, i) => {
            const point = new THREE.Vector3().fromBufferAttribute(shell.geometry.attributes.position, i).applyMatrix4(shell.matrixWorld);
            return new THREE.Vector3(point.x, -point.z, point.y);
        });
        const indices = shell.geometry.index.array;
        const edges = new Set();
        for (let i = 0; i < indices.length; i += 3) {
            for (const [a, b] of [[indices[i], indices[i + 1]], [indices[i + 1], indices[i + 2]], [indices[i + 2], indices[i]]]) edges.add(`${Math.min(a, b)},${Math.max(a, b)}`);
        }
        const pairs = [...edges].map((edge) => edge.split(",").map(Number));
        const checks = {poses: 0, tiltedPoses: 0, minimumCrownClearance: Infinity, maximumGripError: 0, maximumMeshContactError: 0, highestPoint: -Infinity, handoffError: 0, outline: 0.036};
        const heldHat = figure.propByName.get("top_hat");
        const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
        const angle = THREE.MathUtils.degToRad(REACTING.hatGripAngle);
        const radius = BUTLER.hat.crown + BUTLER.hat.brim;
        const contactAt = new THREE.Vector3(-radius * Math.cos(angle), BUTLER.hat.curl * Math.cos(angle) ** 2 + BUTLER.hat.thick / 2, radius * Math.sin(angle));
        const brimGeometry = topHatGeometry();
        const brimPosition = brimGeometry.attributes.position;
        const brimIndex = brimGeometry.index.array;
        const brimTriangles = [];
        for (let i = 0; i < brimIndex.length; i += 3) {
            brimTriangles.push(new THREE.Triangle(...[0, 1, 2].map((j) => new THREE.Vector3().fromBufferAttribute(brimPosition, brimIndex[i + j]))));
        }
        const nearest = new THREE.Vector3();
        for (const posture of clip.postures) {
            for (let step = 0; step <= 720; step++) {
                const frame = step / 720 * (clip.frames - 1);
                const {pose, turned} = drawnPose(figure.rig, figure.stance, clip, frame, 0, {posture});
                const moves = pose.moves(turned);
                moveProps(figure, pose, moves);
                checks.poses++;
                const held = pose.props.get("top_hat");
                if (!held) continue;
                heldHat.updateMatrixWorld(true);
                const bounds = new THREE.Box3().setFromObject(heldHat, true);
                checks.highestPoint = Math.max(checks.highestPoint, bounds.max.y);
                const contact = contactAt.clone().applyMatrix4(heldHat.matrixWorld);
                const fingers = pose.grip("r", [REACTING.hatFingers, 0, 0]).applyMatrix4(moves.get("hand_r")).applyMatrix4(toGlb);
                checks.maximumGripError = Math.max(checks.maximumGripError, contact.distanceTo(fingers));
                const localFingers = fingers.clone().applyMatrix4(heldHat.matrixWorld.clone().invert());
                const meshDistance = Math.min(...brimTriangles.map((triangle) => triangle.closestPointToPoint(localFingers, nearest).distanceTo(localFingers)));
                checks.maximumMeshContactError = Math.max(checks.maximumMeshContactError, meshDistance);
                if (Math.hypot(held.turn.x ?? 0, held.turn.y ?? 0, held.turn.z ?? 0) < 1e-6) continue;
                checks.tiltedPoses++;
                const inverse = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(...[held.turn.x ?? 0, held.turn.y ?? 0, held.turn.z ?? 0].map(THREE.MathUtils.degToRad), "ZYX")).invert();
                const points = head.map((point) => point.clone().sub(held.at).applyMatrix4(inverse));
                const above = points.filter((point) => point.z >= 0);
                for (const [a, b] of pairs) {
                    const from = points[a], to = points[b];
                    if ((from.z < 0) === (to.z < 0)) continue;
                    above.push(from.clone().lerp(to, -from.z / (to.z - from.z)));
                }
                for (const point of above) {
                    checks.minimumCrownClearance = Math.min(checks.minimumCrownClearance, BUTLER.hat.crown - Math.hypot(point.x, point.y), BUTLER.hat.height - point.z);
                }
            }
        }
        for (const u of [0.22 + 1e-8, 0.84 - 1e-8]) {
            const {pose} = drawnPose(figure.rig, figure.stance, clip, u * (clip.frames - 1), 0);
            const held = pose.props.get("top_hat");
            if (held) checks.handoffError = Math.max(checks.handoffError, held.at.distanceTo(new THREE.Vector3(0, 0, BUTLER.hat.base)));
        }
        const opening = new THREE.Mesh(topHatGeometry(), new THREE.MeshBasicMaterial({side: THREE.DoubleSide}));
        const ray = new THREE.Raycaster(new THREE.Vector3(0.1, -0.2, 0.1), new THREE.Vector3(0, 1, 0));
        checks.openUnderside = ray.intersectObject(opening)[0]?.distance > BUTLER.hat.height;
        checks.matchingColour = heldHat.getObjectByName("top_hat_crown").material.uniforms.colour.value.distanceTo(figure.scene.getObjectByName("butler_top_hat").material.uniforms.colour.value) < 1e-9;
        checks.cameraCeiling = FRAMED.middle + FRAMED.height / 2 - 0.07;
        const times = [0, 0.15, 0.25, 0.4, 0.5, 0.67, 0.82, 1];
        const views = [{posture: "stand", facing: 0}, {posture: "stand", facing: 90}, {posture: "sit", facing: 0}];
        const size = 160, rowHeight = size + 24;
        const sheet = document.createElement("canvas");
        sheet.width = times.length * size; sheet.height = views.length * rowHeight;
        const paint = sheet.getContext("2d");
        paint.fillStyle = "#15161a"; paint.fillRect(0, 0, sheet.width, sheet.height);
        for (const [row, options] of views.entries()) {
            for (const [column, u] of times.entries()) {
                const cell = document.createElement("canvas"); cell.width = cell.height = size;
                stage.draw(figure, clip, u * (clip.frames - 1), options.facing, cell, options);
                paint.drawImage(cell, column * size, row * rowHeight);
                paint.font = "11px sans-serif"; paint.fillStyle = "#c0c3d5";
                paint.fillText(`${options.posture} ${options.facing}° · ${u.toFixed(2)}`, column * size + 10, row * rowHeight + size + 15);
            }
        }
        return {checks, png: sheet.toDataURL("image/png")};
    });
    mkdirSync(out, {recursive: true});
    writeFileSync(`${out}/hat_tip.png`, Buffer.from(result.png.split(",")[1], "base64"));
    writeFileSync(`${out}/checks.json`, JSON.stringify(result.checks, null, 2) + "\n");
    const checks = result.checks;
    if (!checks.openUnderside || !checks.matchingColour || checks.minimumCrownClearance < checks.outline || checks.maximumGripError > 1e-6 || checks.maximumMeshContactError > 1e-6 || checks.handoffError > 1e-5 || checks.highestPoint >= checks.cameraCeiling) throw new Error(JSON.stringify(checks));
    console.log(JSON.stringify({out, ...checks}));
} finally {
    await browser.close();
    await server.close();
}
