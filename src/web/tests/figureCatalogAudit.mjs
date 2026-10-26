import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";
import * as THREE from "three";

// A diagnostic sweep of the whole catalog. Tiny samples on either side of authored timing boundaries expose instantaneous pose
// changes; loop joins and non-finite matrices are reported separately. Findings still need review because some acts deliberately cut.
const root = process.env.FIGURE_ROOT ?? fileURLToPath(new URL("..", import.meta.url));
const {CLIPS, drawnPose} = await import(pathToFileURL(resolve(root, "src/figure/figure.js")));
const {ACTS} = await import(pathToFileURL(resolve(root, "src/figure/acts.js")));
const {rig, stances} = JSON.parse(readFileSync(resolve(root, "tests/figureRig.json")));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const numbers = (value) => typeof value === "number" ? [value] : value && typeof value === "object" ? Object.values(value).flatMap(numbers) : [];
const epsilon = 1e-6;
const report = {clips: CLIPS.length, combinations: 0, poses: 0, nonfinite: [], boundaries: [], loops: []};

function sample(clip, stance, posture, frame) {
    const {pose, turned} = drawnPose(RIG, stance, clip, frame, 0, {posture});
    const moves = pose.moves(turned);
    report.poses++;
    return moves;
}

function difference(a, b) {
    let distance = 0;
    let angle = 0;
    let bone = "";
    for (const name of RIG.order) {
        const first = a.get(name), last = b.get(name);
        const at = RIG.heads.get(name).clone().applyMatrix4(first);
        const to = RIG.heads.get(name).clone().applyMatrix4(last);
        const moved = at.distanceTo(to);
        if (moved > distance) { distance = moved; bone = name; }
        const q1 = new THREE.Quaternion(), q2 = new THREE.Quaternion();
        first.decompose(new THREE.Vector3(), q1, new THREE.Vector3());
        last.decompose(new THREE.Vector3(), q2, new THREE.Vector3());
        angle = Math.max(angle, THREE.MathUtils.radToDeg(q1.angleTo(q2)));
    }
    return {distance, angle, bone};
}

for (const clip of CLIPS) {
    for (const voice of clip.voices ?? Object.keys(stances)) {
        const stance = stanceOf(voice);
        for (const posture of clip.postures) {
            report.combinations++;
            const label = {clip: clip.name, voice, posture};
            // Every authored frame, in every supported voice and posture, must yield finite body matrices.
            for (let frame = 0; frame <= clip.frames; frame++) {
                const moves = sample(clip, stance, posture, frame);
                for (const [bone, matrix] of moves) if (!matrix.elements.every(Number.isFinite)) report.nonfinite.push({...label, frame, bone});
            }
            // The first voice checks all percentage and authored boundaries; other voices repeat those same pose joins through their
            // own stance whenever the clip has fewer combinations, keeping the diagnostic inexpensive enough to rerun.
            if (voice === (clip.voices?.[0] ?? Object.keys(stances)[0])) {
                const times = new Set([...Array.from({length: 99}, (_, i) => (i + 1) / 100), ...numbers(ACTS[clip.name]).filter((value) => value > 0 && value < 1)]);
                for (const frame of [clip.intro, clip.frames - (clip.outro ?? 0)]) if (frame > 0 && frame < clip.frames) times.add(frame / clip.frames);
                for (const u of times) {
                    const diff = difference(sample(clip, stance, posture, (u - epsilon) * clip.frames), sample(clip, stance, posture, (u + epsilon) * clip.frames));
                    if (diff.distance > 0.01 || diff.angle > 0.5) report.boundaries.push({...label, u, ...diff});
                }
            }
            if (clip.loops) {
                const diff = difference(sample(clip, stance, posture, (clip.intro ?? 0) + epsilon), sample(clip, stance, posture, clip.frames - (clip.outro ?? 0) - epsilon));
                if (diff.distance > 0.02 || diff.angle > 1) report.loops.push({...label, ...diff});
            }
        }
    }
}
const out = resolve(process.argv[2] ?? "out/catalog-audit.json");
mkdirSync(dirname(out), {recursive: true});
writeFileSync(out, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({path: out, clips: report.clips, combinations: report.combinations, poses: report.poses, nonfinite: report.nonfinite.length, boundaries: report.boundaries.length, loops: report.loops.length}));
