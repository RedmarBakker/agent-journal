import {readFileSync} from "node:fs";
import * as THREE from "three";
import {CLIPS, drawnPose, figureOf, moveProps, telephoneOf} from "../../src/figure/figure.js";
import {decodedFigure} from "./figureModel.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("../figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
export const phoneRig = {...rig, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
export const phoneClip = CLIPS.find((clip) => clip.name === "phone_call");
export const phoneVoices = Object.keys(stances);
const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
const fromGlb = toGlb.clone().invert();
const arrayPoint = (data, index) => new THREE.Vector3().fromArray(data, index * 3);
const armBone = (name) => /^(upper_arm|forearm|hand|wrist)(_|$)/.test(name);
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

export function phoneProps() {
    const groups = ["telephone", "telephone_handset", "telephone_cord", "telephone_poof"].map((name) => Object.assign(new THREE.Group(), {name, matrixAutoUpdate: false}));
    telephoneOf(...groups);
    return {propByName: new Map(groups.map((group) => [group.name, group]))};
}

export function phonePose(u, voice, options, figure = phoneProps()) {
    const {pose, turned} = drawnPose(phoneRig, stanceOf(voice), phoneClip, u * (phoneClip.frames - 1), options.facing ?? 0, options);
    const moves = pose.moves(turned);
    moveProps(figure, pose, moves);
    for (const group of figure.propByName.values()) group.updateMatrixWorld(true);
    return {pose, moves, figure};
}

// Arms and shoulder clothing use the dressed model's actual skin weights. Carried props are put away by the call itself.
export async function phoneArmMeshes(voice) {
    const figure = await figureOf((await decodedFigure(voice)).buffer, voice, "");
    const {pose} = drawnPose(phoneRig, stanceOf(voice), phoneClip, 0.36 * (phoneClip.frames - 1), 0, {posture: "stand"});
    const meshes = [];
    figure.scene.traverse((mesh) => {
        // Outline children have no name and share the solid parent's geometry; their shader shell is not a second solid.
        if (!mesh.isSkinnedMesh || !mesh.name || pose.stowed.has(mesh.userData.item)) return;
        for (let node = mesh; node; node = node.parent) if (!node.visible) return;
        const tracked = new Set(mesh.skeleton.bones.flatMap((bone, index) => armBone(bone.name) ? [index] : []));
        const skin = mesh.geometry.attributes.skinIndex.array, weights = mesh.geometry.attributes.skinWeight.array;
        const weighted = skin.some((joint, index) => tracked.has(joint) && weights[index] > 0);
        const limb = /(?:hand_shell|wrist_joint|elbow_joint|shoulder_joint|upper_arm_shell|forearm_shell|__cuff|__sleeve|__shoulder_stripe|_gauntlet|_bracer|_pauldron)/.test(mesh.name) && /_[lr](?:_\d+)?$/.test(mesh.name);
        if (weighted || limb) meshes.push(mesh);
    });
    const arms = meshes.map((mesh) => {
        const joints = mesh.skeleton.bones.map((bone) => bone.name);
        const positions = mesh.geometry.attributes.position.array;
        const indices = mesh.geometry.index?.array ?? Array.from({length: positions.length / 3}, (_, index) => index);
        const weights = mesh.geometry.attributes.skinWeight.array;
        const skin = mesh.geometry.attributes.skinIndex.array;
        const points = [], influence = [], remap = [], unique = new Map();
        for (let index = 0; index < positions.length / 3; index++) {
            const key = [...positions.slice(index * 3, index * 3 + 3), ...skin.slice(index * 4, index * 4 + 4), ...weights.slice(index * 4, index * 4 + 4)].join(",");
            if (!unique.has(key)) {
                unique.set(key, points.length);
                points.push(arrayPoint(positions, index));
                influence.push(Array.from({length: 4}, (_, offset) => ({bone: joints[skin[index * 4 + offset]], weight: weights[index * 4 + offset]})).filter(({weight}) => weight > 0));
            }
            remap[index] = unique.get(key);
        }
        const triangles = [];
        for (let index = 0; index < indices.length; index += 3) triangles.push([remap[indices[index]], remap[indices[index + 1]], remap[indices[index + 2]]]);
        const edges = new Map();
        for (const triangle of triangles) for (let corner = 0; corner < 3; corner++) {
            const a = triangle[corner], b = triangle[(corner + 1) % 3];
            if (a === b) continue;
            const edge = a < b ? `${a}:${b}` : `${b}:${a}`;
            edges.set(edge, (edges.get(edge) ?? 0) + 1);
        }
        const closed = [...edges.values()].every((count) => count === 2);
        const links = points.map((_, index) => index);
        const connected = (index) => links[index] === index ? index : links[index] = connected(links[index]);
        for (const [a, b, c] of triangles) {
            links[connected(b)] = connected(a);
            links[connected(c)] = connected(a);
        }
        const components = [...new Set(points.map((_, index) => connected(index)))];
        return {name: mesh.name, points, influence, triangles, components, closed, mesh, remap};
    });
    arms.figure = figure;
    return arms;
}

export function posedArm(mesh, moves) {
    const transforms = new Map([...moves].map(([name, matrix]) => [name, toGlb.clone().multiply(matrix).multiply(fromGlb)]));
    return mesh.points.map((point, index) => {
        const result = new THREE.Vector3();
        for (const {bone, weight} of mesh.influence[index]) result.addScaledVector(point.clone().applyMatrix4(transforms.get(bone)), weight);
        return result;
    });
}

export function armSurfaceDistance(arm, moves, point) {
    const points = posedArm(arm, moves), triangle = new THREE.Triangle(), nearest = new THREE.Vector3();
    let distance = Infinity;
    for (const [a, b, c] of arm.triangles) {
        triangle.set(points[a], points[b], points[c]).closestPointToPoint(point, nearest);
        distance = Math.min(distance, nearest.distanceTo(point));
    }
    return distance;
}

export function nearestPropPoint(mesh, point) {
    const own = point.clone().applyMatrix4(mesh.matrixWorld.clone().invert());
    const triangle = new THREE.Triangle(), nearest = new THREE.Vector3(), result = new THREE.Vector3();
    let distance = Infinity;
    for (const {points} of trianglesOf(mesh.geometry)) {
        triangle.set(...points).closestPointToPoint(own, nearest);
        const squared = nearest.distanceToSquared(own);
        if (squared < distance) {
            distance = squared;
            result.copy(nearest);
        }
    }
    return result.applyMatrix4(mesh.matrixWorld);
}

const boxFor = (points) => new THREE.Box3().setFromPoints(points);
const boundsFor = (entries) => entries.reduce((box, entry) => box.union(entry.box), new THREE.Box3());

function treeOf(triangles, depth = 0) {
    const box = boundsFor(triangles);
    if (triangles.length <= 12) return {box, triangles};
    const size = box.getSize(new THREE.Vector3());
    const axis = size.x >= size.y && size.x >= size.z ? "x" : size.y >= size.z ? "y" : "z";
    const sorted = [...triangles].sort((a, b) => a.box.min[axis] + a.box.max[axis] - b.box.min[axis] - b.box.max[axis]);
    const middle = Math.floor(sorted.length / 2);
    return {box, left: treeOf(sorted.slice(0, middle), depth + 1), right: treeOf(sorted.slice(middle), depth + 1)};
}

function trianglesOf(geometry) {
    const positions = geometry.attributes.position;
    const indices = geometry.index?.array ?? Array.from({length: positions.count}, (_, index) => index);
    const triangles = [];
    for (let index = 0; index < indices.length; index += 3) {
        const points = Array.from({length: 3}, (_, corner) => new THREE.Vector3().fromBufferAttribute(positions, indices[index + corner]));
        if (new THREE.Triangle(...points).getArea() > 1e-10) triangles.push({points, box: boxFor(points)});
    }
    return triangles;
}

const geometryTrees = new WeakMap();

function geometryTree(geometry) {
    if (!geometryTrees.has(geometry)) geometryTrees.set(geometry, treeOf(trianglesOf(geometry)));
    return geometryTrees.get(geometry);
}

function candidates(node, box, visit) {
    if (!node.box.intersectsBox(box)) return false;
    if (node.triangles) {
        for (const triangle of node.triangles) if (triangle.box.intersectsBox(box) && visit(triangle.points)) return true;
        return false;
    }
    return candidates(node.left, box, visit) || candidates(node.right, box, visit);
}

function crossed(a, b) {
    const ray = new THREE.Ray(), direction = new THREE.Vector3(), hit = new THREE.Vector3();
    for (const [edges, face] of [[a, b], [b, a]]) for (let index = 0; index < 3; index++) {
        direction.subVectors(edges[(index + 1) % 3], edges[index]);
        const length = direction.length();
        if (length < 1e-9) continue;
        ray.set(edges[index], direction.divideScalar(length));
        if (ray.intersectTriangle(...face, false, hit)) {
            const distance = hit.distanceTo(edges[index]);
            if (distance > 1e-7 && distance < length - 1e-7) return hit.clone();
        }
    }
    return null;
}

function containsPoint(tree, point) {
    if (!tree.box.containsPoint(point)) return false;
    const ray = new THREE.Ray(point, new THREE.Vector3(1, Math.SQRT2, Math.sqrt(3)).normalize());
    const hits = [], hit = new THREE.Vector3();
    const visit = (node) => {
        if (!ray.intersectsBox(node.box)) return;
        if (!node.triangles) {
            visit(node.left);
            visit(node.right);
            return;
        }
        for (const {points} of node.triangles) {
            if (ray.intersectTriangle(...points, false, hit)) {
                const distance = point.distanceTo(hit);
                if (distance > 1e-7) hits.push(distance);
            }
        }
    };
    visit(tree);
    const unique = hits.sort((a, b) => a - b).filter((distance, index) => index === 0 || distance - hits[index - 1] > 1e-6);
    return unique.length % 2 === 1;
}

// Exact segment/triangle crossings catch arm triangles passing through a prop even with no enclosed arm vertices.
export function armPropCrossings(arms, moves, figure, {firstOnly = true, props = ["telephone", "telephone_handset", "telephone_cord"]} = {}) {
    const collision = [];
    const posed = arms.map((arm) => {
        const points = posedArm(arm, moves);
        return {...arm, points, box: boxFor(points)};
    });
    for (const propName of props) {
        const group = figure.propByName.get(propName);
        if (!group?.visible) continue;
        const meshes = [];
        group.traverse((mesh) => { if (mesh.isMesh && mesh.name) meshes.push(mesh); });
        for (const mesh of meshes) {
            if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
            const worldBox = mesh.geometry.boundingBox.clone().applyMatrix4(mesh.matrixWorld);
            const near = posed.filter((arm) => worldBox.intersectsBox(arm.box));
            if (!near.length) continue;
            const inverse = mesh.matrixWorld.clone().invert();
            const tree = geometryTree(mesh.geometry);
            for (const arm of near) {
                const points = arm.points.map((point) => point.clone().applyMatrix4(inverse));
                if (!tree.box.intersectsBox(boxFor(points))) continue;
                let crossing = false;
                for (const indices of arm.triangles) {
                    const triangle = indices.map((index) => points[index]);
                    let hit = null;
                    candidates(tree, boxFor(triangle), (other) => Boolean(hit = crossed(triangle, other)));
                    if (hit) {
                        collision.push({arm: arm.name, prop: mesh.name, at: hit.applyMatrix4(mesh.matrixWorld).toArray()});
                        if (firstOnly) return collision;
                        crossing = true;
                        break;
                    }
                }
                if (crossing) continue;
                // A connected surface wholly inside a closed prop has no crossing edges.
                const closed = !["TubeGeometry", "TorusGeometry"].includes(mesh.geometry.type);
                const inside = closed && arm.components.find((index) => containsPoint(tree, points[index]));
                if (inside !== false && inside !== undefined) {
                    collision.push({arm: arm.name, prop: mesh.name, contained: "arm", at: arm.points[inside].toArray()});
                    if (firstOnly) return collision;
                } else if (arm.closed && arm.box.containsBox(worldBox)) {
                    const armTree = arm.tree ??= treeOf(arm.triangles.map((indices) => {
                        const triangle = indices.map((index) => arm.points[index]);
                        return {points: triangle, box: boxFor(triangle)};
                    }));
                    const point = new THREE.Vector3().fromBufferAttribute(mesh.geometry.attributes.position, 0).applyMatrix4(mesh.matrixWorld);
                    if (containsPoint(armTree, point)) {
                        collision.push({arm: arm.name, prop: mesh.name, contained: "prop", at: point.toArray()});
                        if (firstOnly) return collision;
                    }
                }
            }
        }
    }
    return collision;
}
