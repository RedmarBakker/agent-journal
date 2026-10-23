// A rigged figure drawn in the browser as Blender draws it: posed by a port of clips.py and rig.Posing, shaded as
// toon.py shades it, one held pose for each step of a clip.
import * as THREE from "three";
import {ACTS, heldPhases, partOf, pogoBounces, pogoHop, swingAngle} from "./acts.js";
import {VISOR, glowTurn} from "./visor.js";
import {LIGHT_COLOURS, PARCEL, brightness} from "./parcels.js";
import {blendMoves} from "./blend.js";
import {BUTLER, dressButler, topHatBandGeometry, topHatGeometry} from "./butler.js";
import {GLTFLoader} from "three/addons/loaders/GLTFLoader.js";
import {DRACOLoader} from "three/addons/loaders/DRACOLoader.js";

// render_clips.py and snaps.py: an orthographic camera eight units in front, framing 5.4 units about a height of 2.4
export const CELL = 224;
const FRAMED_HEIGHT = 5.4;
const FRAMED_MIDDLE = 2.4;
const DISTANCE = 8;
const DEPTH = 3;
// three's own Draco decoder, for the review page, which has no server of its own
const DECODER = "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/";
// the share of the picture below the ground the figure stands on, where the chat box's top edge runs
export const GROUND = (FRAMED_HEIGHT / 2 - FRAMED_MIDDLE) / FRAMED_HEIGHT;

// EEVEE takes 16 samples a pixel through a 1.5 px filter; the browser draws twice as wide, scales down and softens
// by this share of a cell pixel, which measured closest to Blender's own frames
const SUPERSAMPLE = 2;
const SOFTEN = 0.5;

// toon.py; the step is on N.L, worked out from its ramp: a 0.8 grey Diffuse BSDF under a sun of strength pi and the
// render's 0.05 grey world reads 0.8 N.L + 0.04, which crosses LIT_FROM = 0.52 at N.L = 0.6 (measured on a sphere: 0.600)
const LIGHT_FROM = new THREE.Vector3(-0.35, -0.8, 0.5);
const LIT_FROM = 0.6;
const SHADE = new THREE.Vector3(0.6, 0.6, 0.7);
const OUTLINE_COLOUR = new THREE.Vector3(0.02, 0.02, 0.05);
const OUTLINE_WIDTH = 0.036;

// clips.py and rig.py
export const SIDES = {l: 1, r: -1};
const HANG = 65;
const ARM_CLEAR_RAISE = 25;
const ARM_RAISE_SPAN = 25;
const HOLD_LIFT = -6;
// how far a forearm held level turns in from pointing out to the side, past forward, so it lies across the waist as a waiter's does
const HOLD_SWING = 95;
const HOLD_TWIST = 25;
// how far the hand holding something level turns back from the forearm's line at the wrist, kept as it was before the forearm was laid
// across the waist
const HOLD_WRIST = 30;
const HOLD_ROLL = 20;
const RAISED_ROLL = 85;
const WAVE_BACK = 40;
const WAVE_BEND = 25;
const WAVE_SWING = 10;
const CHIN_REST = [0.4, -0.92, 2.1];
const THINK_ELBOW = [0.6, 0.3, -1.0];
const THINK_HAND = [1.0, -0.4, 0.35];
const THINK_TIP = 25;
const SLEEP_TILT = 4;
const SLEEP_FRAMES = 18;
// what the butler once carried on the platter is left out, so both his hands are empty and hang and swing as each other
const LEFT_OUT = new Set(["butler_tray"]);
// what a figure holds only in the poses that use it, as the butler's tablet while he writes or searches
const TABLET = "butler_tablet";
// the butler's cloth, kept in his pocket and drawn only to polish his visor
const CLOTH = "butler_towel";
// how far the hand holding the tablet tips it up toward the face, and where on it the free hand touches, from that hand toward the free side
const TABLET_TIP = 65;
const TABLET_TOUCH = [-0.3, -0.22, 0.18];
// what a hand holds level, the forearm across the waist as a waiter's is
const LEVEL_ITEMS = new Set(["colleague_mug"]);
const BUSY_ITEMS = new Set([...LEVEL_ITEMS, "squire_shield", "coach_clipboard"]);
// what a figure carries in its hands, put away while it holds a prop so it never holds two things
const IN_HAND = new Set([...BUSY_ITEMS, "squire_quill"]);
const MIN_EYE_HEIGHT = 0.06;
const HINGES = {forearm: new THREE.Vector3(0, 0, -1), shin: new THREE.Vector3(1, 0, 0)};

// Blender's Z up and -Y front become the glb's Y up and +Z front
const TO_GLB = new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1);
const FROM_GLB = TO_GLB.clone().invert();

const toBlender = (vector) => vector.clone().applyMatrix4(FROM_GLB);
const translation = (vector) => new THREE.Matrix4().makeTranslation(vector.x, vector.y, vector.z);
const radians = THREE.MathUtils.degToRad;

// Blender's Euler "XYZ" is Rz Ry Rx, which three.js names "ZYX"
const euler = (x, y, z) => new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(radians(x), radians(y), radians(z), "ZYX"));

function aboutPoint(at, turn) {
    return translation(at).multiply(turn).multiply(translation(at.clone().negate()));
}

function sideOf(name) {
    const match = name.match(/^(.*)_([lr])$/);
    return match ? {base: match[1], side: match[2]} : {base: name, side: ""};
}

function hingeAxis(base, side) {
    const {x, y, z} = HINGES[base];
    return side === "l" ? new THREE.Vector3(x, y, z) : new THREE.Vector3(x, -y, -z);
}

// rig.Posing, kept as each bone's move from its rest place (final @ matrix_local⁻¹) in Blender's armature space
export class Posing {
    constructor(rig, posture = "stand", stride = 0) {
        this.rig = rig;
        this.final = new Map();
        this.eyes = 1;
        this.eyeShape = null;
        this.eyeShift = [0, 0];
        this.bulbLit = 0;
        this.eyeTint = null;
        this.hearts = 0;
        this.stars = 0;
        this.squeezed = 0;
        this.laptop = false;
        this.tablet = false;
        this.cloth = false;
        this.book = null;
        this.props = new Map();
        this.stowed = new Set();
        this.keep = new Set();
        this.tap = 0;
        this.gaze = null;
        this.posture = posture;
        this.sway = 0;
        this.stride = stride;
        this.sky = null;
        this.screen = null;
    }

    standing(name) {
        const parent = this.rig.parents.get(name);
        return parent ? this.matrix(parent) : new THREE.Matrix4();
    }

    matrix(name) {
        return this.final.get(name) ?? this.standing(name);
    }

    head(name, move) {
        return this.rig.heads.get(name).clone().applyMatrix4(move);
    }

    turn(name, {x = 0, y = 0, z = 0}) {
        const current = this.matrix(name);
        this.final.set(name, aboutPoint(this.head(name, current), euler(x, y, z)).multiply(current));
    }

    face(name, {x = 0, y = 0, z = 0}) {
        const at = this.head(name, this.standing(name));
        const rest = this.rig.heads.get(name).clone().negate();
        this.final.set(
            name,
            translation(at)
                .multiply(euler(x, y, z))
                .multiply(translation(rest))
        );
    }

    lift(name, {x = 0, y = 0, z = 0}) {
        this.final.set(name, translation(new THREE.Vector3(x, y, z)).multiply(this.matrix(name)));
    }

    bend(name, degrees) {
        const {base, side} = sideOf(name);
        const standing = this.standing(name);
        const axis = hingeAxis(base, side).transformDirection(standing).normalize();
        const turn = new THREE.Matrix4().makeRotationAxis(axis, radians(degrees));
        this.final.set(name, aboutPoint(this.head(name, standing), turn).multiply(standing));
    }

    aim(name, direction) {
        const standing = this.standing(name);
        const now = this.rig.along.get(name).clone().transformDirection(standing);
        const turn = new THREE.Matrix4().makeRotationFromQuaternion(
            new THREE.Quaternion().setFromUnitVectors(now, direction.clone().normalize())
        );
        this.final.set(name, aboutPoint(this.head(name, standing), turn).multiply(standing));
    }

    // rig.Posing.reach for an arm: the hand's head put at `target`, the elbow pointing the way `bend` says
    reach(side, target, bend) {
        this.limbTo(side, ["upper_arm", "forearm", "hand"], target, bend);
    }

    // `target` brought in toward the shoulder on `side` until the arm reaches it, `share` of its full length at most
    withinReach(side, target, share) {
        const [shoulder, elbow, hand] = ["upper_arm", "forearm", "hand"].map((role) => this.rig.heads.get(`${role}_${side}`));
        const length = (elbow.distanceTo(shoulder) + hand.distanceTo(elbow)) * share;
        const from = this.head(`upper_arm_${side}`, this.standing(`upper_arm_${side}`));
        const way = target.clone().sub(from);
        return way.length() <= length ? target : from.clone().add(way.setLength(length));
    }

    // the same for a leg: the foot's head put at `target`, the knee pointing the way `bend` says
    step(side, target, bend) {
        this.limbTo(side, ["thigh", "shin", "foot"], target, bend);
    }

    limbTo(side, roles, target, bend) {
        const [upper, lower, end] = roles.map((role) => `${role}_${side}`);
        const first = this.rig.heads.get(lower).distanceTo(this.rig.heads.get(upper));
        const second = this.rig.heads.get(end).distanceTo(this.rig.heads.get(lower));
        const shoulder = this.head(upper, this.standing(upper));
        const way = target.clone().sub(shoulder);
        const distance = way.length();
        if (distance < Math.abs(first - second) || distance > first + second) {
            throw new Error(`the ${upper} cannot reach ${distance.toFixed(3)}`);
        }
        const along = way.clone().normalize();
        const back = (first * first - second * second + distance * distance) / (2 * distance);
        const pole = bend.clone();
        if (side === "r") {
            pole.x = -pole.x;
        }
        pole.sub(along.clone().multiplyScalar(pole.dot(along)));
        const middle = shoulder
            .clone()
            .add(along.multiplyScalar(back))
            .add(pole.normalize().multiplyScalar(Math.sqrt(Math.max(first * first - back * back, 0))));
        this.aim(upper, middle.clone().sub(shoulder));
        this.aim(lower, target.clone().sub(middle));
    }

    // Rotate a snapshot, not a parent already rotated twice.
    turnAll({x = 0, y = 0, z = 0}, at = new THREE.Vector3()) {
        const turn = aboutPoint(at, euler(x, y, z));
        this.final = new Map(this.rig.order.map((name) => [name, turn.clone().multiply(this.matrix(name))]));
    }

    revolve(degrees) {
        this.turnAll({z: degrees});
    }

    // `name` and every bone above it as posed so far turned about its head, as a back bent forward carries the shoulders, arms and head
    bendAbove(name, {x = 0, y = 0, z = 0}) {
        const turn = aboutPoint(this.head(name, this.matrix(name)), euler(x, y, z));
        const above = (bone) => bone === name || (Boolean(bone) && above(this.rig.parents.get(bone)));
        this.final = new Map(this.rig.order.map((bone) => [bone, above(bone) ? turn.clone().multiply(this.matrix(bone)) : this.matrix(bone)]));
    }

    // the whole figure as posed so far moved by `offset`
    shiftAll(offset) {
        const shift = translation(new THREE.Vector3(...offset));
        this.final = new Map(this.rig.order.map((name) => [name, shift.clone().multiply(this.matrix(name))]));
    }

    // a point given against the body at rest, carried wherever the root has been lifted or moved
    carried(point) {
        return point.clone().add(this.head("root", this.matrix("root")).sub(this.rig.heads.get("root")));
    }

    // how far the legs of a seated figure swing, from -1 to 1
    swing(sway) {
        this.sway = sway;
    }

    shutEyes(open) {
        this.eyes = Math.max(open, MIN_EYE_HEIGHT);
    }

    // the eyes in their own shape glancing up `up` of their height and aside `aside` of it, toward the figure's left
    glanceEyes(up, aside) {
        this.eyeShift = [aside, up];
    }

    // the eyes taking on the shape `name` of EYE_SHAPES, `strength` of the way from their own, aside toward `way`, 1 the figure's left
    shapeEyes(name, strength = 1, way = 1) {
        this.eyeShape = strength > 0 ? {name, strength, way} : null;
    }

    // the eyes' colour, as red, green and blue from 0 to 1; none leaves them their own
    tintEyes(colour) {
        this.eyeTint = colour;
    }

    // hearts in place of the eyes, `size` times their own size; 0 leaves the eyes
    heartEyes(size) {
        this.hearts = size;
    }

    // sparkling stars in place of the eyes, `size` times their own size; 0 leaves the eyes
    starEyes(size) {
        this.stars = size;
    }

    // the eyes squeezed shut laughing, a kawaii > <, `size` times their own size; 0 leaves the eyes
    squeezeEyes(size) {
        this.squeezed = size;
    }

    // a laptop open on the lap, its lid toward the face
    holdLaptop() {
        this.laptop = true;
    }

    // the tablet in the hand at the end of the forearm held across the waist, for the free hand to write on or swipe
    holdTablet() {
        this.tablet = true;
    }

    // the cloth out of the pocket, in the hand that keeps it
    holdCloth() {
        this.cloth = true;
    }

    holdBook(open, page, visible) {
        this.book = {open, page, visible};
    }

    holdProp(name, side, offset = [0, 0, 0], turn = {}) {
        this.props.set(name, {bone: `hand_${side}`, frame: `hand_${side}`, at: this.grip(side, offset), turn});
    }

    // a prop in the hand on `side` that keeps turned as the body is, not as the hand is, so a glass or a trophy stays upright
    holdUpright(name, side, offset = [0, 0, 0], turn = {}) {
        this.props.set(name, {bone: `hand_${side}`, frame: "root", at: this.grip(side, offset), turn});
    }

    // a prop standing on the floor at `at` in the figure's units, turned as the figure is and then by `turn`; a crouch lowers the root, so
    // `at` is given raised by as much for the prop to stay on the floor
    standProp(name, at, turn = {}) {
        this.props.set(name, {bone: "root", frame: "root", at: new THREE.Vector3(...at), turn});
    }

    // the light bulb over the head (LIGHT_BULB) toward `way`, 1 the figure's left, grown in `size` of the way and lit `lit` of the way,
    // both 0 to 1
    lightBulb(size, lit, way) {
        const [x, y, z] = LIGHT_BULB.at;
        this.standProp("light_bulb", [way * x, y, z]);
        Object.assign(this.props.get("light_bulb"), {size, lit});
        this.bulbLit = lit;
    }

    // a prop worn on the head, `offset` from the head's own place at rest, as the hat lifted from it or the sunglasses put on
    wearProp(name, offset, turn = {}) {
        this.props.set(name, {bone: "head", frame: "head", at: this.rig.heads.get("head").clone().add(new THREE.Vector3(...offset)), turn});
    }

    // the bone `name` turned `degrees` about its own length, as the forearm turns the hand over
    roll(name, degrees) {
        const current = this.matrix(name);
        const along = this.rig.along.get(name).clone().transformDirection(current).normalize();
        this.final.set(name, aboutPoint(this.head(name, current), new THREE.Matrix4().makeRotationAxis(along, radians(degrees))).multiply(current));
    }

    // the hand on `side` closed into a fist, its fingers curled in to `share` of the open hand's length, as it grips a handle
    clench(side, share) {
        const name = `hand_${side}`;
        const head = this.rig.heads.get(name);
        const along = this.rig.along.get(name).clone().normalize();
        const scale = new THREE.Matrix4().set(
            1 + (share - 1) * along.x * along.x, (share - 1) * along.x * along.y, (share - 1) * along.x * along.z, 0,
            (share - 1) * along.y * along.x, 1 + (share - 1) * along.y * along.y, (share - 1) * along.y * along.z, 0,
            (share - 1) * along.z * along.x, (share - 1) * along.z * along.y, 1 + (share - 1) * along.z * along.z, 0,
            0, 0, 0, 1,
        );
        this.final.set(name, this.matrix(name).clone().multiply(aboutPoint(head, scale)));
    }

    // where the hand on `side` grips at rest, `offset` from its own grip
    grip(side, offset) {
        return this.rig.heads.get(`hand_${side}`).clone().add(new THREE.Vector3(SIDES[side] * (HAND.grip + offset[0]), HAND.forward + offset[1], offset[2]));
    }

    putAway(...items) {
        items.forEach((item) => this.stowed.add(item));
    }

    // every bone's move, the whole figure turned `facing` degrees toward the viewer's right as rig.Posing.revolve turns it
    moves(facing) {
        const turn = new THREE.Matrix4().makeRotationZ(radians(facing));
        const moves = new Map();
        for (const name of this.rig.order) {
            const parent = this.rig.parents.get(name);
            moves.set(name, this.final.get(name) ?? (parent ? moves.get(parent) : new THREE.Matrix4()));
        }
        return new Map([...moves].map(([name, move]) => [name, turn.clone().multiply(move)]));
    }
}

const waveOf = (t, turns = 1) => Math.sin(2 * Math.PI * turns * t);

function breathe(pose, t, amount = 1) {
    pose.turn("spine", {x: 1.0 * amount * waveOf(t)});
    pose.turn("chest", {x: 1.5 * amount * waveOf(t - 0.05)});
    pose.turn("neck", {x: -0.8 * amount * waveOf(t - 0.1)});
    pose.turn("head", {x: -1.2 * amount * waveOf(t - 0.12)});
}

function trunk(pose, {lean = 0, twist = 0, nod = 0, turn = 0, tilt = 0}) {
    pose.turn("spine", {x: lean * 0.4, z: twist * 0.4});
    pose.turn("chest", {x: lean * 0.6, z: twist * 0.6});
    pose.turn("neck", {x: nod * 0.3, z: turn * 0.3, y: tilt * 0.3});
    pose.turn("head", {x: nod * 0.7, z: turn * 0.7, y: tilt * 0.7});
}

function hang(pose, side, swing = 0, bend = 10) {
    pose.turn(`upper_arm_${side}`, {y: SIDES[side] * HANG});
    pose.turn(`upper_arm_${side}`, {x: swing});
    pose.bend(`forearm_${side}`, bend);
}

// clips.hold: `lift` is how far above flat the forearm points, `forward` how far the upper arm swings forward, `tip` how far the hand tips what it holds
function hold(pose, side, lift = HOLD_LIFT, forward = 0, tip = 0) {
    const sign = SIDES[side];
    pose.turn(`upper_arm_${side}`, {y: sign * HANG});
    pose.turn(`upper_arm_${side}`, {x: -forward});
    pose.turn(`upper_arm_${side}`, {z: sign * HOLD_ROLL});
    pose.face(`forearm_${side}`, {y: -sign * lift, z: -sign * HOLD_SWING});
    pose.face(`hand_${side}`, {x: tip, z: -sign * (HOLD_SWING - HOLD_WRIST)});
}

function armsAtRest(pose, stance, apart = [], swing = {}, level = stance.level) {
    for (const side of Object.keys(SIDES)) {
        if (apart.includes(side)) {
            continue;
        }
        if (level.has(side)) {
            hold(pose, side);
            continue;
        }
        hang(pose, side, swing[side] ?? 0);
        if (stance.shield?.has(side)) pose.turn(`hand_${side}`, {y: -SIDES[side] * SHIELD_ROLL, z: SIDES[side] * SHIELD_TURN});
    }
}

const freeSide = (stance) => (stance.busy.has("r") ? "l" : "r");

function idle(pose, stance, t) {
    breathe(pose, t);
    armsAtRest(pose, stance);
    pose.swing(waveOf(t));
}

function nod(pose, stance, t) {
    const dip = Math.max(waveOf(t, 2), 0);
    trunk(pose, {lean: 4 * dip, nod: 26 * dip});
    armsAtRest(pose, stance);
}

// Rubbing its hands together before its chest, pleased with a job well done (acts.js hand_rub): the hands meet at `at` (across, forward, up),
// each `apart` to its own side of it, and slide round each other in circles `circle` round turning opposite ways, so each passes the other
// over and under; the head nods `nod` degrees with each rub
export const RUB = {at: [0, -0.62, 1.95], apart: 0.07, circle: 0.13, nod: 8};

function hand_rub(pose, stance, t) {
    const act = ACTS.hand_rub;
    const u = onceTime(t, act.frames);
    const ready = partOf(u, act.together) * (1 - partOf(u, act.apart));
    const angle = 2 * Math.PI * act.rubs * span(u, act.together[1], act.apart[0]);
    breathe(pose, 0);
    trunk(pose, {lean: 4 * ready, nod: RUB.nod * ready * (0.5 + 0.5 * Math.sin(2 * angle))});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, ready ? Object.keys(SIDES) : []);
    const [x, y, z] = RUB.at;
    for (const [side, sign] of Object.entries(SIDES)) {
        const spot = new THREE.Vector3(x + sign * (RUB.apart + RUB.circle * Math.cos(angle)), y, z + sign * RUB.circle * Math.sin(angle));
        if (ready) handTo(pose, side, ready, pose.withinReach(side, pose.carried(spot), 0.97), new THREE.Vector3(...ACTING.elbow));
    }
    eyesAs(pose, "amused", ready);
}

function shake(pose, stance, t) {
    trunk(pose, {turn: 28 * waveOf(t, 2), tilt: 4 * waveOf(t, 2)});
    armsAtRest(pose, stance);
}

function wave(pose, stance, t) {
    const side = freeSide(stance);
    const sign = SIDES[side];
    trunk(pose, {twist: -sign * 4, turn: -sign * 8, tilt: -sign * 6});
    armsAtRest(pose, stance, [side]);
    waveArm(pose, side, t);
}

// the arm on `side` raised and waving
function waveArm(pose, side, t) {
    pose.turn(`upper_arm_${side}`, {x: -RAISED_ROLL});
    pose.turn(`upper_arm_${side}`, {z: SIDES[side] * WAVE_BACK});
    pose.bend(`forearm_${side}`, WAVE_BEND + WAVE_SWING * waveOf(t));
}

// How the figure thinks: the head tipped back `nod` degrees and turned `turn` away from the free hand; the free hand's knuckles at the
// head's `chin`, the front of its bottom edge (measured on the head shell, the same on every voice), the hand pointing up along `fist`
// with its wrist under them and its elbow pointing down along `elbow`; the other forearm folded across the body under that elbow, its
// hand `inboard` of the way from the middle out to that elbow and `under` it, its own elbow out along `folded`; the knuckles tapping the
// chin `taps` times a loop, each tap lifting them `tap` off it and back; and the eyes glancing up `glance` of their height, and aside
export const THINKING = {nod: -10, turn: 14, chin: [0, -0.58, 2.5], fist: [0.15, -0.2, 1], elbow: [0.1, -0.5, -1], inboard: 0.1, under: 0.12, folded: [1, -0.6, -0.4], taps: 2, tap: 0.08, glance: [0.35, 0.3]};

// The thinking act (acts.js ponder): the head tilted `tilt` degrees to the free hand's side and up `nod`, swaying `sway` degrees; the free
// hand's fingers along the cheek at `cheek`, beside the bottom of the head, pointing up along `finger`; and at its end, "got it", the
// hand raised before the shoulder at `gotIt`, its finger up
export const PONDERING = {tilt: 22, nod: -12, sway: 4, cheek: [0.38, -0.78, 2.6], finger: [0.2, 0.15, 1], gotIt: [0.85, -0.45, 2.75]};

// the wrist of the hand on `side` put so its grip is at `grip`, the hand pointing along `along`, `k` of the way up from hanging
function handAlong(pose, side, k, grip, along, elbow) {
    handTo(pose, side, k, grip.clone().addScaledVector(along, -HAND.grip), elbow);
    pose.aim(`hand_${side}`, new THREE.Vector3(0, 0, -1).lerp(along, k).normalize());
}

// the forearm on `side` folded across the body under the elbow of the arm on `other`, `k` of the way up from hanging
function foldUnder(pose, side, other, k) {
    const elbow = pose.head(`forearm_${other}`, pose.matrix(`forearm_${other}`));
    const under = new THREE.Vector3(elbow.x * THINKING.inboard, elbow.y, elbow.z - THINKING.under);
    handTo(pose, side, k, pose.withinReach(side, under, 0.97), new THREE.Vector3(...THINKING.folded));
}

// thinks it over, its knuckles at its chin and that elbow resting on the other arm folded across its body, its eyes glancing up and
// aside, the hand tapping slowly at the chin
function think(pose, stance, t) {
    const side = freeSide(stance);
    const other = side === "l" ? "r" : "l";
    const sign = SIDES[side];
    const tapping = Math.max(waveOf(t, THINKING.taps), 0) ** 3;
    breathe(pose, t);
    trunk(pose, {nod: THINKING.nod + 2 * waveOf(t), turn: -sign * THINKING.turn, tilt: -sign * 4});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, [side, other]);
    const chin = new THREE.Vector3(...THINKING.chin).applyMatrix4(pose.matrix("head"));
    const [across, forward, up] = THINKING.fist;
    const fist = new THREE.Vector3(-sign * across, forward, up).normalize();
    handAlong(pose, side, 1, chin.addScaledVector(fist, -THINKING.tap * tapping), fist, new THREE.Vector3(...THINKING.elbow));
    foldUnder(pose, other, side, 1);
    pose.glanceEyes(THINKING.glance[0], -sign * THINKING.glance[1]);
}

// The thinking act, played now and then while the agent thinks: it tilts its head up and to one side, swaying a little, its finger along
// its cheek and that elbow on the other arm folded across it, its eyes glancing up and aside, while a thought cloud rises over its head
// (chat/FigureAct.vue); and it always ends with "got it", the head up, the eyes wide and the finger raised as the bulb lights
function ponder(pose, stance, t) {
    const act = ACTS.ponder;
    const u = onceTime(t, act.frames);
    const side = freeSide(stance);
    const other = side === "l" ? "r" : "l";
    const sign = SIDES[side];
    const thinking = partOf(u, act.into) * (1 - partOf(u, act.rise));
    const got = partOf(u, act.rise) * (1 - partOf(u, act.fades));
    const sway = Math.sin(2 * Math.PI * act.sways * u) * thinking;
    breathe(pose, t);
    trunk(pose, {nod: PONDERING.nod * thinking - 10 * got, tilt: -sign * (PONDERING.tilt * thinking + PONDERING.sway * sway), turn: 3 * sway});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, [...(thinking + got ? [side] : []), ...(thinking ? [other] : [])]);
    const [x, y, z] = PONDERING.cheek;
    const cheek = new THREE.Vector3(sign * x, y, z).applyMatrix4(pose.matrix("head"));
    const [gx, gy, gz] = PONDERING.gotIt;
    const raised = pose.carried(new THREE.Vector3(sign * gx, gy, gz + HAND.grip));
    const [across, forward, up] = PONDERING.finger;
    const finger = new THREE.Vector3(-sign * across, forward, up).normalize();
    if (thinking + got) handAlong(pose, side, Math.max(thinking, got), cheek.lerp(raised, partOf(u, act.rise)), finger, new THREE.Vector3(...THINKING.elbow));
    if (thinking) foldUnder(pose, other, side, thinking);
    pose.glanceEyes(THINKING.glance[0] * thinking, -sign * THINKING.glance[1] * thinking);
    eyesAs(pose, "startled", got);
    if (u >= act.appears[0]) pose.lightBulb(partOf(u, act.appears) * (1 - partOf(u, act.goes)), partOf(u, act.lights) * (1 - partOf(u, act.fades)), sign);
}

// the chin rested on the hand on `side`
function chinOnHand(pose, side) {
    const sign = SIDES[side];
    const [x, y, z] = CHIN_REST;
    pose.reach(side, pose.carried(new THREE.Vector3(sign * x, y, z)), new THREE.Vector3(...THINK_ELBOW));
    const [across, forward, up] = THINK_HAND;
    pose.aim(`hand_${side}`, new THREE.Vector3(-sign * across, forward, up));
    pose.turn(`hand_${side}`, {x: THINK_TIP});
}

function celebrate(pose, stance, t) {
    const jump = Math.max(Math.sin(2 * Math.PI * 2 * t), 0);
    pose.lift("root", {z: 0.28 * jump});
    pose.turn("hips", {z: 6 * waveOf(t, 2)});
    trunk(pose, {lean: -5, turn: -6 * waveOf(t, 2)});
    const cheering = Object.keys(SIDES).filter((side) => !stance.busy.has(side));
    armsAtRest(pose, stance, cheering);
    for (const side of cheering) {
        const sign = SIDES[side];
        armTo(pose, side, 1, {y: -ARM_CLEAR_RAISE, bend: 10 + 6 * waveOf(t, 4)});
    }
    for (const side of Object.keys(SIDES)) {
        pose.turn(`thigh_${side}`, {x: -18 * jump});
        pose.turn(`shin_${side}`, {x: 34 * jump});
        pose.turn(`foot_${side}`, {x: -10 * jump});
    }
}

function sleep(pose, stance, t) {
    const frame = t * (ACTING.yawnFrames + SLEEP_FRAMES);
    if (frame < ACTING.yawnFrames) return yawn(pose, stance, frame / ACTING.yawnFrames);
    const breath = waveOf((frame - ACTING.yawnFrames) / SLEEP_FRAMES);
    trunk(pose, {lean: 4 + 1.5 * breath, nod: 8 + 2 * breath, tilt: SIDES[freeSide(stance)] * SLEEP_TILT});
    armsAtRest(pose, stance);
    pose.shutEyes(0.0);
}

function walk(pose, stance, t) {
    pose.stride = t;
    const phase = 2 * Math.PI * t;
    strideUnder(pose);
    pose.turn("hips", {z: 5 * Math.sin(phase)});
    trunk(pose, {lean: 3, twist: -7 * Math.sin(phase), turn: 3 * Math.sin(phase)});
    armsAtRest(pose, stance, [], {l: 22 * Math.sin(phase), r: -22 * Math.sin(phase)});
    strideLegs(pose);
}

// The walk's lower body at `pose.stride` of its cycle: the body bobbing before a clip poses the rest, and the legs stepping after it. Every
// clip drawn on the move walks on these, so the figure goes on thinking or working as it goes; the hips' sway is the walk's own, as a
// clip that reaches for the chin or the lap places its hands against an upper body that does not swing
function strideUnder(pose) {
    pose.lift("root", {z: 0.05 * Math.cos(4 * Math.PI * pose.stride)});
}

function strideLegs(pose) {
    for (const [side, offset] of [
        ["l", 0.0],
        ["r", Math.PI],
    ]) {
        const angle = 2 * Math.PI * pose.stride + offset;
        const thigh = -30 * Math.sin(angle);
        const knee = 42 * Math.max(Math.cos(angle), 0);
        pose.turn(`thigh_${side}`, {x: thigh});
        pose.turn(`shin_${side}`, {x: knee});
        pose.turn(`foot_${side}`, {x: -0.8 * (thigh + knee) + 6});
    }
}

// New clips: a direct numerical port of clips.py, not an interpolated animation.
const ENTRY_DISTANCE = 4.4;
const ENTRY_TRAVEL_END = 0.72;
const ENTRY_TURN_END = 0.94;
const RUN_STRIDE = [1.84, 0.38, 0.2];
const WALK_STRIDE = [1.36, 0.6, 0.16];
const DEPART_TURN = 0.14;
const SEAT_LIFT = 0.2;
// how far each knee bends when sitting on an edge; under a right angle the feet reach ahead of the knees, as a person sits on a wall
const SEAT_SHIN = 66;
const PULL_GRIP_X = 1.51;
const PULL_GRIP_Y = -0.0233463035019455;
const PULL_GRIP_Z = 3.17;
const PULL_WRIST_X = 1.25;
const PULL_WRIST_Z = 2.91;
const PULL_ROOT = {back: 0.58, up: 0.36, rise: 0.38};
const PULL_ELBOW = new THREE.Vector3(1, -1, -1);

function ease(t) {
    t = Math.min(Math.max(t, 0), 1);
    return t * t * (3 - 2 * t);
}

function onceTime(t, frames) {
    return Math.min(Math.max((t * frames) / (frames - 1), 0), 1);
}

// how far u is through the stretch from `from` to `to`, held at 0 before and 1 after; eased, and as a swell that rises and falls back to 0
const span = (u, from, to) => Math.min(Math.max((u - from) / (to - from), 0), 1);
const rise = (u, from, to) => ease(span(u, from, to));
const swell = (u, from, to) => Math.sin(Math.PI * span(u, from, to));
const mix = (from, to, k) => from + (to - from) * k;

// a ring that dies away over s from 0 to 1: `turns` swings, damped by `damping`, and exactly still at both ends
const ringing = (s, turns, damping) => Math.exp(-damping * s) * Math.sin(2 * Math.PI * turns * s) * (1 - s);

export function supportsClip(name, stance) {
    return name !== "pull_ups" || !(stance.busy.size || stance.level.size);
}

// A figure sitting on an edge: the root lifted onto the seat before any clip poses it, and after it the thighs forward and the knees bent
// over the edge, swinging as the clip says. Every clip but those that move the whole body is drawn seated this way as well as standing.
// seated, the body lifted onto the seat, sitting on whatever hangs behind it, as the butler's tails, out of sight under it
function seat(pose) {
    pose.lift("root", {z: SEAT_LIFT});
    pose.putAway(...BUTLER.satOn);
}

// Lounging on a floor's top (places.js POSTURES lounge): sat on it with the legs straight out toward the viewer, the feet up, leaning
// back on both hands set flat on the floor a little behind the hips; the floor line is LOUNGE.floor above the standing feet in the
// figure's units, where the hips' seat meets it
export const LOUNGE = {lean: -24, feet: 18, hands: [0.62, 0.5], floor: 1.4};

function loungedLegs(pose) {
    for (const side of Object.keys(SIDES)) {
        pose.turn(`thigh_${side}`, {x: -88});
        pose.turn(`foot_${side}`, {x: LOUNGE.feet});
    }
    trunk(pose, {lean: LOUNGE.lean, nod: -LOUNGE.lean * 0.6});
    for (const [side, sign] of Object.entries(SIDES)) {
        const flat = new THREE.Vector3(sign * LOUNGE.hands[0], LOUNGE.hands[1], LOUNGE.floor);
        handTo(pose, side, 1, pose.withinReach(side, flat, 0.97), new THREE.Vector3(0.6, 1, 0));
        pose.face(`hand_${side}`, {x: -80});
    }
}

// Sitting composed on a floor's top (places.js POSTURES composed): sat upright facing the viewer with its knees up, its feet flat on the
// floor before it at `feet` (across, forward, up from the standing feet, in the figure's units), never its legs straight out toward the
// viewer, and both hands set flat on the floor at its sides; the floor line is `floor` above the standing feet, as when it lounges
export const COMPOSED = {feet: [0.3, -0.72, 1.5], hands: [0.78, -0.05], nod: -4, floor: LOUNGE.floor};

function composedLegs(pose) {
    for (const [side, sign] of Object.entries(SIDES)) {
        const [x, y, z] = COMPOSED.feet;
        pose.step(side, new THREE.Vector3(sign * x, y, z), new THREE.Vector3(0, -1, 1));
    }
    trunk(pose, {nod: COMPOSED.nod});
    for (const [side, sign] of Object.entries(SIDES)) {
        const flat = new THREE.Vector3(sign * COMPOSED.hands[0], COMPOSED.hands[1], COMPOSED.floor);
        handTo(pose, side, 1, pose.withinReach(side, flat, 0.97), new THREE.Vector3(1, 0.3, 0));
        pose.face(`hand_${side}`, {x: -80});
    }
}

function seatedLegs(pose) {
    for (const [side, sign] of Object.entries(SIDES)) {
        pose.turn(`thigh_${side}`, {x: -88});
        pose.bend(`shin_${side}`, SEAT_SHIN + sign * 9 * pose.sway);
        pose.turn(`foot_${side}`, {x: -sign * 5 * pose.sway + (side === "r" ? pose.tap : 0)});
    }
}

// the body lowered by `depth` on bent knees, the feet flat where they stand; seated or walking, the posture has the legs
function crouch(pose, depth) {
    if (pose.posture !== "stand") return;
    pose.lift("root", {z: -depth});
    fold(pose, depth);
}

// the hands of the figure that carry nothing, carried up through the front to a spot `k` of the way (0 hanging, 1 there), the spot
// given against the body at rest
function handsTo(pose, stance, k, spot, elbow = THINK_ELBOW) {
    armsAtRest(pose, stance, [...stance.free]);
    for (const side of stance.free) {
        handTo(pose, side, k, pose.carried(new THREE.Vector3(SIDES[side] * spot[0], spot[1], spot[2])), new THREE.Vector3(...elbow));
    }
}

// The looks the eyes take on, over whatever the body does: how far they open, the colour they turn, whether they are hearts, and the shape
// of EYE_SHAPES they take on. The helmet hides everything else, so the eyes carry the expression.
export const EYES = {
    hearts: {open: 1, tint: null, hearts: true},
    amused: {open: 0.3, tint: [1, 0.85, 0.4]},
    startled: {open: 1.5, tint: [1, 1, 1]},
    worried: {open: 0.7, tint: [0.6, 0.75, 1]},
    angry: {open: 0.45, tint: [1, 0.35, 0.3]},
    reading: {open: 0.8, tint: null},
    focused: {open: 1, tint: null, shape: "focused"},
    narrowed: {open: 1, tint: null, shape: "narrowed"},
    bright: {open: 1, tint: null, shape: "bright"},
    calm: {open: 1, tint: null, shape: "calm"},
    eyeing: {open: 1, tint: null, shape: "eyeing"},
};

function eyesAs(pose, mood, strength = 1) {
    const {open, tint, shape} = EYES[mood];
    pose.shutEyes(mix(1, open, strength));
    if (tint && strength > 0.5) pose.tintEyes(tint);
    if (shape) pose.shapeEyes(shape, strength);
}

// where the hands rest to type on a laptop on the lap, and where they cover the eyes
const TYPING_HANDS = [0.3, -0.45, 2.0];
const EYE_HANDS = [0.46, -0.82, 2.04];

// head down at a laptop on its lap, the hands moving, and now and then a pause
function type(pose, stance, t) {
    const pause = swell(t, 0.55, 0.75);
    const tap = (1 - pause) * waveOf(t, 6);
    breathe(pose, 0);
    trunk(pose, {lean: 6, nod: 20 - 4 * pause, turn: 2 * waveOf(t)});
    handsTo(pose, stance, 1, [TYPING_HANDS[0], TYPING_HANDS[1], TYPING_HANDS[2] + 0.035 * tap]);
    pose.holdLaptop();
    eyesAs(pose, "reading");
}

// jumps for joy: both arms thrown up and the whole body leaving the ground, or the seat, twice, the head back
function joy(pose, stance, t) {
    const u = onceTime(t, ACTS.joy.frames);
    const leap = Math.max(Math.sin(2 * Math.PI * ACTS.joy.jumps * span(u, 0.06, 0.94)), 0) * (1 - 0.3 * u);
    pose.lift("root", {z: 0.32 * leap});
    breathe(pose, 0);
    trunk(pose, {lean: -5 * leap, nod: -14 + 4 * leap});
    flung(pose, stance, 0, 70 + 55 * leap, 6 * waveOf(t, 4));
    tucked(pose, 0.5 * leap);
}

// the hands go up over the eyes, then a slow shake of the head, then the hands come down
function dismay(pose, stance, t) {
    const u = onceTime(t, 28);
    const hands = rise(u, 0, 0.2) * (1 - rise(u, 0.82, 1));
    const shaking = swell(u, 0.28, 0.82);
    breathe(pose, 0);
    trunk(pose, {lean: 4 * hands, nod: 10 * hands, turn: 24 * shaking * waveOf(span(u, 0.28, 0.82), 1.5)});
    handsTo(pose, stance, hands, EYE_HANDS);
    for (const side of stance.free) pose.face(`hand_${side}`, {z: -SIDES[side] * 90 * hands});
    eyesAs(pose, "worried", hands);
}

// stretches both arms up and leans back with a yawn, then settles
function stretch(pose, stance, t) {
    const u = onceTime(t, 24);
    const up = swell(u, 0.05, 0.9);
    breathe(pose, 0);
    trunk(pose, {lean: -10 * up, nod: -10 * up});
    flung(pose, stance, 0, 100 * up);
    pose.shutEyes(1 - 0.9 * swell(u, 0.2, 0.75));
}

function strideFoot(phase, stride, duty, clearance) {
    phase = ((phase % 1) + 1) % 1;
    const span = stride * duty;
    if (phase < duty) {
        return [-span / 2 + stride * phase, 0];
    }
    const flight = (phase - duty) / (1 - duty);
    return [span / 2 - span * ease(flight), clearance * Math.sin(Math.PI * flight)];
}

function stepLeg(pose, side, forward, lift, rootHeight, toe = 0) {
    const thigh = pose.rig.heads.get(`thigh_${side}`);
    const shin = pose.rig.heads.get(`shin_${side}`);
    const foot = pose.rig.heads.get(`foot_${side}`);
    const upper = thigh.z - shin.z,
        lower = shin.z - foot.z;
    const down = upper + lower + rootHeight - lift;
    const cosine = (forward * forward + down * down - upper * upper - lower * lower) / (2 * upper * lower);
    if (cosine < -1 - 1e-10 || cosine > 1 + 1e-10) {
        throw new RangeError(`${side} stride target is outside the unchanged leg reach`);
    }
    const knee = Math.acos(Math.round(cosine * 1e10) / 1e10);
    const hip = Math.atan2(forward, down) - Math.atan2(lower * Math.sin(knee), upper + lower * Math.cos(knee));
    pose.turn(`thigh_${side}`, {x: (hip * 180) / Math.PI});
    pose.bend(`shin_${side}`, (knee * 180) / Math.PI);
    pose.face(`foot_${side}`, {x: toe});
}

// A stride `cycle` steps into its run along the figure's own forward line, faded out by `motion`, posed parent first: the root's bob lowered by `drop`,
// the trunk with idle's first breath, its lean and any `bend` of the trunk on top, the arms not held `apart`, and the legs, folded by `drop` when standing,
// their steps `behind` the hips by so much, as when leaning into a push
function stride(pose, stance, cycle, motion, {running = false, lean = running ? 10 : 3, clearance, apart = [], drop = 0, bend = {}, behind = 0} = {}) {
    const [length, duty, lift] = running ? RUN_STRIDE : WALK_STRIDE;
    const halfPhase = cycle % 0.5;
    const flight = running && halfPhase > duty ? Math.max(0, Math.sin((Math.PI * (halfPhase - duty)) / (0.5 - duty))) : 0;
    const rootHeight = motion * (-(running ? 0.075 : 0.11) + (running ? 0.055 * flight : 0)) - drop;
    pose.lift("root", {z: rootHeight});
    breathe(pose, 0);
    trunk(pose, {...bend, lean: lean * motion + (bend.lean ?? 0), nod: (running ? -6 : -2) * motion + (bend.nod ?? 0)});
    const swing = (running ? 24 : 14) * waveOf(cycle) * motion;
    const carried = stance.carried ?? stance.busy;
    const jogging = Object.keys(SIDES).filter((side) => running && !carried.has(side) && !stance.level.has(side) && !apart.includes(side));
    armsAtRest(
        pose,
        stance,
        [...jogging, ...apart],
        Object.fromEntries(Object.entries(SIDES).map(([side, sign]) => [side, carried.has(side) ? 0 : sign * swing]))
    );
    for (const side of jogging) hang(pose, side, SIDES[side] * swing, 10 + 40 * motion);
    if (motion > 0 || drop || behind) {
        for (const [side, offset] of [
            ["l", 0],
            ["r", 0.5],
        ]) {
            const [step, raised] = strideFoot(cycle + offset, length, duty, clearance ?? lift);
            const phase = (cycle + offset) % 1;
            const flightPhase = phase >= duty ? (phase - duty) / (1 - duty) : 0;
            const toe = (running ? 14 : 11) * Math.sin(Math.PI * flightPhase) * motion;
            stepLeg(pose, side, motion * step + behind, motion * raised, rootHeight, toe);
        }
    }
}

// An arrival from the left: off the frame at the start, home by `until`, turned to face the viewer by `faced`; returns the facing to revolve to last
function arrive(pose, stance, u, until, faced, gait = {}) {
    const q = span(u, 0, until);
    const progress = ease(q);
    pose.lift("root", {y: ENTRY_DISTANCE * (1 - progress)});
    stride(pose, stance, (ENTRY_DISTANCE * progress) / (gait.running ? RUN_STRIDE : WALK_STRIDE)[0], 1 - ease((q - 0.76) / 0.24), gait);
    return 90 * (1 - rise(u, until, faced));
}

// A departure toward `way` (1 the viewer's right, -1 the left) from home at `from`: it turns first, then strides off the frame, gathering speed; returns the facing
function depart(pose, stance, u, from, way, gait = {}) {
    const q = span(u, from + DEPART_TURN / 2, 1);
    const progress = (q < 0.3 ? (q * q) / 0.6 : q - 0.15) / 0.85;
    pose.lift("root", {y: -ENTRY_DISTANCE * progress});
    stride(pose, stance, (ENTRY_DISTANCE * progress) / (gait.running ? RUN_STRIDE : WALK_STRIDE)[0], ease(q / 0.25), gait);
    return way * 90 * rise(u, from, from + DEPART_TURN);
}

function entering(pose, stance, t, frames, running = false) {
    pose.revolve(arrive(pose, stance, onceTime(t, frames), ENTRY_TRAVEL_END, ENTRY_TURN_END, {running}));
}

function walk_in(pose, stance, t) {
    entering(pose, stance, t, 40);
}

function run_in(pose, stance, t) {
    entering(pose, stance, t, 28, true);
}

function pull_ups(pose, stance, t) {
    if (!supportsClip("pull_ups", stance)) {
        idle(pose, stance, t);
        return;
    }
    gripping(pose, stance, t, {pull: 0.5 - 0.5 * Math.cos(2 * Math.PI * t), swing: 0});
}

// hangs from a ledge by one hand, `side`, with the body below and the feet loose and swinging a little; the other arm hangs or carries
const dangle = (side) => (pose, stance, t) => gripping(pose, stance, t, {pull: 0, swing: waveOf(t), grips: [side]});

function gripping(pose, stance, t, {pull, swing, grips = Object.keys(SIDES)}) {
    const free = grips.filter((side) => stance.free.has(side));
    pose.lift("root", {y: PULL_ROOT.back, z: PULL_ROOT.up + PULL_ROOT.rise * pull});
    trunk(pose, {nod: -3 * pull, turn: 2 * swing});
    armsAtRest(pose, stance, free);
    for (const [side, sign] of Object.entries(SIDES)) {
        pose.turn(`thigh_${side}`, {x: -8 + 7 * swing * sign});
        pose.bend(`shin_${side}`, 18 + 8 * swing * sign);
        pose.turn(`foot_${side}`, {x: -10});
        if (!free.includes(side)) continue;
        pose.reach(side, new THREE.Vector3(sign * PULL_WRIST_X, 0, PULL_WRIST_Z), PULL_ELBOW);
        pose.face(`hand_${side}`, {x: -90});
    }
}

// Each voice comes in and goes out in a manner of its own; an entrance ends on idle's first frame and an exit starts on it.
const ENTER_FRAMES = 36;
const EXIT_FRAMES = 28;
const BUTLER_SPRINT = 0.5;
const BUTLER_BOW = 0.36;
const PLATE_PITCH = 16;
const PLATE_ROLL = 7;
const CLIMB_PEEK = -2.45;
const CLIMB_PULLED = -1.54;
const CLIMB_GRIP = new THREE.Vector3(1.0, -0.6, 0.02);
const CLIMB_ELBOW = new THREE.Vector3(1, -1, -1);
const HANGING_ELBOW = new THREE.Vector3(0, 1, 0);
const HOMIE_FLING = {y: -15, z: -10, bend: 15};
const HANG_REACH = 0.97;
const CHIN_ELBOW = new THREE.Vector3(...THINK_ELBOW);
const LANDED = 0.24;
const TUCK = 0.1;
const HOP_RISE = 6.04;
const HOP_FALL = 10.36;
const HOP_REACH = 2.4;
const SQUIRE_CHARGE = 0.52;
const COACH_JOG = 0.42;
const COLLEAGUE_STROLL = 0.6;
const SIP_LIFT = 70;
const SIP_FORWARD = 45;
const SIP_TIP = -25;
const SQUIRE_SHIELD = {y: 60, z: -10, bend: 15};
// how far a shield hanging at the side is turned from facing forward, so it is carried edge on, its face to the side
const SHIELD_TURN = 60;
// and how far it is rolled in its own plane, so its point hangs straight down
const SHIELD_ROLL = 45;
const SQUIRE_QUILL = {y: 30, z: -25, bend: 10};
const COACH_POINT = {y: 0, z: -15, bend: 0};

// an arm taken from hanging at rest (k 0) toward a shape of its own (k 1): the upper arm's turn from the T about y, then x, then z, and the elbow's bend
function armTo(pose, side, k, {y = HANG, x = 0, z = 0, bend = 10}) {
    const sign = SIDES[side];
    pose.turn(`upper_arm_${side}`, {y: sign * mix(HANG, y, k)});
    pose.turn(`upper_arm_${side}`, {x: x * k});
    pose.turn(`upper_arm_${side}`, {z: sign * z * k});
    pose.bend(`forearm_${side}`, mix(10, bend, k));
}

// the hand carried from hanging (k 0) up through the front to `target` (k 1), the elbow pointing the way `elbow` says; it stays there while the body moves
function handTo(pose, side, k, target, elbow) {
    const shoulder = pose.head(`upper_arm_${side}`, pose.standing(`upper_arm_${side}`));
    const toTarget = target.clone().sub(shoulder);
    const hanging = new THREE.Vector3(SIDES[side] * Math.cos(radians(HANG)), 0, -Math.sin(radians(HANG)));
    const way = hanging.lerp(toTarget.clone().normalize(), k).normalize();
    pose.reach(side, shoulder.clone().add(way.multiplyScalar(mix(HANG_REACH, toTarget.length(), k))), HANGING_ELBOW.clone().lerp(elbow, k));
}

const chin = (side) => new THREE.Vector3(SIDES[side] * CHIN_REST[0], CHIN_REST[1], CHIN_REST[2]);

// the legs folded so the feet stand `depth` nearer the hips, flat on whatever they stand on
function fold(pose, depth) {
    for (const side of Object.keys(SIDES)) stepLeg(pose, side, 0, 0, -depth);
}

// whatever a hand holds level rides on after the body has stopped: it pitches and rolls, and rings out by the end of `s`
function slosh(pose, stance, s) {
    [...stance.level].sort().forEach((side, index) => {
        const lag = Math.max(s - 0.05 * index, 0);
        pose.turn(`hand_${side}`, {x: PLATE_PITCH * ringing(lag, 3, 2.5), y: SIDES[side] * PLATE_ROLL * ringing(lag, 2.5, 3)});
    });
}

// how hard the whistle is blown at u: a short blast at each of `blasts`
const blowing = (u, blasts) => blasts.reduce((sum, at) => sum + swell(u, at, at + 0.05), 0);

const heldUp = (stance) => [...stance.carried].filter((side) => !stance.busy.has(side));

function butler_enter(pose, stance, u) {
    const brake = swell(u, BUTLER_SPRINT, BUTLER_SPRINT + 0.22);
    const facing = arrive(pose, stance, u, BUTLER_SPRINT, BUTLER_SPRINT + 0.14, {
        running: true,
        lean: 15,
        drop: 0.12 * brake,
        bend: {lean: -7 * brake, nod: 5 * brake},
    });
    slosh(pose, stance, span(u, BUTLER_SPRINT, 1));
    pose.revolve(facing);
}

function butler_exit(pose, stance, u) {
    const bow = swell(u, 0, BUTLER_BOW);
    pose.revolve(depart(pose, stance, u, BUTLER_BOW, -1, {bend: {lean: 30 * bow, nod: 24 * bow}}));
}

// the homie climbs up from behind the box: his head shows first, his hands slap onto the edge, he pulls up and springs onto it
function homie_enter(pose, stance, u) {
    const spring = span(u, 0.55, 0.72);
    const landed = u < 0.72 ? 0 : LANDED * (1 - rise(u, 0.84, 1));
    const height =
        u < 0.55
            ? mix(-4.4, CLIMB_PEEK, rise(u, 0, 0.16)) + (CLIMB_PULLED - CLIMB_PEEK) * rise(u, 0.3, 0.55)
            : u < 0.72
              ? mix(CLIMB_PULLED, -LANDED, spring) + 1.2 * Math.sin(Math.PI * spring)
              : -landed;
    pose.lift("root", {z: height});
    breathe(pose, 0);
    trunk(pose, {
        turn: 25 * Math.sin(2 * Math.PI * span(u, 0.06, 0.2)),
        lean: 14 * (landed / LANDED) + 8 * rise(u, 0.3, 0.55) * (1 - spring),
        nod: -10 * swell(u, 0.86, 1),
    });
    const grip = u >= 0.2 && u < 0.55 ? rise(u, 0.2, 0.27) : 0;
    const fling = swell(u, 0.55, 0.74);
    armsAtRest(pose, stance, grip || fling ? Object.keys(SIDES) : []);
    for (const side of Object.keys(SIDES)) {
        if (grip) {
            handTo(pose, side, grip, new THREE.Vector3(SIDES[side] * CLIMB_GRIP.x, CLIMB_GRIP.y, CLIMB_GRIP.z), CLIMB_ELBOW);
            pose.face(`hand_${side}`, {z: -SIDES[side] * 90 * grip});
        } else if (fling) {
            armTo(pose, side, fling, HOMIE_FLING);
        }
    }
    fold(pose, u < 0.72 ? mix(0, LANDED, spring) + TUCK * Math.sin(Math.PI * spring) : landed);
}

// the homie springs off the box and drops out of sight below its edge, arms up all the way down
function homie_exit(pose, stance, u) {
    const flight = span(u, 0.3, 1);
    const ready = rise(u, 0.05, 0.3);
    const up = rise(u, 0.3, 0.42);
    pose.lift("root", {y: -HOP_REACH * flight, z: u < 0.3 ? -LANDED * ready : -LANDED + HOP_RISE * flight - HOP_FALL * flight * flight});
    breathe(pose, 0);
    trunk(pose, {lean: 15 * ready * (1 - up), nod: 18 * ready * (1 - up)});
    for (const side of Object.keys(SIDES)) {
        armTo(pose, side, ready, {y: mix(HANG, -15, up), x: mix(40, 0, up), z: -10 * up, bend: 10});
    }
    fold(pose, u < 0.3 ? LANDED * ready : LANDED * (1 - up) + 2 * TUCK * swell(u, 0.36, 0.62));
    pose.revolve(-35 * rise(u, 0, 0.2));
}

// the squire charges in, shield up and quill held aloft like a sword, skids to a stop and lowers both
function squire_enter(pose, stance, u) {
    const shield = [...stance.busy];
    const quill = heldUp(stance);
    const charge = 1 - rise(u, 0.7, 0.92);
    const skid = swell(u, SQUIRE_CHARGE, SQUIRE_CHARGE + 0.2);
    const facing = arrive(pose, stance, u, SQUIRE_CHARGE, SQUIRE_CHARGE + 0.14, {
        running: true,
        lean: 14,
        apart: [...shield, ...quill],
        drop: 0.14 * skid,
        bend: {lean: -6 * skid},
    });
    shield.forEach((side) => armTo(pose, side, charge, SQUIRE_SHIELD));
    quill.forEach((side) => armTo(pose, side, charge, SQUIRE_QUILL));
    pose.shutEyes(1 - 0.45 * charge);
    pose.revolve(facing);
}

// the squire salutes with the quill before his face, turns and marches off
function squire_exit(pose, stance, u) {
    const quill = heldUp(stance);
    const salute = rise(u, 0, 0.12) * (1 - rise(u, 0.24, 0.34));
    const facing = depart(pose, stance, u, 0.34, -1, {
        clearance: 0.18,
        lean: 0,
        apart: salute ? quill : [],
        bend: {nod: 10 * swell(u, 0.1, 0.26)},
    });
    if (salute) quill.forEach((side) => handTo(pose, side, salute, chin(side), CHIN_ELBOW));
    pose.revolve(facing);
}

// the coach jogs in, jogs on the spot a few steps, then stops and blows the whistle twice
function coach_enter(pose, stance, u) {
    const side = freeSide(stance);
    const jog = rise(u, COACH_JOG, COACH_JOG + 0.04) * (1 - rise(u, 0.62, 0.7));
    const cycle = 6 * span(u, COACH_JOG, 0.7);
    const bob = -0.05 * jog * Math.abs(waveOf(cycle));
    const whistling = rise(u, 0.7, 0.76) * (1 - rise(u, 0.9, 0.98));
    const blast = blowing(u, [0.77, 0.83]);
    pose.lift("root", {z: bob});
    const facing = arrive(pose, stance, u, COACH_JOG, COACH_JOG + 0.1, {
        running: true,
        lean: 6,
        apart: whistling ? [side] : [],
        bend: {nod: 7 * blast, lean: 2 * blast},
    });
    if (whistling) handTo(pose, side, whistling, chin(side), CHIN_ELBOW);
    if (jog) {
        for (const [leg, offset] of [
            ["l", 0],
            ["r", 0.5],
        ])
            stepLeg(pose, leg, 0, 0.22 * jog * Math.max(waveOf(cycle + offset), 0), bob);
    }
    pose.shutEyes(1 - 0.6 * blast);
    pose.revolve(facing);
}

// the coach blows the whistle, points the way with the free hand and jogs off that way
function coach_exit(pose, stance, u) {
    const side = freeSide(stance);
    const whistling = rise(u, 0, 0.06) * (1 - rise(u, 0.2, 0.26));
    const pointing = rise(u, 0.26, 0.32) * (1 - rise(u, 0.42, 0.5));
    const blast = blowing(u, [0.07, 0.13]);
    const facing = depart(pose, stance, u, 0.4, SIDES[side], {
        running: true,
        lean: 6,
        apart: whistling || pointing ? [side] : [],
        bend: {nod: 7 * blast, lean: 2 * blast},
    });
    if (whistling) handTo(pose, side, whistling, chin(side), CHIN_ELBOW);
    if (pointing) armTo(pose, side, pointing, COACH_POINT);
    pose.shutEyes(1 - 0.6 * blast);
    pose.revolve(facing);
}

// the colleague strolls in with the mug, stops, and takes a sip
function colleague_enter(pose, stance, u) {
    const lifted = rise(u, 0.72, 0.8) * (1 - rise(u, 0.9, 0.98));
    const tipped = swell(u, 0.78, 0.92);
    const level = [...stance.level].sort();
    const facing = arrive(pose, stance, u, COLLEAGUE_STROLL, COLLEAGUE_STROLL + 0.12, {
        apart: lifted ? level : [],
        bend: {nod: -8 * tipped},
    });
    if (lifted) sipMotion(pose, stance, lifted, tipped);
    pose.shutEyes(1 - 0.7 * tipped);
    pose.revolve(facing);
}

// the colleague gives a small wave with the free hand, turns and strolls off that way
function colleague_exit(pose, stance, u) {
    const side = freeSide(stance);
    const waving = rise(u, 0, 0.08) * (1 - rise(u, 0.24, 0.32));
    const facing = depart(pose, stance, u, 0.3, SIDES[side], {apart: waving ? [side] : [], bend: {tilt: -SIDES[side] * 5 * waving}});
    if (waving)
        armTo(pose, side, waving, {y: 0, x: -RAISED_ROLL, z: WAVE_BACK, bend: WAVE_BEND + WAVE_SWING * waveOf(span(u, 0, 0.32), 2)});
    pose.revolve(facing);
}

// the bare robot, with no manner of its own, walks in and turns to the viewer, and walks off
function bare_enter(pose, stance, u) {
    pose.revolve(arrive(pose, stance, u, ENTRY_TRAVEL_END, ENTRY_TURN_END));
}

function bare_exit(pose, stance, u) {
    pose.revolve(depart(pose, stance, u, 0, -1));
}

const ENTRANCES = {
    bare: bare_enter,
    butler: butler_enter,
    homie: homie_enter,
    squire: squire_enter,
    coach: coach_enter,
    colleague: colleague_enter,
};
const EXITS = {bare: bare_exit, butler: butler_exit, homie: homie_exit, squire: squire_exit, coach: coach_exit, colleague: colleague_exit};

function enter(pose, stance, t) {
    ENTRANCES[stance.voice](pose, stance, onceTime(t, ENTER_FRAMES));
}

function exit(pose, stance, t) {
    EXITS[stance.voice](pose, stance, onceTime(t, EXIT_FRAMES));
}

// What the figure does while the agent works, and the moments it marks; each pose starts and ends on idle's first frame unless it loops
const SEARCH_CROUCH = 0.2;
const CHASE_REACH = 1.4;
const TAP_LIFT = 0.13;

// where the glance is across one slow search cycle: one way, a pause, the other way, a pause, back to centre, a longer rest
function glanceOf(t) {
    return rise(t, 0, 0.22) - 2 * rise(t, 0.32, 0.62) + rise(t, 0.7, 0.85);
}

// rummages through a pile in front of it with the free hand, looking down and slowly from side to side
function search(pose, stance, t) {
    const side = freeSide(stance);
    const sweep = glanceOf(t);
    crouch(pose, SEARCH_CROUCH);
    breathe(pose, 0);
    trunk(pose, {lean: 26, nod: 20, turn: -SIDES[side] * 28 * sweep, twist: -SIDES[side] * 10 * sweep});
    armsAtRest(pose, stance, [side]);
    armTo(pose, side, 1, {y: 30, z: -60 + 25 * sweep, bend: 80});
    pose.holdUpright("magnifying_glass", side, [0, 0, 0], {x: GLASS_LEAN});
    eyesAs(pose, "reading");
}

const READING = {
    intro: 12,
    hold: 48,
    outro: 12,
    fps: 12,
    ready: 3,
    opens: 11,
    pageEvery: 24,
    pageFrom: 12,
    pageTo: 20,
    nod: 12,
    lineNod: 0.8,
    scan: 3,
    lines: 4,
    referenceArm: 0.985,
    forward: 0.68,
    drop: 0.3,
    drawDrop: 0.18,
    elbow: [1, -1, -1],
    wristTurn: 90,
};
const READ_FRAMES = READING.intro + READING.hold + READING.outro;

export const HAND = {grip: 0.34, forward: 0.02};
export const ACTING = {
    intro: 8, hold: 32, outro: 8, fps: 12,
    yawnFrames: 28, pastimeFrames: 40, greetingFrames: 24,
    hopFrames: 20, stumbleFrames: 24,
    elbow: [1, -0.15, -0.35],
    wrist: [0.72, -0.72, 1.76],
    supportLift: 0.22, whistleLift: 0.25, clothLift: 0.2, clothTurn: -90, compactFps: 6,
    tap: 10, rock: 3, turn: 12, nod: 8,
    writeStroke: 0.035, writeHeight: 0.02,
    glance: 22, hop: 0.18, stumble: 12,
    writingWrist: [0.38, -0.76, 2.1],
    yawnWrist: [0.48, -0.86, 2.12], whistleWrist: [0.48, -0.82, 2.2],
    sipWrist: [0.7, -0.63, 2.17], shieldWrist: [0.22, -0.64, 2.13],
    wipeWrist: [0.1, -0.7, 1.9], saluteWrist: [1.28, -0.32, 2.59],
    gestureIn: 0.2, gestureOut: 0.8,
    yawnEyes: 0.94, yawnSpan: [0.08, 0.92],
    pastimeSpan: [0.3, 0.7], whistleEyes: 0.65, sipEyes: 0.5, sipTip: 12,
    headphoneEyes: 0.4, beats: 4, sways: 2, wipes: 3, wipeLift: 0.035,
    wipeAcross: 0.04, bowLean: 18, bowNod: 10,
    leapSpan: [0.18, 0.78], catchSpan: [0.15, 0.45], recoverSpan: [0.45, 0.85], recover: 0.3,
};
export const WRITING = {butler: "writing_stylus", coach: "writing_pencil", colleague: "writing_pen", homie: "writing_marker", squire: "writing_quill"};
const HELD_FRAMES = ACTING.intro + ACTING.hold + ACTING.outro;
// The wait, one long round: the figure turned toward the compose box, tapping its foot, and toward the end a while of whistling idly.
// Spans are shares of the held part.
export const WAIT = {intro: 8, hold: 144, outro: 8, whistleSpan: [0.7, 0.98], beats: 12, sways: 3};
const WAIT_FRAMES = WAIT.intro + WAIT.hold + WAIT.outro;
const READ_GAZE = {across: 0.04, top: 0.52, bottom: 0.44, forward: [0, -1, 0]};

function heldTime(t) {
    const frame = t * HELD_FRAMES;
    const held = frame >= ACTING.intro && frame < ACTING.intro + ACTING.hold;
    const draw = frame < ACTING.intro ? frame : HELD_FRAMES - 1 - frame;
    return {frame, held, ready: held ? 1 : rise(draw, 0, ACTING.intro - 1), phase: held ? (frame - ACTING.intro) / ACTING.hold : 0};
}

function waitTime(t) {
    const frame = t * WAIT_FRAMES;
    const held = frame >= WAIT.intro && frame < WAIT.intro + WAIT.hold;
    const draw = frame < WAIT.intro ? frame : WAIT_FRAMES - 1 - frame;
    return {ready: held ? 1 : rise(draw, 0, WAIT.intro - 1), phase: held ? (frame - WAIT.intro) / WAIT.hold : 0};
}

function gestureTime(t, frames) {
    const u = onceTime(t, frames);
    return {u, ready: rise(u, 0, ACTING.gestureIn) * (1 - rise(u, ACTING.gestureOut, 1))};
}

function handGrip(pose, side, offset = [0, 0, 0]) {
    return pose.rig.heads.get(`hand_${side}`).clone()
        .add(new THREE.Vector3(SIDES[side] * (HAND.grip + offset[0]), HAND.forward + offset[1], offset[2]))
        .applyMatrix4(pose.matrix(`hand_${side}`));
}

function propHand(pose, side, ready, target, turn = {}) {
    if (!ready) return;
    handTo(pose, side, ready, pose.carried(new THREE.Vector3(SIDES[side] * target[0], target[1], target[2])), new THREE.Vector3(...ACTING.elbow));
    pose.face(`hand_${side}`, {z: -SIDES[side] * 90 * ready, ...turn});
}

// the most the head turns from the way the body faces, either side, in degrees; a look further round turns the body the rest of the way
export const HEAD_TURN = 65;

// The head turned to look at `target`, `amount` of the way, never further round than HEAD_TURN from the body: it returns how many degrees
// further round the look is, which the body turns
function eyesToward(pose, target, amount = 1) {
    const centre = pose.rig.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(pose.rig.eyes.length);
    const pivot = pose.head("head", pose.standing("head"));
    const way = target.clone().sub(pivot);
    const above = centre.z - pose.rig.heads.get("head").z;
    const pitch = Math.asin(THREE.MathUtils.clamp(above / way.length(), -1, 1)) - Math.atan2(way.z, Math.hypot(way.x, way.y));
    const yaw = THREE.MathUtils.radToDeg(Math.atan2(way.x, -way.y));
    const turned = THREE.MathUtils.clamp(yaw, -HEAD_TURN, HEAD_TURN);
    pose.face("head", {x: THREE.MathUtils.radToDeg(pitch) * amount, z: turned * amount});
    pose.gaze = {target: target.toArray(), forward: READ_GAZE.forward};
    return (yaw - turned) * amount;
}


function read(pose, stance, t) {
    const frame = t * READ_FRAMES;
    const held = frame >= READING.intro && frame < READING.intro + READING.hold;
    const taking = frame < READING.intro ? frame : READ_FRAMES - 1 - frame;
    const ready = held ? 1 : rise(taking, 0, READING.ready);
    const open = held ? 1 : rise(taking, READING.ready, READING.opens);
    const phase = held ? (frame - READING.intro) % READING.pageEvery : 0;
    const page = held ? rise(phase, READING.pageFrom, READING.pageTo) : 0;
    const scan = held ? (frame - READING.intro) / READING.hold : 0;
    breathe(pose, 0);

    armsAtRest(pose, stance);
    const scale = Math.min(...Object.keys(SIDES).map((side) => {
        const at = (name) => pose.rig.heads.get(`${name}_${side}`);
        return at("upper_arm").distanceTo(at("forearm")) + at("forearm").distanceTo(at("hand"));
    })) / READING.referenceArm;
    const shoulders = Object.keys(SIDES).map((side) => pose.head(`upper_arm_${side}`, pose.standing(`upper_arm_${side}`)));
    const middle = shoulders[0].clone().add(shoulders[1]).multiplyScalar(0.5);
    const turn = bookTurn(open);
    const grip = bookGrip("l", open).add(bookGrip("r", open)).multiplyScalar(0.5).applyMatrix4(turn);
    const at = new THREE.Vector3(middle.x - grip.x * scale, middle.z - (READING.drop + READING.drawDrop * (1 - ready)) * scale - grip.y * scale, -middle.y + READING.forward * scale - grip.z * scale);
    const matrix = new THREE.Matrix4().makeTranslation(at.x, at.y, at.z)
        .multiply(turn)
        .scale(new THREE.Vector3(scale, scale, scale));
    for (const [side, sign] of Object.entries(SIDES)) {
        const target = toBlender(bookGrip(side, open).applyMatrix4(matrix));
        if (!ready) continue;
        handTo(pose, side, ready, target, new THREE.Vector3(...READING.elbow));
        const inward = THREE.MathUtils.radToDeg(Math.atan2(BOOK.closedGrip * (1 - open), BOOK.gripBack));
        pose.face(`hand_${side}`, {z: -sign * (READING.wristTurn + inward) * ready});
    }
    const line = Math.floor(phase / (READING.pageEvery / READING.lines));
    const along = (phase % (READING.pageEvery / READING.lines)) / (READING.pageEvery / READING.lines - 1);
    const target = new THREE.Vector3(mix(-READ_GAZE.across, READ_GAZE.across, along), mix(READ_GAZE.top, READ_GAZE.bottom, line / (READING.lines - 1)), -BOOK.pages).applyMatrix4(matrix);
    eyesToward(pose, toBlender(target), open);
    pose.holdBook(open, page, held || taking >= READING.ready);
    eyesAs(pose, "reading", open);
}

// The butler draws his cloth from his pocket, polishes his visor in small circles, and tucks it away again
const POCKET = [0.55, -0.35, 1.35];
const POLISHED = [0.65, -0.92, 2.04];
const POLISH_ELBOW = [0.7, 0.2, -1.0];
const POLISH_RUB = 0.06;
function polish(pose, stance, t) {
    breathe(pose, t);
    const sides = [...stance.cloth];
    armsAtRest(pose, stance, sides);
    const up = rise(t, 0.15, 0.3) * (1 - rise(t, 0.75, 0.9));
    const out = rise(t, 0.08, 0.15) * (1 - rise(t, 0.88, 0.95));
    const rub = rise(t, 0.3, 0.35) * (1 - rise(t, 0.7, 0.75));
    trunk(pose, {nod: 6 * up, tilt: 4 * rub * Math.sin(2 * Math.PI * 3 * t)});
    for (const side of sides) {
        const sign = SIDES[side];
        const circle = 2 * Math.PI * 4 * t;
        const at = POCKET.map((p, axis) => p + (POLISHED[axis] - p) * up);
        const target = new THREE.Vector3(sign * (at[0] + POLISH_RUB * rub * Math.cos(circle)), at[1], at[2] + POLISH_RUB * rub * Math.sin(circle));
        handTo(pose, side, out, pose.carried(target), new THREE.Vector3(sign * POLISH_ELBOW[0], POLISH_ELBOW[1], POLISH_ELBOW[2]));
        pose.face(`hand_${side}`, {z: -sign * 90 * out});
        if (out > 0.5) pose.holdCloth();
    }
    eyesAs(pose, rub > 0.5 ? "amused" : "reading");
}

// The figure waits turned toward the compose box, tapping its foot, its arms hanging as they do standing idle, and whistles idly, swaying,
// toward the end of the round; the butler sways only while he whistles.
function waiting(pose, stance, t) {
    const {ready, phase} = waitTime(t);
    const butler = stance.voice === "butler";
    const tune = swell(phase, ...WAIT.whistleSpan) * ready;
    breathe(pose, 0);
    trunk(pose, {turn: ACTING.turn * ready, nod: -ACTING.nod * tune / 2, lean: ACTING.rock * waveOf(phase, WAIT.sways) * (butler ? tune : ready)});
    armsAtRest(pose, stance);
    pose.tap = ACTING.tap * Math.max(waveOf(phase, WAIT.beats), 0) * ready;
    if (pose.posture === "stand") pose.turn("foot_r", {x: pose.tap});
    if (tune) pose.shutEyes(1 - ACTING.whistleEyes * tune);
}

function yawn(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.yawnFrames);
    const side = freeSide(stance);
    breathe(pose, 0);
    trunk(pose, {lean: -ACTING.rock * ready, nod: -ACTING.nod * ready});
    armsAtRest(pose, stance);
    propHand(pose, side, ready, ACTING.yawnWrist);
    if (ready) pose.putAway(...IN_HAND);
    pose.shutEyes(1 - ACTING.yawnEyes * swell(u, ...ACTING.yawnSpan));
}

function whistle(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.pastimeFrames);
    const blast = swell(u, ...ACTING.pastimeSpan);
    const side = freeSide(stance);
    breathe(pose, 0);
    trunk(pose, {lean: -ACTING.rock * blast, nod: -ACTING.nod * blast});
    armsAtRest(pose, stance);
    propHand(pose, side, ready, ACTING.whistleWrist);
    if (ready) pose.putAway(...IN_HAND, "coach_whistle");
    if (ready > 0.5) pose.holdProp("hand_whistle", side, [0, 0, ACTING.whistleLift], {z: SIDES[side] * 90});
    pose.shutEyes(1 - ACTING.whistleEyes * blast);
}

// The figure lies down on its back on the floor it stands on, its hands behind its head and a straw in its mouth, its near foot crossed over
// the other knee, whistling now and then with the crossed foot bobbing to the tune, and gets up again. Shares of the clip: lying down over
// `down`, getting up over `up`, and whistling in each of `tunes`. The back of the head rests on the hands at `pillow`, tipped `tilt` degrees
// back from upright, the head turned `glance` degrees toward the viewer so the eyes are seen, and the head laid `across` from where the
// figure stood, so the body lies in the middle of the picture.
export const REST = {
    frames: 120, fps: 8,
    down: [0, 0.1], up: [0.9, 1], tunes: [[0.3, 0.45], [0.62, 0.8]], beats: 40,
    pillow: [0, 1.0, 3.2], tilt: 72, across: -1.6,
    kneeUp: 60, kneeBend: 105, glance: 40, ankle: [-0.15, -0.15, -0.1], crossedKnee: [1, -0.4, 0.6], footBob: 18,
    wrist: [0.6, 0.55, 2.85], fingers: [-1, 0.4, 0.4], elbow: [1, -0.3, 0.8],
    straw: [0.14, -0.9, 0.4], strawTip: 115, strawWag: 8, eyes: 0.45, whistleEyes: 0.2,
};

// how far into a tune the clip is at u: a swell over each of REST.tunes, 0 between them
const tuneOf = (u) => REST.tunes.reduce((sum, [from, to]) => sum + swell(u, from, to), 0);

function rest(pose, stance, t) {
    const u = onceTime(t, REST.frames);
    const lying = rise(u, ...REST.down) * (1 - rise(u, ...REST.up));
    const tune = tuneOf(u);
    const tap = Math.max(waveOf(u, REST.beats), 0);
    breathe(pose, 0);
    armsAtRest(pose, stance, lying ? Object.keys(SIDES) : []);
    if (!lying) return;
    pose.putAway(...IN_HAND);
    trunk(pose, {turn: -REST.glance * lying});
    for (const [side, sign] of Object.entries(SIDES)) {
        const [x, y, z] = REST.wrist;
        handTo(pose, side, lying, new THREE.Vector3(sign * x, y, z), new THREE.Vector3(...REST.elbow));
        const [across, forward, up] = REST.fingers;
        pose.aim(`hand_${side}`, new THREE.Vector3(sign * across, forward, up));
    }
    pose.turn("thigh_l", {x: -REST.kneeUp * lying});
    pose.bend("shin_l", REST.kneeBend * lying);
    const knee = pose.head("shin_l", pose.matrix("shin_l"));
    const resting = pose.head("foot_r", pose.standing("foot_r"));
    pose.step("r", resting.lerp(knee.add(new THREE.Vector3(...REST.ankle)), lying), new THREE.Vector3(...REST.crossedKnee));
    pose.turn("foot_r", {x: -REST.footBob * tune * tap});
    pose.wearProp("straw", REST.straw, {x: REST.strawTip + REST.strawWag * (1 + tune) * waveOf(u, 9)});
    const pillow = new THREE.Vector3(...REST.pillow);
    pose.turnAll({x: -REST.tilt * lying}, pillow);
    pose.turnAll({z: 90 * lying}, pillow);
    pose.shiftAll([REST.across * lying, -pillow.y * lying, -pillow.z * lying]);
    pose.shutEyes(mix(1, mix(REST.eyes, REST.whistleEyes, tune), lying));
}

function sipMotion(pose, stance, ready, tipped) {
    for (const side of stance.level) {
        propHand(pose, side, ready, ACTING.sipWrist, {x: -ACTING.sipTip * tipped});
    }
}

function sip(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.pastimeFrames);
    breathe(pose, 0);
    trunk(pose, {nod: -ACTING.rock * ready});
    armsAtRest(pose, stance);
    sipMotion(pose, stance, ready, swell(u, ...ACTING.pastimeSpan));
    pose.shutEyes(1 - ACTING.sipEyes * swell(u, ...ACTING.pastimeSpan));
}

function headphones(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.pastimeFrames);
    breathe(pose, 0);
    trunk(pose, {nod: ACTING.nod * waveOf(u, ACTING.beats) * ready, tilt: ACTING.rock * waveOf(u, ACTING.sways) * ready});
    armsAtRest(pose, stance);
    pose.swing(waveOf(u, ACTING.sways) * ready);
    pose.shutEyes(1 - ACTING.headphoneEyes * ready);
}

function shieldPolish(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.pastimeFrames);
    const shield = [...stance.shield][0];
    if (!shield) return idle(pose, stance, t);
    const cloth = shield === "l" ? "r" : "l";
    breathe(pose, 0);
    trunk(pose, {nod: ACTING.nod * ready});
    armsAtRest(pose, stance);
    propHand(pose, shield, ready, ACTING.shieldWrist);
    propHand(pose, cloth, ready, [ACTING.wipeWrist[0], ACTING.wipeWrist[1] + ACTING.wipeAcross * waveOf(u, ACTING.wipes), ACTING.wipeWrist[2] + ACTING.wipeLift * waveOf(u, ACTING.wipes * 2)]);
    if (ready) {
        pose.putAway("squire_quill");
        pose.keep.add("squire_shield");
    }
    if (ready > 0.5) pose.holdProp("polishing_cloth", cloth, [0, 0, ACTING.clothLift], {x: ACTING.clothTurn});
}

function writing(pose, stance, t) {
    const {ready, phase} = heldTime(t);
    const stroke = ACTING.writeStroke * waveOf(phase, ACTING.beats);
    breathe(pose, 0);
    trunk(pose, {nod: ACTING.nod * ready, lean: ACTING.rock * ready});
    armsAtRest(pose, stance);
    propHand(pose, "l", ready, ACTING.wrist);
    propHand(pose, "r", ready, [ACTING.writingWrist[0] + stroke, ACTING.writingWrist[1], ACTING.writingWrist[2]]);
    if (ready) pose.putAway(...IN_HAND);
    if (ready >= 1) {
        const tablet = stance.voice === "butler";
        const surface = TOOLS.paper.thickness * (tablet ? 2.5 : 0.5);
        const tipLift = ACTING.wrist[2] + ACTING.supportLift + surface + TOOLS.pen.length / 2 + TOOLS.pen.tip - ACTING.writingWrist[2];
        pose.holdProp(WRITING[stance.voice] || "writing_pen", "r", [0, 0, tipLift], {z: -90});
        pose.holdProp(stance.voice === "butler" ? "writing_tablet" : "writing_paper", "l", [0, -ACTING.wrist[0], ACTING.supportLift], {z: 90});
    }
    eyesAs(pose, "reading", ready);
}

function compacting(pose, stance, t) {
    const {ready, phase} = heldTime(t);
    breathe(pose, 0);
    trunk(pose, {nod: ACTING.nod * ready});
    armsAtRest(pose, stance);
    propHand(pose, "l", ready, ACTING.wrist);
    propHand(pose, "r", ready, [ACTING.wrist[0] + ACTING.writeStroke * waveOf(phase, ACTING.sways), ACTING.wrist[1], ACTING.wrist[2] + ACTING.writeHeight * Math.max(waveOf(phase, ACTING.sways), 0)]);
    if (ready) pose.putAway(...IN_HAND);
    if (ready >= 1) {
        pose.holdProp("papers", "l", [0, -ACTING.wrist[0], ACTING.supportLift], {z: 90});
        pose.props.get("papers").phase = phase;
    }
}

function bow(pose, stance, t) {
    const {ready} = gestureTime(t, ACTING.greetingFrames);
    breathe(pose, 0);
    trunk(pose, {lean: ACTING.bowLean * ready, nod: ACTING.bowNod * ready});
    armsAtRest(pose, stance);
    if (ready) pose.putAway(...IN_HAND);
}

function salute(pose, stance, t) {
    const {ready} = gestureTime(t, ACTING.greetingFrames);
    const side = freeSide(stance);
    breathe(pose, 0);
    trunk(pose, {nod: -ACTING.rock * ready});
    armsAtRest(pose, stance);
    propHand(pose, side, ready, ACTING.saluteWrist);
    if (ready) pose.putAway(...IN_HAND);
}

function startled(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.hopFrames);
    const leap = swell(u, ...ACTING.leapSpan);
    crouch(pose, ACTING.hop * swell(u, 0, ACTING.leapSpan[0]));
    pose.lift("root", {z: ACTING.hop * leap});
    breathe(pose, 0);
    trunk(pose, {lean: -ACTING.rock * leap});
    flung(pose, stance, 0, ARM_CLEAR_RAISE * leap);
    if (pose.posture === "stand") tucked(pose, leap);
    eyesAs(pose, "startled", ready);
}

function stumble(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.stumbleFrames);
    const catchStep = swell(u, ...ACTING.catchSpan) - ACTING.recover * swell(u, ...ACTING.recoverSpan);
    breathe(pose, 0);
    trunk(pose, {lean: ACTING.stumble * catchStep, tilt: ACTING.rock * catchStep});
    flung(pose, stance, 0, ARM_CLEAR_RAISE * ready);
    eyesAs(pose, "startled", Math.max(catchStep, 0));
}

function glance(pose, stance, t) {
    const {ready} = gestureTime(t, ACTING.greetingFrames);
    breathe(pose, 0);
    trunk(pose, {turn: ACTING.glance * ready, nod: -ACTING.rock * ready});
    armsAtRest(pose, stance);
}

// a figure that has a tablet tips it up toward its face in the hand holding it, and touches it with the free hand, `stroke` off the
// spot it touches
function onTablet(pose, stance, side, stroke) {
    for (const held of stance.tablet) {
        const sign = SIDES[held];
        pose.face(`hand_${held}`, {x: TABLET_TIP, z: -sign * HOLD_TWIST});
        const touch = TABLET_TOUCH.map((at, axis) => at + stroke[axis]);
        const spot = pose.head(`hand_${held}`, pose.matrix(`hand_${held}`)).add(new THREE.Vector3(sign * touch[0], touch[1], touch[2]));
        pose.reach(side, spot, new THREE.Vector3(-sign * THINK_ELBOW[0], THINK_ELBOW[1], THINK_ELBOW[2]));
        pose.holdTablet();
    }
}

// One blow of `blowFrames` frames a loop, so the hammering can stop after any blow; how long it goes on for each parcel the page decides
// (figure/parcels.js HAMMER). Each blow comes down quick,
// gathering speed, lands `lands` of the way through, and lifts back slower, easing up; the wrist snaps the hammer's head `snap` degrees
// down into the blow. The forearm is turned `roll` degrees so the thumb is on top, the hand closed round the handle near its end, its
// fingers curled in to `fist` of the open hand's length, and the handle turned `thumb` degrees to run across the palm through the fist,
// the head out beyond the thumb. The swing stops dead `strike` of the way up from its lowest, where the hammer's head comes to rest on the
// parcel's top (parcels.js PARCEL height at the chat's 112-pixel picture), so no blow passes into it. On its feet the figure turns side-on, `turn` degrees, its face in profile toward the parcel the blow lands on,
// `landsAt` from its feet at rest across and forward; the parcel stands on the page, not in the picture, so it never turns with the figure.
export const WORK = {blows: 1, blowFrames: 8, fps: 10, lands: 0.3, snap: 50, thumb: 90, roll: -90, fist: 0.62, turn: 80, strike: 0.413, landsAt: [0.72, -1.81]};

function blowOf(t) {
    const phase = (t * WORK.blows) % 1;
    return phase < WORK.lands ? 1 - (phase / WORK.lands) ** 2 : ease(span(phase, WORK.lands, 1));
}

// Where the blows land in the picture of a figure of `stance` hammering on its feet, as a share of the picture's width from its middle,
// toward the viewer's right
export function blowsLandAt(stance) {
    const sign = SIDES[freeSide(stance)];
    const [across, forward] = WORK.landsAt;
    const turn = radians(sign * WORK.turn);
    return (sign * across * Math.cos(turn) - forward * Math.sin(turn)) / FRAMED_HEIGHT;
}

// hammers away with a hammer in the free hand, the body dipping into each blow
function work(pose, stance, t) {
    const side = freeSide(stance);
    const raised = Math.max(blowOf(t), WORK.strike);
    const blow = 1 - raised;
    crouch(pose, 0.04 * blow);
    breathe(pose, 0);
    trunk(pose, {lean: 8 + 6 * blow, nod: 10});
    armsAtRest(pose, stance, [side]);
    armTo(pose, side, 1, {y: mix(75, 5, raised), z: -35, bend: mix(15, 70, raised)});
    pose.roll(`forearm_${side}`, SIDES[side] * WORK.roll);
    pose.clench(side, WORK.fist);
    pose.holdProp("work_hammer", side, [0, 0, 0], {x: WORK.thumb, z: SIDES[side] * WORK.snap * blow});
    if (pose.posture === "stand") pose.revolve(SIDES[side] * WORK.turn);
}

// Inspecting the box it hammers (parcels.js INSPECT): side-on to it as it hammers, it takes the magnifying glass out over `out`, bends
// `bend` and leans `lean` degrees in over the box, the glass held out over the box's top at `held` (across, forward, up from the feet,
// before it turns side-on) and tipped down `tip` degrees, sweeping it a little, and puts it away over `away`
export const INSPECTING = {frames: 22, fps: 12, out: [0, 0.18], away: [0.82, 1], bend: 0.28, lean: 30, nod: 24, held: [0.55, -1.2, 1.7], sweep: 0.12, tip: 45};

function inspect(pose, stance, t) {
    const side = freeSide(stance);
    const ready = partOf(t, INSPECTING.out) * (1 - partOf(t, INSPECTING.away));
    const sweep = INSPECTING.sweep * waveOf(span(t, INSPECTING.out[1], INSPECTING.away[0]));
    crouch(pose, INSPECTING.bend * ready);
    breathe(pose, 0);
    trunk(pose, {lean: INSPECTING.lean * ready, nod: INSPECTING.nod * ready});
    armsAtRest(pose, stance, [side]);
    const [x, y, z] = INSPECTING.held;
    handTo(pose, side, ready, pose.withinReach(side, pose.carried(new THREE.Vector3(SIDES[side] * (x + sweep), y, z)), 0.97), new THREE.Vector3(...ACTING.elbow));
    pose.putAway(...IN_HAND);
    if (ready > 0.3) pose.holdUpright("magnifying_glass", side, [0, 0, 0], {x: INSPECTING.tip * ready});
    eyesAs(pose, "reading", ready);
    if (pose.posture === "stand") pose.revolve(SIDES[side] * WORK.turn);
}

// The figure stands still watching something in the sky, as the page says in `pose.sky`, its head turned to it by the look the page gives
// (lookToward): the free hand shading its eyes by `shade`, 0 to 1, as when what it watches is far off, the hand at the side of the visor
// and pointing out over it like a cap's peak; and stepped back by `back`, 0 to 1, with a small hop as it steps, leaning back to look up
export const SKY = {step: 0.6, hop: 0.12, lean: 8, shadeWrist: [1.18, -0.5, 2.72], shadeHand: [-0.35, -1, 0.2]};

// how far in front of the figure what it looks at in its picture is taken to be, or behind it on the page for a look `behind`
const LOOK_DEPTH = -1.2;

// The head turned to look at `at`, a point in the figure's picture as shares of its width from the left and its height from the top, as
// the UFO it watches or the leading edge of a progress bar under its feet, in front of the figure, or `at.behind` it on the page, the
// figure turned `facing` degrees; `at.amount` of the way from
// the head as its clip has it, 0 to 1, as the look eases in and out. It returns how many degrees the body turns for a look further round
// than the head goes, the body following the head as the look eases in, so the head leads.
export function lookToward(pose, at, facing = 0) {
    const point = new THREE.Vector3((at.x - 0.5) * FRAMED_HEIGHT, at.behind ? -LOOK_DEPTH : LOOK_DEPTH, FRAMED_MIDDLE + (0.5 - at.y) * FRAMED_HEIGHT);
    const own = pose.matrix("head").clone();
    const further = eyesToward(pose, point.applyAxisAngle(new THREE.Vector3(0, 0, 1), radians(-facing)));
    const amount = at.amount ?? 1;
    if (amount < 1) pose.final.set("head", between(own, pose.matrix("head"), amount));
    return further * amount * amount;
}

// a bone's move `k` of the way from `from` to `to`, turned and placed part way, as a head easing into or out of a look
function between(from, to, k) {
    const [a, b] = [from, to].map((move) => {
        const parts = {at: new THREE.Vector3(), turn: new THREE.Quaternion(), size: new THREE.Vector3()};
        move.decompose(parts.at, parts.turn, parts.size);
        return parts;
    });
    return new THREE.Matrix4().compose(a.at.lerp(b.at, k), a.turn.slerp(b.turn, k), a.size.lerp(b.size, k));
}

function watch(pose, stance, t) {
    const {shade, back} = pose.sky ?? {shade: 0, back: 0};
    pose.lift("root", {y: SKY.step * back, z: SKY.hop * Math.sin(Math.PI * back)});
    breathe(pose, t);
    trunk(pose, {lean: -SKY.lean * back});
    const side = freeSide(stance);
    armsAtRest(pose, stance, shade ? [side] : []);
    if (shade) {
        propHand(pose, side, shade, SKY.shadeWrist);
        const [across, forward, up] = SKY.shadeHand;
        const hand = `hand_${side}`;
        const now = pose.rig.along.get(hand).clone().transformDirection(pose.matrix(hand));
        pose.aim(hand, now.lerp(new THREE.Vector3(SIDES[side] * across, forward, up), shade));
        pose.putAway(...IN_HAND);
    }
}

// Pushes a parcel along in front of it, which stands far lower than its hands: the knees bent to lower the hips by `drop` and the back
// leaning into the parcel it pushes: the body angled forward, the back `lean` degrees from upright, the knees
// giving by `drop`, the feet stepping `behind` the hips, and both hands out against the parcel's near side at `hands` from where its feet
// stand, about half way up it, its head going with the lean, nodded `nod` degrees further down the way it goes and never turned by a look
// (the clip's `ownLook`). It turns to face the parcel before it leans in: the clip's first `turn` frames it stands upright while it turns, as long as the change of
// facing eases at its pace (places.js CHANGE_SECONDS), and over the rest of its `intro` it leans in; then it pushes, a stride a `stride`
// frames
export const SHOVE = {lean: 60, nod: 4, drop: 0.3, behind: 0.25, hands: [0.4, -0.25, 0.8], turn: 4, intro: 9, stride: 6, fps: 12};

// how far into the lean the push is at `t` of its frames, 0 upright while it turns and 1 leaning in
export function leanOf(t) {
    const frame = t * (SHOVE.intro + SHOVE.stride);
    return frame >= SHOVE.intro ? 1 : ease((frame - SHOVE.turn) / (SHOVE.intro - SHOVE.turn));
}

function push(pose, stance, t) {
    const k = leanOf(t);
    stride(pose, stance, pose.stride, pose.posture === "walk" ? 1 : 0, {lean: 0, drop: SHOVE.drop * k, behind: SHOVE.behind * k, bend: {nod: SHOVE.nod * k}});
    pose.bendAbove("spine", {x: SHOVE.lean * k});
    const [across, forward, up] = SHOVE.hands;
    for (const [side, sign] of Object.entries(SIDES)) {
        handTo(pose, side, k, pose.withinReach(side, new THREE.Vector3(sign * across, forward, up), 0.97), new THREE.Vector3(...ACTING.elbow));
        pose.face(`hand_${side}`, {z: -sign * 90 * k});
    }
    pose.putAway(...IN_HAND);
}

// points up at what waits for the user, looking at it, the arm bobbing a little
function point(pose, stance, t) {
    const side = freeSide(stance);
    breathe(pose, 0);
    trunk(pose, {nod: -14, lean: -3, tilt: -SIDES[side] * 5});
    armsAtRest(pose, stance, [side]);
    armTo(pose, side, 1, {y: -12 + 3 * waveOf(t), z: -15, bend: 10});
    eyesAs(pose, "worried", 0.6);
}

// the arms of a jump or a fall, those that carry nothing: swung back by `back` degrees and out and up by `up` degrees
function flung(pose, stance, back, up, flail = 0) {
    armsAtRest(pose, stance, [...stance.free]);
    for (const side of stance.free) {
        const sign = SIDES[side];
        const amount = Math.min(Math.max(up / ARM_RAISE_SPAN, 0), 1);
        armTo(pose, side, amount, {x: back + flail * sign, y: -Math.min(up, ARM_CLEAR_RAISE), bend: 10});
    }
}

// the legs tucked up under a body in the air, `tuck` from 0 to 1
function tucked(pose, tuck, kick = 0) {
    for (const [side, sign] of Object.entries(SIDES)) {
        pose.turn(`thigh_${side}`, {x: -24 * tuck + kick * sign});
        pose.turn(`shin_${side}`, {x: 44 * tuck});
        pose.turn(`foot_${side}`, {x: -8 * tuck});
    }
}

// a jump up to a perch: crouch with the arms swung back, push off with them swinging up, and leave the ground with the legs tucked
function jump(pose, stance, t) {
    const u = onceTime(t, 16);
    const crouch = rise(u, 0, 0.26) * (1 - rise(u, 0.26, 0.36));
    const air = rise(u, 0.3, 0.45);
    pose.lift("root", {z: 0.1 * air});
    breathe(pose, 0);
    trunk(pose, {lean: 14 * crouch - 6 * air, nod: -4 * air});
    flung(pose, stance, 40 * crouch, 80 * rise(u, 0.26, 0.42) * (1 - 0.4 * rise(u, 0.6, 1)));
    fold(pose, 0.28 * crouch);
    tucked(pose, air);
}

const BACKFLIP_RAISE = 25;
const BACKFLIP_TURN = 360;

// a jump that turns over backwards on the way up a high jump, where the jump carries it: the crouch, then the body tucked and turned all the
// way round about its hips in the air, and landed
function backflip(pose, stance, t) {
    const u = onceTime(t, 22);
    const crouch = rise(u, 0, 0.26) * (1 - rise(u, 0.26, 0.34));
    const turn = rise(u, 0.3, 0.86);
    const air = rise(u, 0.28, 0.4) * (1 - rise(u, 0.86, 0.95));
    pose.lift("root", {z: 0.1 * air});
    breathe(pose, 0);
    trunk(pose, {lean: 12 * crouch});
    flung(pose, stance, 30 * crouch, BACKFLIP_RAISE * air);
    fold(pose, 0.28 * crouch);
    tucked(pose, 1.2 * air);
    pose.turnAll({x: BACKFLIP_TURN * turn}, pose.head("hips", pose.matrix("hips")));
}

// a fall down to a perch: the arms thrown up and flailing, the legs kicking, the body leaning back as it drops
function fall(pose, stance, t) {
    const u = onceTime(t, 12);
    const drop = rise(u, 0, 0.2);
    // the first instant is a gasp: the head and arms snap back and up before the flailing starts
    const gasp = swell(u, 0, 0.3);
    pose.lift("root", {z: 0.1 * drop});
    breathe(pose, 0);
    trunk(pose, {lean: -9 * drop - 8 * gasp, nod: -6 * drop - 10 * gasp, tilt: 4 * waveOf(t, 3) * drop});
    flung(pose, stance, 0, (70 + 8 * waveOf(t, 3)) * drop + 25 * gasp, 14 * waveOf(t, 3) * drop);
    eyesAs(pose, "startled", Math.max(gasp, 0.6 * drop));
    tucked(pose, 0.5 * drop, 14 * waveOf(t, 3) * drop);
}

// the landing after either: the knees take the weight, the body folds forward and the arms spread for balance, then it stands
function land(pose, stance, t) {
    const u = onceTime(t, LANDING.frames);
    const dip = rise(u, 0, 0.2) * (1 - rise(u, 0.2, 1));
    breathe(pose, 0);
    trunk(pose, {lean: 16 * dip, nod: 8 * dip});
    flung(pose, stance, 0, 38 * dip);
    fold(pose, 0.32 * dip);
}

// the squire runs after a bug when a check goes red, quill out ahead of him, and comes back
function squire_chase(pose, stance, t) {
    const u = onceTime(t, 24);
    const out = u < 0.5;
    const reach = CHASE_REACH * (out ? ease(span(u, 0, 0.5)) : 1 - ease(span(u, 0.5, 1)));
    const motion = Math.sqrt(Math.max(Math.sin(Math.PI * u), 0));
    const quill = heldUp(stance);
    pose.lift("root", {y: out ? -reach : reach});
    stride(pose, stance, 4 * u, motion, {running: true, lean: 12, apart: quill});
    quill.forEach((side) => armTo(pose, side, motion, SQUIRE_QUILL));
    pose.revolve((out ? 90 : -90) * Math.min(1, 3 * Math.sin(Math.PI * u)));
}

// Each voice's one pointed remark after a long wait on the user, played once
// the butler taps his foot, patiently
function butler_pointed(pose, stance, u) {
    const tap = TAP_LIFT * Math.max(waveOf(3 * u), 0) * swell(u, 0, 1);
    breathe(pose, 0);
    trunk(pose, {tilt: 8 * swell(u, 0, 1), nod: 6 * swell(u, 0, 1), turn: 10 * swell(u, 0, 1)});
    armsAtRest(pose, stance);
    stepLeg(pose, "r", 0, tap, 0, (15 * tap) / TAP_LIFT);
}

// the homie shrugs: arms out, palms up, head on one side
function homie_pointed(pose, stance, u) {
    const shrug = swell(u, 0, 1);
    breathe(pose, 0);
    trunk(pose, {tilt: 14 * shrug, nod: -8 * shrug});
    for (const side of Object.keys(SIDES)) armTo(pose, side, shrug, {y: 30, z: -15, bend: 100});
}

// the coach gives one long blast on the whistle
function coach_pointed(pose, stance, u) {
    const side = freeSide(stance);
    const whistling = rise(u, 0, 0.15) * (1 - rise(u, 0.8, 1));
    const blast = swell(u, 0.2, 0.75);
    breathe(pose, 0);
    trunk(pose, {lean: -4 * blast, nod: -6 * blast});
    armsAtRest(pose, stance, whistling ? [side] : []);
    if (whistling) handTo(pose, side, whistling, chin(side), CHIN_ELBOW);
    pose.shutEyes(1 - 0.7 * blast);
}

// the colleague looks at the time on the free wrist, then at you
function colleague_pointed(pose, stance, u) {
    const side = freeSide(stance);
    const wrist = rise(u, 0, 0.2) * (1 - rise(u, 0.6, 0.85));
    breathe(pose, 0);
    trunk(pose, {nod: 18 * wrist * (1 - rise(u, 0.35, 0.5)), turn: -SIDES[side] * 8 * wrist});
    armsAtRest(pose, stance, wrist ? [side] : []);
    if (wrist) handTo(pose, side, wrist, chin(side), CHIN_ELBOW);
}

// the squire wags his quill at you, tut tut
function squire_pointed(pose, stance, u) {
    const quill = heldUp(stance);
    const raised = rise(u, 0, 0.2) * (1 - rise(u, 0.75, 1));
    breathe(pose, 0);
    trunk(pose, {tilt: -5 * raised, nod: 4 * raised});
    armsAtRest(pose, stance, raised ? quill : []);
    if (raised) quill.forEach((side) => armTo(pose, side, raised, {y: 30, z: -25 + 5 * waveOf(3 * u), bend: 10}));
}

const POINTED = {
    bare: butler_pointed,
    butler: butler_pointed,
    homie: homie_pointed,
    coach: coach_pointed,
    colleague: colleague_pointed,
    squire: squire_pointed,
};

function pointed(pose, stance, t) {
    POINTED[stance.voice](pose, stance, onceTime(t, 20));
}

// Each voice's answer to one of its own faces, put by the agent on the user's message: a gesture in the voice's manner, played once, starting
// and ending at rest. The hand that gestures is the free one; what the other carries stays in it.
export const REACTING = {
    frames: 36, fps: 12,
    hatOn: 1.101, hatWrist: [1.05, -0.2, 2.85], hatRaised: [0.95, -0.5, 2.85], hatTip: 25, hatFingers: 0.25, hatBow: 22, hatNod: 14,
    monocleWrist: [0.55, -0.8, 2.62], monocleWorn: [0.354, -0.95, 0.66], monoclePeer: 8, monocleTilt: 9,
    toastWrist: [0.78, -0.72, 2.55], toastClink: 0.12, sipWrist: [0.42, -0.78, 2.38], sipTip: 20,
    shakaWrist: [1.22, -0.25, 2.72], shakaWaggle: 28, shakaWaggles: 3,
    shadesWrist: [0.5, -0.82, 2.55], shadesWorn: [0, -0.96, 0.66], shadesLean: 7, shadesTilt: 10,
    fireWrist: [0.48, -0.86, 2.28], fireSize: 2.4,
    thumbWrist: [0.62, -0.84, 2.3],
    glassesWrist: [0.32, -0.8, 2.47], peerLean: 12, peerTurn: 18,
    prayerWrist: [0.12, -0.62, 2.0], prayerRoll: 180, thanksBow: 14,
    popperWrist: [0.95, -0.45, 2.85], popAt: 0.4, popHop: 0.12,
    flex: {y: 0, x: -85, z: 15, bend: 115}, flexPump: 15,
    trophy: {y: -55, x: 15, z: 0, bend: 15}, trophyHop: 0.1,
    sword: {y: -62, x: 18, z: 0, bend: 12}, swordThrust: 12,
    shieldWrist: [0.24, -0.78, 2.3], shieldCrouch: 0.08, shieldBump: 0.5,
    castleWrist: [0.55, -0.88, 2.34],
};

// what the hand that does not gesture carries stays in it while the gesturing hand holds a prop
const keepCarrying = (pose) => BUSY_ITEMS.forEach((item) => pose.keep.add(item));

// the clip's time as {u, ready}, ready rising from rest and back to it over the whole clip
const reacting = (t) => gestureTime(t, REACTING.frames);

// the hand on `side` taken from hanging toward `target` (k), and turned so its back faces out and its grip points up
function handUp(pose, side, k, target, turn = {}) {
    propHand(pose, side, k, target, {x: -60 * k, ...turn});
}

// straight up, at rest
const UP = new THREE.Vector3(0, 0, 1);

// the butler raises his hand beside his top hat, the hat comes off into it by the brim, he lifts it and bows a little, and puts it back on
function hat_tip(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const held = rise(u, 0.2, 0.3) * (1 - rise(u, 0.7, 0.8));
    const raised = rise(u, 0.3, 0.4) * (1 - rise(u, 0.6, 0.7));
    const bow = swell(u, 0.32, 0.72);
    breathe(pose, 0);
    trunk(pose, {lean: REACTING.hatBow * bow, nod: REACTING.hatNod * bow});
    armsAtRest(pose, stance, ready ? [side] : []);
    handUp(pose, side, ready, REACTING.hatWrist.map((value, axis) => mix(value, REACTING.hatRaised[axis], raised)));
    if (ready) pose.aim(`hand_${side}`, pose.rig.along.get(`hand_${side}`).clone().transformDirection(pose.matrix(`hand_${side}`)).lerp(UP, ready));
    if (held) {
        const turn = {y: SIDES[side] * REACTING.hatTip * held};
        pose.putAway("butler_top_hat", "butler_top_hat_band");
        pose.wearProp("top_hat", hatHeld(pose, side, held, turn).toArray(), turn);
    }
    eyesAs(pose, "amused", bow);
}

// where the hat sits against the head at rest, `held` of the way from on the head to in the hand on `side`, its brim's edge at the fingers
function hatHeld(pose, side, held, turn) {
    const edge = new THREE.Vector3(SIDES[side] * (BUTLER.hat.crown + BUTLER.hat.brim), 0, 0).applyMatrix4(euler(0, turn.y, 0));
    const grip = handGrip(pose, side, [REACTING.hatFingers, 0, 0]).applyMatrix4(pose.matrix("head").clone().invert());
    const inHand = grip.sub(edge).sub(pose.rig.heads.get("head"));
    return new THREE.Vector3(0, 0, REACTING.hatOn).lerp(inHand, held);
}

// the butler brings up a monocle, screws it into his eye, peers through it a moment, and lets it drop
function monocle(pose, stance, t) {
    const {u} = reacting(t);
    const side = freeSide(stance);
    const sign = SIDES[side];
    const raised = rise(u, 0, 0.2) * (1 - rise(u, 0.82, 1));
    const peer = rise(u, 0.26, 0.36) * (1 - rise(u, 0.66, 0.76));
    breathe(pose, 0);
    trunk(pose, {lean: REACTING.monoclePeer * peer, nod: REACTING.monoclePeer * peer, tilt: sign * REACTING.monocleTilt * peer});
    armsAtRest(pose, stance, raised ? [side] : []);
    const away = 1 - 0.35 * peer;
    handUp(pose, side, raised, REACTING.monocleWrist.map((value, axis) => (axis === 2 ? value - 0.25 * (1 - away) : value)));
    const [x, y, z] = REACTING.monocleWorn;
    if (u > 0.18 && u < 0.8) pose.wearProp("monocle", [sign * x, y, z]);
    else if (raised > 0.4) pose.holdUpright("monocle", side, [0, 0, 0.2]);
    eyesAs(pose, "startled", 0.6 * peer);
}

// the butler raises a glass of champagne to you, clinks it toward you, and takes a sip
function toast(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const clink = swell(u, 0.3, 0.42);
    const sip = swell(u, 0.5, 0.78);
    breathe(pose, 0);
    trunk(pose, {lean: 4 * clink, nod: -6 * sip});
    armsAtRest(pose, stance, ready ? [side] : []);
    const target = REACTING.toastWrist.map((value, axis) => mix(value, REACTING.sipWrist[axis], sip) + (axis === 1 ? -REACTING.toastClink * clink : 0));
    handUp(pose, side, ready, target);
    if (ready > 0.3) pose.holdUpright("champagne_flute", side, [0, 0, 0.1], {x: REACTING.sipTip * sip, y: SIDES[side] * REACTING.sipTip * sip});
    pose.shutEyes(1 - 0.7 * sip);
    if (clink > 0.5) eyesAs(pose, "amused", clink);
}

// the homie throws a shaka up beside his head and waggles it, leaning back easy
function shaka(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const sign = SIDES[side];
    breathe(pose, 0);
    trunk(pose, {lean: -5 * ready, tilt: -sign * 8 * ready, turn: -sign * 6 * ready});
    armsAtRest(pose, stance, ready ? [side] : []);
    handUp(pose, side, ready, REACTING.shakaWrist, {y: REACTING.shakaWaggle * waveOf(span(u, 0.2, 0.8), REACTING.shakaWaggles) * ready});
    if (ready > 0.5) pose.holdUpright("shaka", side, [0, 0, 0.32]);
    eyesAs(pose, "amused", ready);
}

// the homie puts on a pair of sunglasses, leans back and nods slowly to himself, then takes them off again
function shades(pose, stance, t) {
    const {u} = reacting(t);
    const side = freeSide(stance);
    const sign = SIDES[side];
    const putting = rise(u, 0, 0.15) * (1 - rise(u, 0.15, 0.3));
    const taking = rise(u, 0.72, 0.86) * (1 - rise(u, 0.86, 1));
    const worn = u > 0.22 && u < 0.82;
    const cool = rise(u, 0.28, 0.38) * (1 - rise(u, 0.66, 0.76));
    breathe(pose, 0);
    trunk(pose, {lean: -REACTING.shadesLean * cool, tilt: sign * REACTING.shadesTilt * cool, nod: 6 * cool * Math.max(waveOf(span(u, 0.38, 0.66), 2), 0)});
    const hand = Math.max(putting, taking);
    armsAtRest(pose, stance, hand ? [side] : []);
    handUp(pose, side, hand, REACTING.shadesWrist);
    if (worn) pose.wearProp("sunglasses", REACTING.shadesWorn);
    else if (hand > 0.4) pose.holdUpright("sunglasses", side, [0, -0.1, 0.25]);
}

// the homie holds up a hand with a flame on it, nods along to how hot that was, shakes it out and blows on his fingers
function fire(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const burning = rise(u, 0.18, 0.28) * (1 - rise(u, 0.66, 0.74));
    const shaking = swell(u, 0.66, 0.84);
    breathe(pose, 0);
    trunk(pose, {nod: 8 * burning * Math.max(waveOf(span(u, 0.28, 0.66), 3), 0) + 6 * shaking, tilt: SIDES[side] * 5 * burning});
    armsAtRest(pose, stance, ready ? [side] : []);
    handUp(pose, side, ready, REACTING.fireWrist, {y: 25 * shaking * waveOf(u, 9)});
    if (burning > 0.02) {
        pose.holdUpright("flame", side, [0, 0, 0.18]);
        Object.assign(pose.props.get("flame"), {phase: u, size: REACTING.fireSize * burning});
    }
    eyesAs(pose, shaking > 0.3 ? "startled" : "amused", Math.max(burning, shaking));
}

// the colleague gives a thumbs up and a firm nod
function thumbs_up(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const nodded = swell(u, 0.35, 0.6);
    breathe(pose, 0);
    trunk(pose, {nod: 14 * nodded, lean: 3 * ready});
    armsAtRest(pose, stance, ready ? [side] : []);
    handUp(pose, side, ready, REACTING.thumbWrist, {y: 0});
    if (ready > 0.5) {
        pose.holdUpright("thumb", side, [0, 0, 0.3]);
        keepCarrying(pose);
    }
    eyesAs(pose, "amused", nodded);
}

// the colleague pushes his glasses up his nose, leans in and looks it over, one side and the other
function peer(pose, stance, t) {
    const {u} = reacting(t);
    const side = freeSide(stance);
    const push = rise(u, 0, 0.14) * (1 - rise(u, 0.24, 0.36));
    const leaning = rise(u, 0.26, 0.38) * (1 - rise(u, 0.8, 0.95));
    const look = swell(u, 0.38, 0.58) - swell(u, 0.58, 0.8);
    breathe(pose, 0);
    trunk(pose, {lean: REACTING.peerLean * leaning, nod: 6 * leaning, turn: REACTING.peerTurn * look});
    armsAtRest(pose, stance, push ? [side] : []);
    const [x, y, z] = REACTING.glassesWrist;
    handUp(pose, side, push, [x, y, z + 0.08 * rise(u, 0.12, 0.22)]);
    eyesAs(pose, "reading", leaning);
}

// any voice presses its hands together before its chest, fingers up, and gives a small bow, eyes closed: thanks
function thanks(pose, stance, t) {
    const {u, ready} = reacting(t);
    const bow = swell(u, 0.25, 0.8);
    breathe(pose, 0);
    trunk(pose, {lean: REACTING.thanksBow * bow, nod: 10 * bow});
    armsAtRest(pose, stance, ready ? Object.keys(SIDES) : []);
    if (ready) pose.putAway(...IN_HAND);
    for (const [side, sign] of Object.entries(SIDES)) {
        propHand(pose, side, ready, REACTING.prayerWrist, {x: REACTING.prayerRoll * ready, y: -sign * 90 * ready, z: 0});
    }
    pose.shutEyes(1 - 0.85 * bow);
}

// the coach pulls a party popper over his head; the confetti bursts out and he hops with it
function party_popper(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const hop = swell(u, REACTING.popAt, REACTING.popAt + 0.2);
    pose.lift("root", {z: REACTING.popHop * hop});
    breathe(pose, 0);
    trunk(pose, {lean: -4 * hop, nod: -8 * hop});
    armsAtRest(pose, stance, ready ? [side] : []);
    handUp(pose, side, ready, REACTING.popperWrist);
    if (ready > 0.4) {
        pose.holdUpright("party_popper", side, [0, 0, 0.1], {y: SIDES[side] * 25});
        pose.props.get("party_popper").burst = span(u, REACTING.popAt, 0.95);
        keepCarrying(pose);
    }
    eyesAs(pose, "amused", hop);
}

// the coach flexes the free arm, pumping it twice, chest out
function flex(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const pump = Math.max(waveOf(span(u, 0.25, 0.75), 2), 0);
    breathe(pose, 0);
    trunk(pose, {lean: -5 * ready, twist: -SIDES[side] * 10 * ready, tilt: SIDES[side] * 4 * ready, nod: -4 * ready});
    armsAtRest(pose, stance, ready ? [side] : []);
    if (ready) armTo(pose, side, ready, {...REACTING.flex, bend: REACTING.flex.bend + REACTING.flexPump * pump});
    eyesAs(pose, "angry", 0.6 * pump);
}

// the coach holds a trophy up over his head and bounces with it twice
function trophy(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = freeSide(stance);
    const bounce = Math.max(waveOf(span(u, 0.25, 0.75), 2), 0);
    pose.lift("root", {z: REACTING.trophyHop * bounce});
    breathe(pose, 0);
    trunk(pose, {nod: -12 * ready, lean: -4 * ready});
    armsAtRest(pose, stance, ready ? [side] : []);
    if (ready) armTo(pose, side, ready, REACTING.trophy);
    if (ready > 0.4) {
        pose.holdUpright("trophy", side, [0, 0, 0.3]);
        keepCarrying(pose);
    }
    eyesAs(pose, "amused", ready);
}

// the squire puts the quill away, draws a sword and raises it high, thrusting it up twice, onwards
function sword(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = heldUp(stance)[0] || freeSide(stance);
    const thrust = Math.max(waveOf(span(u, 0.25, 0.75), 2), 0);
    breathe(pose, 0);
    trunk(pose, {lean: -4 * ready, nod: -10 * ready});
    armsAtRest(pose, stance, ready ? [side] : []);
    if (ready) armTo(pose, side, ready, {...REACTING.sword, y: REACTING.sword.y - REACTING.swordThrust * thrust});
    if (ready) pose.putAway("squire_quill");
    if (ready > 0.4) {
        pose.holdUpright("sword", side, [0, 0, 0.15], {x: -15});
        keepCarrying(pose);
    }
    eyesAs(pose, "angry", ready);
}

// the squire raises his shield before him and braces behind it as a blow lands, then lowers it
function shield_up(pose, stance, t) {
    const {u, ready} = reacting(t);
    const shield = [...stance.shield][0];
    if (!shield) return idle(pose, stance, t);
    const bump = swell(u, REACTING.shieldBump, REACTING.shieldBump + 0.12);
    crouch(pose, REACTING.shieldCrouch * ready);
    breathe(pose, 0);
    trunk(pose, {lean: 8 * ready - 8 * bump, nod: 6 * ready});
    armsAtRest(pose, stance, ready ? [shield] : []);
    const [x, y, z] = REACTING.shieldWrist;
    propHand(pose, shield, ready, [x, y + 0.08 * bump, z]);
    pose.keep.add("squire_shield");
    eyesAs(pose, bump > 0.3 ? "startled" : "angry", ready);
}

// the squire holds out a small castle on his palm, the realm he keeps, and bows his head over it
function castle(pose, stance, t) {
    const {u, ready} = reacting(t);
    const side = heldUp(stance)[0] || freeSide(stance);
    const bow = swell(u, 0.35, 0.75);
    breathe(pose, 0);
    trunk(pose, {nod: 12 * bow, lean: 4 * bow});
    armsAtRest(pose, stance, ready ? [side] : []);
    propHand(pose, side, ready, REACTING.castleWrist, {x: -30 * ready});
    if (ready) pose.putAway("squire_quill");
    if (ready > 0.4) {
        pose.holdUpright("castle", side, [0, 0, 0.12]);
        keepCarrying(pose);
    }
    eyesAs(pose, "amused", bow);
}

// The journal moments and the searches the figure acts out (acts.js ACTS), what it holds and what grows beside it drawn by the page at its
// free hand and its feet (chat/FigureAct.vue). The wrist places, against the body at rest with the free hand's side outward: held up high,
// the sign held up, at
// the drawer, at the binoculars before the eyes, the flashlight held out, and down at the corner of the floor while it crouches `crouch`
export const ACTED = {
    high: [1.0, -0.25, 2.92],
    sign: [0.5, -0.25, 3.0], signWaggle: 0.1,
    drawer: [1.16, -0.4, 1.66], drop: 0.12, binoculars: [0.24, -0.8, 2.36], sweep: 30, torch: [1.1, -0.55, 1.88], torchSweep: 0.16,
    corner: [1.0, -0.42, 1.36], lift: 0.3, crouch: 0.6, peekLean: 34,
}

// the free hand's place between the wrist places `from` and `to`, `k` of the way
const between3 = (from, to, k) => from.map((n, index) => mix(n, to[index], k));

// what the free hand carries put away while it holds what the page draws in it, the busy hand keeping its own
const emptyHand = (pose) => pose.putAway(...[...IN_HAND].filter((item) => !BUSY_ITEMS.has(item)));

// the free hand carried `ready` of the way from hanging to the wrist place `at`, the other arm at rest
function actHand(pose, stance, ready, at, turn = {}) {
    const side = freeSide(stance);
    armsAtRest(pose, stance, ready ? [side] : []);
    propHand(pose, side, ready, at, turn);
    if (ready) emptyHand(pose);
}

// The call on the telephone (acts.js phone_call): how deep it bends to the telephone and how far it leans and nods into the bend, and how
// far it nods while it talks, in the figure's units and degrees; where its ear is on the head at rest, against which the handset's ear cup
// is held, the handset leaning `lean` degrees back from upright; how far it tilts its head to the handset; how far above a hole of the
// dial its finger's wrist is held, the finger reaching down into it; and how far in from the palm the handset's grip is held, its fingers
// round the back of the grip: toward the head at the ear, under the palm as it takes the handset off the cradle
export const CALL = {bend: 0.9, lean: 30, nod: 18, talkNod: 7, ear: [1.24, 0.05, 3.3], handsetLean: 16, tilt: 8, wrist: [0, -0.12, 0.3], palm: 0.16};

// a point on the telephone, `local` in its own axes (across, back, up from the middle of its base on the floor), where it stands now, the
// whole telephone tipped `tip` degrees toward the viewer so its dial shows, raised by `raised` as the root is lowered by a crouch
function onPhone(local, raised = 0) {
    const tipped = local.clone().applyAxisAngle(new THREE.Vector3(1, 0, 0), radians(TELEPHONE.tip));
    return tipped.add(new THREE.Vector3(TELEPHONE.at[0], TELEPHONE.at[1], raised));
}

// a point in the telephone's own axes (y up, its front +z) in the figure's (z up, its front -y)
const fromSet = (point) => new THREE.Vector3(point.x, -point.z, point.y);

// where the dial sits in the telephone's own axes: its middle on the middle of the front face, from the face's foot to its brow, and its
// axis out of the face, as a matrix from the dial's own axes (its face up its y)
function dialFrame() {
    const {base} = TELEPHONE;
    const [foot, brow] = [[base.depth / 2, 0], base.brow];
    const out = new THREE.Vector2(brow[1], foot[0] - brow[0]).normalize();
    const middle = new THREE.Vector3(0, (foot[1] + brow[1]) / 2, (foot[0] + brow[0]) / 2).add(new THREE.Vector3(0, out.y, out.x).multiplyScalar(bulge()));
    return new THREE.Matrix4().compose(middle, new THREE.Quaternion().setFromEuler(new THREE.Euler(Math.atan2(out.x, out.y), 0, 0)), new THREE.Vector3(1, 1, 1));
}

// how far the body's rounding swells out of its side outline, and how high its domed top is `across` from the middle
const bulge = () => TELEPHONE.base.round * 0.8;
const crownAt = (across) => TELEPHONE.base.height + bulge() + TELEPHONE.base.dome * Math.max(1 - (across / (TELEPHONE.base.width / 2)) ** 2, 0);

// where the handset's middle rests across the cradle's prongs, in the figure's axes against the telephone
const cradled = () => fromSet(new THREE.Vector3(0, crownAt(TELEPHONE.cradle.apart) + TELEPHONE.cradle.height + TELEPHONE.handset.rest, TELEPHONE.cradle.at));

// a point `turned` degrees round the dial from its first hole, on the ring of holes, just over the dial's face, in the figure's axes
// against the telephone
function dialHole(turned) {
    const {dial} = TELEPHONE;
    const angle = radians(dial.first - turned);
    return fromSet(new THREE.Vector3(Math.cos(angle) * dial.ring, dial.face * 1.5, -Math.sin(angle) * dial.ring).applyMatrix4(dialFrame()));
}

// the handset held at the ear on `side`: its long axis, ear cup up, leaning back from upright, and its cups' mouths toward the head, as
// the turn its prop takes (figure.js euler, degrees about x, y and z) and that axis
function handsetAtEar(side) {
    const sign = SIDES[side];
    const along = new THREE.Vector3(0, Math.sin(radians(CALL.handsetLean)), Math.cos(radians(CALL.handsetLean)));
    const outward = new THREE.Vector3(sign, 0, 0);
    const basis = new THREE.Matrix4().makeBasis(along, outward.clone().cross(along), outward);
    const turn = new THREE.Euler().setFromRotationMatrix(basis, "ZYX");
    return {along, turn: {x: THREE.MathUtils.radToDeg(turn.x), y: THREE.MathUtils.radToDeg(turn.y), z: THREE.MathUtils.radToDeg(turn.z)}};
}

// The telephone's way in and out at `u` of the call (acts.js phone_call): whether it is there, how far above the floor it is drawn and how it
// squashes, and how far through a poof of smoke it is at its place, if one bursts. It is there whole from the first frame, `above` the
// floor in the burst of its poof; it drops onto the floor over `drop`, gathering speed, and settles over `settle`, squashing `squash` flat
// as it lands and wobbling `wobbles` times smaller each time to still; it goes in the middle of the poof it leaves in, over `goes`
export function phoneArrival(u) {
    const act = ACTS.phone_call;
    const fell = span(u, ...act.drop);
    const settling = span(u, ...act.settle);
    const wobble = settling > 0 && settling < 1 ? Math.sin(Math.PI * act.wobbles * settling) * (1 - settling) ** 2 : 0;
    const leaving = span(u, ...act.goes);
    const arriving = span(u, ...act.poof);
    return {
        here: leaving < 0.5,
        above: act.above * (1 - fell * fell),
        squash: act.squash * wobble,
        puff: u >= act.goes[0] ? leaving : arriving < 1 ? 0.3 + 0.7 * arriving : null,
    };
}

// A call on an old desk telephone that appears on the floor before it: it bends and lifts the handset to its ear with its free hand, bends
// again and dials with a finger of the other, the dial turning round to the stop and springing back as the finger leaves it, talks a while,
// nodding, and bends to put the handset back on the cradle; then the telephone goes. Its coiled cord runs from the base to the mouthpiece.
function phone_call(pose, stance, t) {
    const act = ACTS.phone_call;
    const u = onceTime(t, act.frames);
    const side = freeSide(stance);
    const dialler = side === "l" ? "r" : "l";
    const bent = Math.max(
        partOf(u, act.reach) * (1 - partOf(u, act.lift)),
        partOf(u, act.finger) * (1 - partOf(u, act.back)),
        partOf(u, [act.hang[0], (act.hang[0] + act.hang[1]) / 2]) * (1 - partOf(u, [act.hang[1], act.goes[0]])),
    );
    const lifted = partOf(u, act.lift) * (1 - partOf(u, [act.hang[0], act.hang[0] + (act.hang[1] - act.hang[0]) * 0.7]));
    const talking = span(u, ...act.talk);
    const down = CALL.bend * bent;
    crouch(pose, down);
    breathe(pose, 0);
    trunk(pose, {lean: CALL.lean * bent, nod: CALL.nod * bent + CALL.talkNod * Math.sin(Math.PI * act.nods * talking) ** 2, tilt: SIDES[side] * CALL.tilt * lifted});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, [side, dialler]);
    // the handset: taken off the cradle, held with its ear cup at the ear, and put back
    const {handset} = TELEPHONE;
    const atEar = handsetAtEar(side);
    const [x, y, z] = CALL.ear;
    const ear = new THREE.Vector3(SIDES[side] * x, y, z).applyMatrix4(pose.matrix("head"));
    const held = ear.clone().addScaledVector(atEar.along, -handset.length / 2);
    const rest = onPhone(cradled());
    const reach = u >= act.reach[1] && u < act.hang[1] ? 1 : partOf(u, act.reach) * (1 - partOf(u, [act.hang[1], act.goes[0]]));
    // the palm behind the grip, the way from it to the handset turning from down, over the handset on its cradle, to the head at the ear
    const inward = new THREE.Vector3(0, 0, -1).lerp(new THREE.Vector3(-SIDES[side], 0, 0), lifted).normalize();
    const palm = rest.clone().lerp(held, lifted).addScaledVector(inward, -CALL.palm);
    handTo(pose, side, reach, pose.withinReach(side, palm, 0.97), new THREE.Vector3(1, 0.4, -0.6));
    const inHand = u >= act.reach[1] && u < act.hang[1];
    const along = new THREE.Vector3(1, 0, 0).lerp(atEar.along, lifted).normalize();
    // lifted, the hand turns to run up along the handset, its fingers round the back of the grip
    if (inHand) {
        const pointing = pose.rig.along.get(`hand_${side}`).clone().transformDirection(pose.matrix(`hand_${side}`));
        pose.aim(`hand_${side}`, pointing.lerp(atEar.along, lifted).normalize());
    }
    const grip = inHand && pose.grip(side, [0, 0, 0]).applyMatrix4(pose.matrix(`hand_${side}`)).addScaledVector(inward, CALL.palm);
    const mouth = inHand ? grip.clone().addScaledVector(along, -handset.length / 2) : onPhone(cradled().add(new THREE.Vector3(-handset.length / 2, 0, -handset.drop - handset.end[1])));
    if (inHand) {
        pose.holdUpright("telephone_handset", side, [0, 0, 0], {x: atEar.turn.x * lifted + TELEPHONE.tip * (1 - lifted), y: atEar.turn.y * lifted, z: atEar.turn.z * lifted});
        pose.props.get("telephone_handset").at = grip.clone().applyMatrix4(pose.matrix(`hand_${side}`).clone().invert());
    } else pose.standProp("telephone_handset", onPhone(cradled(), down), {x: TELEPHONE.tip});
    // the dial: a finger put in its first hole, turned round to the stop, and taken out as the dial springs back
    const turned = act.turn * partOf(u, act.dial) * (1 - partOf(u, act.back));
    const finger = partOf(u, act.finger) * (1 - partOf(u, act.back));
    const hole = onPhone(dialHole(act.turn * partOf(u, act.dial))).add(new THREE.Vector3(...CALL.wrist));
    handTo(pose, dialler, finger, pose.withinReach(dialler, hole, 0.97), new THREE.Vector3(-1, 0.2, -0.6));
    eyesAs(pose, "amused", talking > 0 && talking < 1 ? 1 : 0);
    // the telephone: whole from the first frame, dropping in out of its poof and settling, gone in the poof it leaves in
    const arrival = phoneArrival(u);
    const poof = arrival.puff ?? 0;
    if (poof > 0 && poof < 1) {
        pose.standProp("telephone_poof", onPhone(new THREE.Vector3(0, 0, TELEPHONE.base.height / 2 + (u < act.goes[0] ? act.above : 0)), down));
        Object.assign(pose.props.get("telephone_poof"), {puff: poof});
    }
    if (!arrival.here) {
        pose.props.delete("telephone_handset");
        return;
    }
    const lift = new THREE.Vector3(0, 0, arrival.above);
    pose.standProp("telephone", onPhone(new THREE.Vector3(), down).add(lift), {x: TELEPHONE.tip});
    Object.assign(pose.props.get("telephone"), {squash: arrival.squash, dial: turned});
    if (!inHand) pose.props.get("telephone_handset").at.add(lift).add(new THREE.Vector3(0, 0, -arrival.squash * cradled().z));
    // the cord, from the base's side to the mouthpiece, against the root
    pose.standProp("telephone_cord", [0, 0, down]);
    const root = new THREE.Vector3(0, 0, -down);
    const end = inHand ? mouth : mouth.add(lift);
    Object.assign(pose.props.get("telephone_cord"), {from: onPhone(new THREE.Vector3(-SIDES[side] * TELEPHONE.base.width * 0.4, 0.25, TELEPHONE.base.height * 0.3)).add(lift).sub(root), to: end.sub(root)});
}

// raises a sign with a question mark on a stick high over its head and waggles it
function ask_sign(pose, stance, t) {
    const act = ACTS.ask_sign;
    const u = onceTime(t, act.frames);
    const up = partOf(u, act.raise) * (1 - partOf(u, act.lower));
    const waggle = waveOf(span(u, ...act.waggle), act.waggles) * swell(u, ...act.waggle);
    const [x, y, z] = ACTED.sign;
    breathe(pose, 0);
    trunk(pose, {nod: -10 * up, tilt: 4 * waggle});
    actHand(pose, stance, up, [x + ACTED.signWaggle * waggle, y, z]);
    eyesAs(pose, "worried", up);
}

// Where the scroll is held, against the body at rest: the rollers' middle `at` before the chest, low enough for the eyes to show over its
// top edge, each hand `across` from the middle toward its own side, the rollers `closed` apart in height while it is rolled and `apart`
// once it is open; and the head reading it, nodded `nod` degrees down into it and `lineNod` more for each line below, turned slowly from
// `scan` degrees to its own left to as far to its right over the first `sweep` of a line, and back for the next
export const SCROLL = {at: [0, -0.74, 2.02], across: 0.4, closed: 0.08, apart: 0.6, elbow: [1, 0.4, -0.6], nod: 16, lineNod: 4, scan: 12, sweep: 0.6};

// brings the rolled scroll up before its chest, pulls its two rollers apart between its hands, the free hand's above, reads it down line
// by line with its head going slowly along each, and rolls it closed between its hands again
function scroll(pose, stance, t) {
    const act = ACTS.scroll;
    const u = onceTime(t, act.frames);
    const ready = partOf(u, act.raise) * (1 - partOf(u, act.lower));
    const open = partOf(u, act.unrolls) * (1 - partOf(u, act.rolls));
    const read = span(u, act.unrolls[1], act.rolls[0]);
    breathe(pose, 0);
    trunk(pose, {lean: 3 * ready});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, ready ? Object.keys(SIDES) : []);
    const top = freeSide(stance);
    const [x, y, z] = SCROLL.at;
    for (const [side, sign] of Object.entries(SIDES)) {
        const height = z + ((side === top ? 1 : -1) * mix(SCROLL.closed, SCROLL.apart, open)) / 2;
        const spot = new THREE.Vector3(x + sign * SCROLL.across, y, height);
        if (ready) handTo(pose, side, ready, pose.withinReach(side, pose.carried(spot), 0.97), new THREE.Vector3(...SCROLL.elbow));
    }
    const line = Math.min(Math.floor(read * act.lines), act.lines - 1);
    const along = read * act.lines - line;
    const turn = SCROLL.scan * (1 - 2 * partOf(along, [0, SCROLL.sweep]) + 2 * partOf(along, [SCROLL.sweep, 1]));
    pose.face("head", {x: (SCROLL.nod + SCROLL.lineNod * line) * open, z: turn * open});
    eyesAs(pose, "reading", open);
    if (ready) holdScroll(pose, top, ready === 1 ? (top === "l" ? "r" : "l") : null, open);
}

// The report scroll (REPORT_SCROLL) in the hands as they are posed: its top roller gripped toward one end by the hand on `top`, its bottom
// roller toward the other end by the hand on `bottom`, the scroll centred between the two hands; or rolled up just under the top one in
// that hand alone while `bottom` is none; unrolled `open` of the way
function holdScroll(pose, top, bottom, open) {
    const grip = (side) => pose.grip(side, [0, 0, 0]).applyMatrix4(pose.matrix(`hand_${side}`));
    const upper = grip(top);
    const lower = bottom ? grip(bottom) : upper.clone().add(new THREE.Vector3(0, 0, -REPORT_SCROLL.rolled));
    const middle = upper.clone().add(lower).multiplyScalar(0.5);
    if (bottom) upper.x = lower.x = middle.x;
    const root = pose.matrix("root").clone().invert();
    pose.standProp("report_scroll", middle.clone().applyMatrix4(root).toArray());
    Object.assign(pose.props.get("report_scroll"), {top: upper.sub(middle), bottom: lower.sub(middle), open});
}

// reaches down to the drawer slid out of the cabinet beside it and drops a card into it
function file_card(pose, stance, t) {
    const act = ACTS.file_card;
    const u = onceTime(t, act.frames);
    const out = partOf(u, act.reach) * (1 - partOf(u, act.back));
    const [x, y, z] = ACTED.drawer;
    breathe(pose, 0);
    trunk(pose, {lean: 10 * out, nod: 14 * out});
    actHand(pose, stance, out, [x, y, z - ACTED.drop * partOf(u, act.filed)]);
}

// how far into the box the packed figure sinks, below the floor where the page hides it
const PACKED = {sink: 2.1, hop: 0.75, leap: 1.0};

// hops up into the box grown at its feet and sinks down in it, and once the compaction is over jumps out of it, arms up
function pack_box(pose, stance, t) {
    const act = ACTS.pack_box;
    const {into, out} = heldPhases(act, t);
    const hop = swell(into, ...act.hop);
    const sunk = partOf(into, act.into) * (1 - partOf(out, [act.pops, act.pops + 0.2]));
    const leap = swell(out, ...act.leap);
    pose.lift("root", {z: PACKED.hop * hop - PACKED.sink * sunk + PACKED.leap * leap});
    breathe(pose, 0);
    trunk(pose, {lean: 6 * hop, nod: 12 * sunk - 10 * leap});
    flung(pose, stance, 0, 60 * hop + 120 * leap);
    tucked(pose, 0.7 * hop + 0.6 * leap);
    pose.putAway(...IN_HAND);
    eyesAs(pose, "amused", leap);
}

// holds up the press coming down on its head with both hands, eyes squeezed shut while it is squashed, and lets go as it lifts
function press(pose, stance, t) {
    const act = ACTS.press;
    const {into, out} = heldPhases(act, t);
    const up = partOf(into, [0.2, 0.55]) * (1 - partOf(out, [0.2, 0.5]));
    breathe(pose, 0);
    trunk(pose, {nod: -8 * up});
    flung(pose, stance, 0, 140 * up);
    pose.putAway(...IN_HAND);
    pose.shutEyes(1 - 0.8 * partOf(into, act.squashes) * (1 - partOf(out, act.frees)));
}

// holds the vacuum's nozzle out low beside it, sweeping it a little, as the words fly into it
function vacuum(pose, stance, t) {
    const {held, into, out} = heldPhases(ACTS.vacuum, t);
    const [x, y, z] = ACTED.torch;
    breathe(pose, 0);
    trunk(pose, {lean: 8, nod: 14, turn: -SIDES[freeSide(stance)] * 14});
    actHand(pose, stance, into * (1 - out), [x, y, z - 0.12 * waveOf(held ?? 0, 2)], {x: -10});
}

// Eager for the bar under its feet to end: its feet tapping fast over the intro, then pointing down at the bar with the free hand, bouncing
// Eager for the bar under its feet to end, wild with it as a child is: its feet tapping fast over the intro, then both free hands pointing
// down at the bar, bouncing and wiggling, and all the while its eyes sparkling stars
export const EAGERNESS = {intro: 18, hold: 12, outro: 6, fps: 12, taps: 6, tap: 18, point: [1.25, -0.45, 1.75], bounce: 0.14, wiggle: 7, sparkle: 0.25};

function eager(pose, stance, t) {
    const {intro, hold, outro, taps, tap, point, bounce, wiggle, sparkle} = EAGERNESS;
    const frame = t * (intro + hold + outro);
    const tapping = frame < intro ? Math.sin((Math.PI * frame) / intro) : 0;
    const pointing = frame < intro ? rise(frame / intro, 0.7, 1) : 1 - rise((frame - intro - hold) / outro, 0, 1);
    const held = frame >= intro && frame < intro + hold ? (frame - intro) / hold : null;
    const bob = held === null ? 0 : Math.abs(Math.sin(2 * Math.PI * held));
    const beat = waveOf(frame / intro, taps);
    pose.lift("root", {z: bounce * bob});
    breathe(pose, 0);
    trunk(pose, {lean: 6 * pointing, nod: 14 * pointing + 4 * bob, twist: wiggle * (held === null ? tapping * beat : waveOf(held, 2))});
    if (pose.posture === "stand") {
        pose.turn("foot_l", {x: tap * tapping * Math.max(beat, 0)});
        pose.turn("foot_r", {x: tap * tapping * Math.max(-beat, 0)});
    }
    armsAtRest(pose, stance, pointing ? [...stance.free] : []);
    for (const side of stance.free) propHand(pose, side, pointing, [point[0], point[1], point[2] + 0.1 * bob * SIDES[side]], {x: 40});
    if (pointing) emptyHand(pose);
    const glow = Math.min(frame / 4, 1) * (1 - span(frame, intro + hold, intro + hold + outro));
    pose.starEyes(glow * (1 + sparkle * Math.abs(waveOf(frame / 6))));
}

// crushed by the bar it was eager for failing, slumped and looking down, then mad about it: stamping one foot and the other, fists
// clenched at its sides, shaking, its eyes red
function fume(pose, stance, t) {
    const act = ACTS.fume;
    const u = onceTime(t, act.frames);
    const crushed = swell(u, act.crushed[0], act.crushed[1] + 0.06);
    const mad = partOf(u, [act.mad[0], act.mad[0] + 0.06]) * (1 - partOf(u, [act.mad[1], 1]));
    const stamp = waveOf(span(u, ...act.mad), act.stamps / 2);
    crouch(pose, 0.14 * crushed);
    pose.lift("root", {z: 0.12 * mad * Math.abs(stamp)});
    breathe(pose, 0);
    trunk(pose, {lean: 16 * crushed + 6 * mad, nod: 28 * crushed + 10 * mad, tilt: 5 * mad * waveOf(u, 14)});
    armsAtRest(pose, stance, mad ? [...stance.free] : []);
    for (const side of stance.free) armTo(pose, side, mad, {y: 40, z: -25, bend: 95});
    if (pose.posture === "stand") {
        for (const [side, sign] of [["l", 1], ["r", -1]]) {
            const up = mad * Math.max(sign * stamp, 0);
            pose.turn(`thigh_${side}`, {x: -34 * up, y: sign * 18 * up});
            pose.turn(`shin_${side}`, {x: 52 * up});
        }
    }
    if (crushed > mad) eyesAs(pose, "worried", crushed);
    else eyesAs(pose, "angry", mad);
}

// A glance from standing still, held a moment and back: to the page's left or right, the head turned up to `head` degrees and the
// shoulders `body` more after it, so a look further round than HEAD_TURN turns the body too; or up, the head tipped back
// a glance aside is small and held a moment: the head turns a little, the body barely
export const GLANCE = {frames: 36, fps: 12, head: 18, body: 5, up: 10};

const glanceAt = (way, up) => (pose, stance, t) => {
    const u = onceTime(t, GLANCE.frames);
    const held = rise(u, 0.08, 0.25) * (1 - rise(u, 0.75, 0.92));
    trunk(pose, {twist: way * GLANCE.body * held, turn: way * GLANCE.head * held, nod: -up * GLANCE.up * held});
    armsAtRest(pose, stance);
};

// how quick a landing is: a real fall's stop, the knees giving and springing back in under a third of a second
export const LANDING = {frames: 6, fps: 20};

// Landing wrong from a launch: it trips, falls onto its knees at a fall's speed with a little bounce, shakes its head, gets up and gives a little hop, arms up, as if nothing
// happened; the hips drop `drop` to kneel, the shins laid back along the floor
export const TUMBLE = {frames: 48, fps: 12, trip: [0, 0.14], down: [0.05, 0.11], bounce: [0.11, 0.18], shake: [0.3, 0.58], shakes: 3, up: [0.62, 0.8], hop: [0.8, 0.96], drop: 0.74};

function tumble(pose, stance, t) {
    const u = onceTime(t, TUMBLE.frames);
    const kneel = rise(u, ...TUMBLE.down) * (1 - rise(u, ...TUMBLE.up));
    const flail = swell(u, ...TUMBLE.trip);
    const shake = waveOf(span(u, ...TUMBLE.shake), TUMBLE.shakes) * swell(u, ...TUMBLE.shake);
    const hop = swell(u, ...TUMBLE.hop);
    pose.lift("root", {z: -TUMBLE.drop * kneel + 0.1 * swell(u, ...TUMBLE.bounce) + 0.16 * hop});
    if (pose.posture === "stand") for (const side of Object.keys(SIDES)) pose.turn(`shin_${side}`, {x: 90 * kneel});
    trunk(pose, {lean: 12 * kneel + 10 * flail * (1 - kneel), nod: 12 * kneel, turn: 26 * shake});
    flung(pose, stance, 0, 100 * flail * (1 - kneel) + 60 * hop, 8 * flail);
    pose.putAway(...IN_HAND);
    if (hop > 0.1) eyesAs(pose, "amused", hop);
    else eyesAs(pose, kneel > 0.5 ? "worried" : "startled", Math.max(kneel, flail));
}

// Sitting on the edge of a floor facing the viewer, legs over the edge, leaning back a little on both hands laid flat on the edge beside
// its hips, palms down and fingers out, the free hands only, a carried thing kept in hand; it breathes and its legs swing gently. `hands`
// is where each wrist rests, across and forward, on the floor line the seat sits on (LOUNGE floor), the free hand's side outward
export const LEDGE = {hands: [0.8, 0.18], lean: -7, nod: -3};

function ledge_sit(pose, stance, t) {
    breathe(pose, t);
    trunk(pose, {lean: LEDGE.lean, nod: LEDGE.nod + 2 * waveOf(t)});
    const [x, y] = LEDGE.hands;
    armsAtRest(pose, stance, [...stance.free]);
    for (const side of stance.free) {
        handTo(pose, side, 1, pose.withinReach(side, new THREE.Vector3(SIDES[side] * x, y, LOUNGE.floor), 0.97), new THREE.Vector3(1, 0.6, 0.2));
        pose.face(`hand_${side}`, {x: -80});
    }
    if (stance.free.size) emptyHand(pose);
    pose.swing(0.6 * waveOf(t));
}

// hops on up from bubble to bubble, arms flung up and legs tucked, very fast
function hop_up(pose, stance, t) {
    const pump = waveOf(t);
    breathe(pose, 0);
    trunk(pose, {lean: 8, nod: -12});
    flung(pose, stance, 0, 110 + 20 * pump);
    tucked(pose, 0.6 + 0.2 * pump);
}

// where the hands swat at the tickling pointer, in front of the face, across, forward (toward the viewer is less) and up in the
// figure's units; how many swats a play of it has, and how much it giggles, shaking
// where the swatting hands go, across, forward and up in the figure's units, with no pointer to aim at; how far across and how low and high
// a swat aimed at the pointer reaches; how many swats a play holds and how far it giggles
const SWAT = {at: [0.3, -0.8, 2.45], across: 1.5, low: 1.1, high: 3.4, swats: 4, giggle: 4};

// where a swat aims: at the pointer, `pose.at` in shares of the picture (lookToward), brought within the arms' reach, or straight ahead
function swatTarget(pose) {
    if (!pose.at) return null;
    const across = Math.min(Math.max((pose.at.x - 0.5) * FRAMED_HEIGHT, -SWAT.across), SWAT.across);
    const up = Math.min(Math.max(FRAMED_MIDDLE + (0.5 - pose.at.y) * FRAMED_HEIGHT, SWAT.low), SWAT.high);
    return new THREE.Vector3(across, SWAT.at[1], up);
}

// tickled by the mouse pointer it swats at it, giggling, its eyes squeezed shut laughing, a kawaii > <: with the pointer in sight each swat
// goes at the pointer, with the hand on its side, else with one hand and then the other at the air before it
function tickle_swat(pose, stance, t) {
    const swat = t * SWAT.swats;
    const aimed = swatTarget(pose);
    const which = aimed ? (aimed.x * SIDES.l > 0 ? "l" : "r") : Math.floor(swat) % 2 ? "l" : "r";
    const out = Math.sin(Math.PI * (swat % 1));
    breathe(pose, t);
    trunk(pose, {tilt: SWAT.giggle * Math.sin(2 * Math.PI * swat * 2), nod: -3});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, Object.keys(SIDES));
    for (const side of Object.keys(SIDES)) {
        const [x, y, z] = SWAT.at;
        const target = side === which && aimed ? pose.withinReach(side, aimed, 0.95) : new THREE.Vector3(SIDES[side] * x, y, z);
        handTo(pose, side, side === which ? out : 0.25, target, new THREE.Vector3(1, -0.4, -0.3));
    }
    pose.squeezeEyes(1);
}

// where the disco dance points its hands, across, forward (toward the viewer is less) and up in the figure's units: one up and out over
// its shoulder, the other down and out by its hip
const DISCO = {up: [1.2, -0.3, 2.85], down: [0.95, -0.25, 1.3], sway: 12, bounce: 0.18};

// dances the classic disco move under the disco ball (acts.js disco): one arm pointing up and the other down, switching sides each beat,
// the hips swaying toward the arm pointing down and the knees bouncing on every beat
function disco(pose, stance, t) {
    const {beats} = ACTS.disco;
    const beat = t * beats;
    const which = Math.floor(beat) % 2 ? 1 : -1;
    const swing = Math.sin(Math.PI * Math.min((beat % 1) * 3, 1) * 0.5);
    const into = partOf(t, [0, 0.06]) * (1 - partOf(t, [0.94, 1]));
    breathe(pose, t);
    trunk(pose, {tilt: which * DISCO.sway * swing * into, nod: -4});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, Object.keys(SIDES));
    for (const side of Object.keys(SIDES)) {
        const sign = SIDES[side];
        const [x, y, z] = sign === which ? DISCO.up : DISCO.down;
        handTo(pose, side, into, new THREE.Vector3(sign * x, y, z), new THREE.Vector3(1, -0.3, sign === which ? 0.2 : -0.6));
    }
    fold(pose, DISCO.bounce * Math.abs(Math.sin(Math.PI * beat)) * into);
    eyesAs(pose, "amused", into);
}

// where the hands hold the rifle for the bug shot, across toward the free hand's side, forward (toward the viewer is less) and up in the
// figure's units: the trigger hand at the stock, the other forward on it near the middle, and the trigger hand reaching behind the back
const RIFLE = {trigger: [0.5, -0.4, 1.7], fore: [0.12, -0.45, 1.85], behind: [0.45, 0.45, 1.45]};

// shoots the bug a passing run brings (acts.js bug_shot): reaches behind its back for the rifle, brings it up at the bug out on its free
// hand's side, turned toward it, each shot kicking it back, and lowers it once the bug has splattered
function bug_shot(pose, stance, t) {
    const act = ACTS.bug_shot;
    const middle = (act.draw[0] + act.draw[1]) / 2;
    const reach = partOf(t, [act.draw[0], middle]) * (1 - partOf(t, [middle, act.draw[1]]));
    const aim = partOf(t, [middle, act.draw[1]]) * (1 - partOf(t, [act.drops[0] + 0.05, act.drops[0] + 0.2]));
    const shot = Math.min(Math.max((t - act.shots[0]) / (act.shots[1] - act.shots[0]), 0), 1) * act.count;
    const kick = t > act.shots[0] && t < act.shots[1] ? Math.max(0, 1 - (shot % 1) * 3) : 0;
    const side = freeSide(stance);
    const sign = SIDES[side];
    breathe(pose, t);
    trunk(pose, {twist: -sign * 25 * aim, lean: 4 * aim - 5 * kick});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, Object.keys(SIDES));
    const at = (point, mirror = sign) => new THREE.Vector3(mirror * point[0], point[1], point[2]);
    if (reach > aim) handTo(pose, side, reach, at(RIFLE.behind), new THREE.Vector3(1, 0.5, -0.5));
    else handTo(pose, side, aim, at(RIFLE.trigger), new THREE.Vector3(1, -0.2, -0.4));
    handTo(pose, side === "l" ? "r" : "l", aim, at(RIFLE.fore), new THREE.Vector3(-1, -0.4, -0.4));
    eyesAs(pose, "amused", aim);
}

// where the hands hold the pogo stick's handles, across, forward (toward the viewer is less) and up in the figure's units, and where the
// hand reaching behind its back for the stick goes
const POGO_GRIP = [0.42, -0.55, 1.55];
const POGO_BEHIND = [0.45, 0.45, 1.45];

// up a high place on a pogo stick (acts.js pogo): reaches behind its back and brings the stick round, holds both handles and bounces,
// the knees giving at the foot of each bounce, springs up and lets the stick go at the top of the throw
function pogo(pose, stance, t) {
    const act = ACTS.pogo;
    const reach = partOf(t, [act.draw[0], act.draw[1] * 0.5]) * (1 - partOf(t, [act.draw[1] * 0.5, act.draw[1]]));
    const held = partOf(t, [act.draw[1] * 0.6, act.draw[1]]) * (1 - partOf(t, act.release));
    const hop = pogoHop(pogoBounces(), (t - act.bounces[0]) / (act.bounces[1] - act.bounces[0]));
    const give = t > act.bounces[0] && t < act.bounces[1] ? 1 - Math.sin(Math.PI * hop.s) : 0;
    breathe(pose, t);
    trunk(pose, {lean: 6 * held, nod: -6 * held});
    pose.putAway(...IN_HAND);
    armsAtRest(pose, stance, Object.keys(SIDES));
    const [x, y, z] = POGO_GRIP;
    const [bx, by, bz] = POGO_BEHIND;
    for (const side of Object.keys(SIDES)) {
        const sign = SIDES[side];
        if (side === "r" && reach > held) handTo(pose, side, reach, new THREE.Vector3(sign * bx, by, bz), new THREE.Vector3(1, 0.5, -0.5));
        else handTo(pose, side, held, new THREE.Vector3(sign * x, y, z), new THREE.Vector3(1, -0.2, -0.4));
    }
    fold(pose, 0.35 * give * held);
    eyesAs(pose, "amused", held);
}

// where each hand holds its rope of the swing, beside the head, in the figure's units across, forward and up: the ropes' half span apart
// (acts.js rope_swing ties, as a share of the 5.4 units the picture frames)
const ROPE_GRIP = [(ACTS.rope_swing.ties * FRAMED_HEIGHT) / 2, -0.1, 2.6];

// sits on the rope swing's seat holding both ropes up beside its head, leaning back and pumping its legs with each swing (acts.js
// swingAngle)
function rope_swing(pose, stance, t) {
    const pump = swingAngle(t) / ACTS.rope_swing.sway;
    breathe(pose, t);
    trunk(pose, {lean: -5 * pump, nod: -4});
    pose.putAway(...IN_HAND);
    const [x, y, z] = ROPE_GRIP;
    armsAtRest(pose, stance, Object.keys(SIDES));
    for (const side of Object.keys(SIDES)) {
        handTo(pose, side, 1, pose.carried(new THREE.Vector3(SIDES[side] * x, y, z)), new THREE.Vector3(1, 0, -0.4));
        pose.face(`hand_${side}`, {z: -SIDES[side] * 90});
    }
    pose.swing(1.2 * pump);
    eyesAs(pose, "amused");
}

// hangs from the parachute's lines with both hands up holding them, the legs dangling and swinging a little
function chute(pose, stance, t) {
    const swing = waveOf(t);
    breathe(pose, t);
    trunk(pose, {nod: -6, tilt: 3 * swing});
    flung(pose, stance, 0, 150);
    pose.putAway(...IN_HAND);
    tucked(pose, 0.15, 6 * swing);
    eyesAs(pose, "amused");
}

// The figure looks all about through binoculars held up to its eyes, sweeping slowly from one side to the other, the hand keeping them
// before the eyes as the head turns
function binoculars(pose, stance, t) {
    const turn = ACTED.sweep * waveOf(t, ACTS.binoculars.sweep);
    trunk(pose, {twist: turn, nod: -4});
    const side = freeSide(stance);
    const [x, y, z] = ACTED.binoculars;
    const at = new THREE.Vector3(SIDES[side] * x, y, z).applyAxisAngle(new THREE.Vector3(0, 0, 1), radians(turn));
    actHand(pose, stance, 1, [SIDES[side] * at.x, at.y, at.z], {x: -60});
}

// shines a flashlight held out low into a dark corner beside it, the beam moving about in it, leaning to look
function flashlight(pose, stance, t) {
    const sweep = glanceOf(t);
    const [x, y, z] = ACTED.torch;
    breathe(pose, 0);
    trunk(pose, {lean: 10, nod: 18, turn: -SIDES[freeSide(stance)] * 20});
    actHand(pose, stance, 1, [x, y, z - ACTED.torchSweep * sweep], {x: -10});
    eyesAs(pose, "reading");
}

// crouches, lifts a corner of the floor beside it with the free hand and peeks under it, then lets it down and stands
function peek_under(pose, stance, t) {
    const act = ACTS.peek_under;
    const down = partOf(t, [0, act.lift[0] + 0.1]) * (1 - partOf(t, [act.down[1], 1]));
    const lifted = partOf(t, act.lift) * (1 - partOf(t, act.down));
    const peek = partOf(t, act.peek) * (1 - partOf(t, act.down));
    crouch(pose, ACTED.crouch * down);
    breathe(pose, 0);
    trunk(pose, {lean: ACTED.peekLean * down, nod: 14 * down + 10 * peek, turn: -SIDES[freeSide(stance)] * 24 * peek, tilt: 8 * peek});
    const [x, y, z] = ACTED.corner;
    actHand(pose, stance, down, [x, y, z + ACTED.lift * lifted]);
    eyesAs(pose, "reading", peek);
}

// The figure types on and stops to think now and then, a hand at its chin and the other tapping slowly at the laptop
function type_ponder(pose, stance, t) {
    const side = freeSide(stance);
    const sign = SIDES[side];
    const [x, y, z] = TYPING_HANDS;
    breathe(pose, t);
    trunk(pose, {lean: 4, nod: 14 + 3 * waveOf(t), turn: -sign * 6, tilt: -sign * 4});
    handsTo(pose, stance, 1, [x, y, z + 0.03 * Math.max(waveOf(t, 2), 0)]);
    chinOnHand(pose, side);
    pose.holdLaptop();
    eyesAs(pose, "reading");
}

// The figure wipes its brow with the back of the free hand in a break from the work, and blows out
function wipe_brow(pose, stance, t) {
    const {u, ready} = gestureTime(t, ACTING.greetingFrames);
    const across = swell(u, 0.3, 0.75);
    breathe(pose, 0);
    trunk(pose, {lean: -4 * ready, nod: -10 * ready});
    actHand(pose, stance, ready, between3([0.7, -0.62, 2.34], [0.3, -0.84, 2.38], across), {x: -40});
    pose.shutEyes(1 - 0.6 * across);
}

// The figure waves up at the UFO with the free hand, stepping back as the watch does
function wave_up(pose, stance, t) {
    const {back} = pose.sky ?? {back: 0};
    pose.lift("root", {y: SKY.step * back, z: SKY.hop * Math.sin(Math.PI * back)});
    breathe(pose, t);
    trunk(pose, {lean: -SKY.lean * back});
    const side = freeSide(stance);
    armsAtRest(pose, stance, [side]);
    waveArm(pose, side, t);
    emptyHand(pose);
    eyesAs(pose, "amused");
}

// What a posture does to the legs of whatever clip is drawn in it: what it sets before the clip poses the body, and what it lays over the
// legs after. Standing, the clip has the legs to itself, and so does a clip that poses its own `legs`, as the push walks on bent knees.
export const LEGS = {
    sit: {under: seat, over: seatedLegs},
    lounge: {under: seat, over: loungedLegs},
    composed: {under: seat, over: composedLegs},
    walk: {under: strideUnder, over: strideLegs},
};

// The postures a clip is drawn in: a gesture standing, seated on an edge, lounging or sitting composed on a floor's top or on the move, its legs laid by the posture; a move of the whole
// body on its feet alone; a hang from its hands alone; and the laptop only on a lap
const GESTURE = ["stand", "sit", "lounge", "composed", "walk"];
const MOVE = ["stand"];
const HANGING = ["hang"];
const ON_A_LAP = ["sit", "lounge"];
// a gesture whose hands are both up off the floor, so never drawn lounging or sitting composed, where both hands lean on it
const HANDS_UP = ["stand", "sit", "walk"];
// the seconds the figure types at its laptop, once it has started, before anything else may take it off it
export const TYPING_SECONDS = 5;

// Every clip plays out before another starts, so the figure never reads as cut off: one that plays once to its end, a loop to the end of
// its cycle or of the stretch it names as `leaves`. An `interruptible` clip gives way the moment something else is wanted instead, as the
// walk does the moment there is nowhere left to go and a fall the moment its feet meet the ground; a beat, a reaction, a jump or a
// landing never is. A clip that names `marks` has the page draw its mark drifting up from the head in the frames it names, from one to
// the next of each pair: the Z of sleep, the notes of a whistled tune. A clip that `cuts` in takes over at once from whatever plays, as the
// figure stops what it does to watch the UFO or swats at a tickle. A clip with its `ownLook` keeps it, the head never turned away to watch
// the bar under it or the UFO, nor turned toward the viewer for a look in the eyes, as the figure faces the user dancing or laughing, or
// pushes a parcel with its head going with its lean. A clip that names `least` plays at least that many seconds before anything else may
// take over, the beats waiting behind it, as typing does; one that is `aside` is drawn seated turned aside from the viewer, never square
// to it, as at the laptop.

export const CLIPS = [
    {name: "idle", frames: 24, fps: 8, loops: true, leaves: 8, postures: GESTURE, pose: idle},
    {name: "nod", frames: 10, fps: 12, loops: false, postures: GESTURE, pose: nod},
    {name: "hand_rub", frames: ACTS.hand_rub.frames, fps: ACTS.hand_rub.fps, loops: false, postures: GESTURE, pose: hand_rub},
    {name: "ponder", frames: ACTS.ponder.frames, fps: ACTS.ponder.fps, loops: false, ownLook: true, postures: GESTURE, pose: ponder},
    {name: "shake", frames: 12, fps: 12, loops: false, postures: GESTURE, pose: shake},
    {name: "wave", frames: 12, fps: 12, loops: true, postures: GESTURE, pose: wave},
    {name: "think", frames: 24, fps: 6, loops: true, leaves: 12, postures: GESTURE, pose: think},
    {name: "celebrate", frames: 12, fps: 10, loops: true, postures: MOVE, pose: celebrate},
    {name: "sleep", frames: ACTING.yawnFrames + SLEEP_FRAMES, intro: ACTING.yawnFrames, leaves: SLEEP_FRAMES, fps: 6, loops: true, postures: GESTURE, marks: {mark: "Z", frames: [[ACTING.yawnFrames, ACTING.yawnFrames + SLEEP_FRAMES]]}, pose: sleep},
    {name: "walk", frames: 12, fps: 12, loops: true, interruptible: true, postures: MOVE, pose: walk},
    {name: "walk_in", frames: 40, fps: 12, loops: false, postures: MOVE, pose: walk_in},
    {name: "run_in", frames: 28, fps: 12, loops: false, postures: MOVE, pose: run_in},
    {name: "pull_ups", frames: 24, fps: 10, loops: true, postures: MOVE, pose: pull_ups},
    {name: "hang_l", frames: 24, fps: 8, loops: true, leaves: 8, postures: HANGING, pose: dangle("l")},
    {name: "hang_r", frames: 24, fps: 8, loops: true, leaves: 8, postures: HANGING, pose: dangle("r")},
    {name: "enter", frames: 36, fps: 12, loops: false, postures: MOVE, pose: enter},
    {name: "exit", frames: 28, fps: 12, loops: false, postures: MOVE, pose: exit},
    {name: "search", frames: 80, fps: 10, loops: true, postures: GESTURE, pose: search},
    {name: "read", frames: READ_FRAMES, fps: READING.fps, loops: true, intro: READING.intro, outro: READING.outro, leaves: READING.pageEvery, postures: GESTURE, pose: read},
    {name: "write", frames: HELD_FRAMES, intro: ACTING.intro, outro: ACTING.outro, leaves: ACTING.hold, fps: ACTING.fps, loops: true, postures: GESTURE, pose: writing},
    {name: "waiting", frames: WAIT_FRAMES, intro: WAIT.intro, outro: WAIT.outro, leaves: WAIT.hold, fps: ACTING.fps, loops: true, postures: ["stand", "sit"], pose: waiting},
    {name: "compacting", frames: HELD_FRAMES, intro: ACTING.intro, outro: ACTING.outro, leaves: ACTING.hold, fps: ACTING.compactFps, loops: true, postures: GESTURE, pose: compacting},
    {name: "yawn", frames: ACTING.yawnFrames, fps: ACTING.fps, loops: false, postures: GESTURE, pose: yawn},
    {name: "rest", frames: REST.frames, fps: REST.fps, loops: false, postures: MOVE, marks: {mark: "♪", frames: REST.tunes.map((tune) => tune.map((share) => share * REST.frames))}, pose: rest},
    {name: "whistle", frames: ACTING.pastimeFrames, fps: ACTING.fps, loops: false, postures: GESTURE, voices: ["coach"], pose: whistle},
    {name: "phone_call", frames: ACTS.phone_call.frames, fps: ACTS.phone_call.fps, loops: false, postures: MOVE, pose: phone_call},
    {name: "sip", frames: ACTING.pastimeFrames, fps: ACTING.fps, loops: false, postures: GESTURE, voices: ["colleague"], pose: sip},
    {name: "headphones", frames: ACTING.pastimeFrames, fps: ACTING.fps, loops: false, postures: GESTURE, voices: ["homie"], pose: headphones},
    {name: "shield_polish", frames: ACTING.pastimeFrames, fps: ACTING.fps, loops: false, postures: GESTURE, voices: ["squire"], pose: shieldPolish},
    {name: "bow", frames: ACTING.greetingFrames, fps: ACTING.fps, loops: false, postures: GESTURE, voices: ["butler"], pose: bow},
    {name: "salute", frames: ACTING.greetingFrames, fps: ACTING.fps, loops: false, postures: GESTURE, voices: ["squire"], pose: salute},
    {name: "startled", frames: ACTING.hopFrames, fps: ACTING.fps, loops: false, postures: GESTURE, pose: startled},
    {name: "stumble", frames: ACTING.stumbleFrames, fps: ACTING.fps, loops: false, postures: ["walk"], pose: stumble},
    {name: "glance", frames: ACTING.greetingFrames, fps: ACTING.fps, loops: false, postures: GESTURE, pose: glance},
    {name: "work", frames: WORK.blows * WORK.blowFrames, fps: WORK.fps, loops: true, postures: ["stand", "sit"], pose: work},
    {name: "inspect", frames: INSPECTING.frames, fps: INSPECTING.fps, loops: true, postures: ["stand"], pose: inspect},
    {name: "point", frames: 12, fps: 8, loops: true, postures: GESTURE, pose: point},
    {name: "watch", frames: 8, fps: 8, loops: true, cuts: true, postures: ["stand", "sit"], pose: watch},
    {name: "push", frames: SHOVE.intro + SHOVE.stride, intro: SHOVE.intro, fps: SHOVE.fps, loops: true, legs: true, ownLook: true, postures: ["walk", "stand"], pose: push},
    {name: "jump", frames: 16, fps: 20, loops: false, postures: MOVE, pose: jump},
    {name: "tickle_swat", frames: 24, fps: 16, loops: false, cuts: true, ownLook: true, postures: GESTURE, pose: tickle_swat},
    {name: "disco", frames: ACTS.disco.frames, fps: ACTS.disco.fps, loops: false, ownLook: true, postures: MOVE, pose: disco},
    {name: "bug_shot", frames: ACTS.bug_shot.frames, fps: ACTS.bug_shot.fps, loops: false, postures: MOVE, pose: bug_shot},
    {name: "pogo", frames: ACTS.pogo.frames, fps: ACTS.pogo.fps, loops: false, postures: MOVE, pose: pogo},
    {name: "fall", frames: 12, fps: 12, loops: false, interruptible: true, postures: MOVE, pose: fall},
    {name: "backflip", frames: 22, fps: 20, loops: false, postures: MOVE, pose: backflip},
    {name: "land", frames: LANDING.frames, fps: LANDING.fps, loops: false, postures: MOVE, pose: land},
    {name: "type", frames: 24, fps: 8, loops: true, leaves: 8, least: TYPING_SECONDS, aside: true, postures: ON_A_LAP, pose: type},
    {name: "joy", frames: ACTS.joy.frames, fps: ACTS.joy.fps, loops: false, postures: GESTURE, pose: joy},
    {name: "dismay", frames: 28, fps: 10, loops: false, postures: GESTURE, pose: dismay},
    {name: "polish", frames: 40, fps: 12, loops: false, postures: GESTURE, voices: ["butler"], pose: polish},
    {name: "stretch", frames: 24, fps: 8, loops: false, postures: GESTURE, pose: stretch},
    {name: "squire_chase", frames: 24, fps: 12, loops: false, postures: MOVE, pose: squire_chase},
    {name: "pointed", frames: 20, fps: 10, loops: false, postures: MOVE, pose: pointed},
    {name: "hat_tip", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["butler"], pose: hat_tip},
    {name: "monocle", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["butler"], pose: monocle},
    {name: "toast", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["butler"], pose: toast},
    {name: "shaka", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["homie"], pose: shaka},
    {name: "shades", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["homie"], pose: shades},
    {name: "fire", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["homie"], pose: fire},
    {name: "thumbs_up", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["colleague"], pose: thumbs_up},
    {name: "peer", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["colleague"], pose: peer},
    {name: "thanks", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, pose: thanks},
    {name: "party_popper", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["coach"], pose: party_popper},
    {name: "flex", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["coach"], pose: flex},
    {name: "trophy", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["coach"], pose: trophy},
    {name: "sword", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["squire"], pose: sword},
    {name: "shield_up", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["squire"], pose: shield_up},
    {name: "castle", frames: REACTING.frames, fps: REACTING.fps, loops: false, postures: GESTURE, voices: ["squire"], pose: castle},
    {name: "ask_sign", frames: ACTS.ask_sign.frames, fps: ACTS.ask_sign.fps, loops: false, postures: GESTURE, pose: ask_sign},
    {name: "scroll", frames: ACTS.scroll.frames, fps: ACTS.scroll.fps, loops: false, ownLook: true, postures: GESTURE, pose: scroll},
    {name: "file_card", frames: ACTS.file_card.frames, fps: ACTS.file_card.fps, loops: false, postures: MOVE, pose: file_card},
    {name: "pack_box", frames: ACTS.pack_box.intro + ACTS.pack_box.hold + ACTS.pack_box.outro, intro: ACTS.pack_box.intro, outro: ACTS.pack_box.outro, leaves: ACTS.pack_box.hold, fps: ACTS.pack_box.fps, loops: true, postures: MOVE, pose: pack_box},
    {name: "press", frames: ACTS.press.intro + ACTS.press.hold + ACTS.press.outro, intro: ACTS.press.intro, outro: ACTS.press.outro, leaves: ACTS.press.hold, fps: ACTS.press.fps, loops: true, postures: GESTURE, pose: press},
    {name: "vacuum", frames: ACTS.vacuum.intro + ACTS.vacuum.hold + ACTS.vacuum.outro, intro: ACTS.vacuum.intro, outro: ACTS.vacuum.outro, leaves: ACTS.vacuum.hold, fps: ACTS.vacuum.fps, loops: true, postures: MOVE, pose: vacuum},
    {name: "eager", frames: EAGERNESS.intro + EAGERNESS.hold + EAGERNESS.outro, intro: EAGERNESS.intro, outro: EAGERNESS.outro, leaves: EAGERNESS.hold, fps: EAGERNESS.fps, loops: true, postures: MOVE, pose: eager},
    {name: "fume", frames: ACTS.fume.frames, fps: ACTS.fume.fps, loops: false, cuts: true, postures: MOVE, pose: fume},
    {name: "look_left", frames: GLANCE.frames, fps: GLANCE.fps, loops: false, postures: GESTURE, pose: glanceAt(-1, 0)},
    {name: "look_right", frames: GLANCE.frames, fps: GLANCE.fps, loops: false, postures: GESTURE, pose: glanceAt(1, 0)},
    {name: "look_up", frames: GLANCE.frames, fps: GLANCE.fps, loops: false, postures: GESTURE, pose: glanceAt(0, 1)},
    {name: "tumble", frames: TUMBLE.frames, fps: TUMBLE.fps, loops: false, postures: MOVE, pose: tumble},
    {name: "ledge_sit", frames: 32, fps: 8, loops: true, leaves: 8, postures: ON_A_LAP, pose: ledge_sit},
    {name: "hop_up", frames: 8, fps: 16, loops: true, interruptible: true, cuts: true, postures: MOVE, pose: hop_up},
    {name: "rope_swing", frames: ACTS.rope_swing.intro + ACTS.rope_swing.hold + ACTS.rope_swing.outro, intro: ACTS.rope_swing.intro, outro: ACTS.rope_swing.outro, leaves: ACTS.rope_swing.hold, fps: ACTS.rope_swing.fps, loops: true, postures: ON_A_LAP, pose: rope_swing},
    {name: "chute", frames: ACTS.chute.frames, fps: ACTS.chute.fps, loops: true, interruptible: true, cuts: true, postures: MOVE, pose: chute},
    {name: "binoculars", frames: ACTS.binoculars.frames, fps: ACTS.binoculars.fps, loops: true, postures: HANDS_UP, pose: binoculars},
    {name: "flashlight", frames: ACTS.flashlight.frames, fps: ACTS.flashlight.fps, loops: true, postures: MOVE, pose: flashlight},
    {name: "peek_under", frames: ACTS.peek_under.frames, fps: ACTS.peek_under.fps, loops: true, postures: MOVE, pose: peek_under},
    {name: "type_ponder", frames: 24, fps: 6, loops: true, leaves: 8, least: TYPING_SECONDS, aside: true, postures: ON_A_LAP, pose: type_ponder},
    {name: "wipe_brow", frames: ACTING.greetingFrames, fps: ACTING.fps, loops: false, postures: GESTURE, pose: wipe_brow},
    {name: "wave_up", frames: 12, fps: 12, loops: true, cuts: true, postures: ["stand", "sit"], pose: wave_up},
];

// An eye closes about its own middle before the head carries it, as rig.Figure.shut_eyes scales the eye object
const SKINNED = /* glsl */ `
    #include <common>
    #include <skinning_pars_vertex>
    attribute vec3 hullNormal;
    uniform float push;
    uniform float openness;
    uniform float eyeMiddle;
    uniform float eyeHeight;
    uniform vec2 eyeShift;
    varying vec3 worldNormal;
    varying vec3 worldPosition;
    varying vec3 localPosition;

    void main() {
        localPosition = position;
        #include <beginnormal_vertex>
        #ifdef HULL
            objectNormal = hullNormal;
        #endif
        #include <skinbase_vertex>
        #include <skinnormal_vertex>
        #include <begin_vertex>
        transformed.y = eyeMiddle + (transformed.y - eyeMiddle) * openness;
        transformed.xy += eyeShift * eyeHeight;
        #include <skinning_vertex>
        transformed += normalize(objectNormal) * push;
        worldNormal = normalize(mat3(modelMatrix) * objectNormal);
        worldPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
    }
`;

// Every flat part is lit by the light bulb over the head too while it glows (LIGHT_BULB): as warm as `bulbGlow`, on the faces turned to the
// bulb at `bulbAt`, weaker with the square of the distance by `bulbFalloff`
const FLAT = /* glsl */ `
    uniform vec3 colour;
    uniform vec3 light;
    uniform vec3 shade;
    uniform float litFrom;
    uniform vec3 bulbAt;
    uniform vec3 bulbGlow;
    uniform float bulbFalloff;
    varying vec3 worldNormal;
    varying vec3 worldPosition;

    void main() {
        vec3 normal = normalize(worldNormal);
        if (!gl_FrontFacing) {
            normal = -normal;
        }
        float lit = step(litFrom, dot(normal, light));
        vec3 toBulb = bulbAt - worldPosition;
        float bulb = max(dot(normal, normalize(toBulb)), 0.0) / (1.0 + dot(toBulb, toBulb) * bulbFalloff);
        gl_FragColor = vec4(colour * mix(shade, vec3(1.0), lit) + bulbGlow * bulb * mix(colour, vec3(1.0), 0.35), 1.0);
        #include <colorspace_fragment>
    }
`;

// The visor, shaded as any flat part, and lit as a screen as an old CRT powers up (figure/visor.js): a band about its middle reaching
// `across` and `open` of the way to its sides and its top and bottom, white with `flash` and else `glow`, as strong as `lit`, the rest
// of it dark. The lit band is a grid of square pixels `pitch` apart, the lines between them `gap` of a pixel wide and darker, as a big
// screen is seen up close.
export const SCREEN = {pitch: 0.1, gap: 0.24, dark: 0.3};
const SCREEN_FRAGMENT = /* glsl */ `
    uniform vec3 colour;
    uniform vec3 light;
    uniform vec3 shade;
    uniform float litFrom;
    uniform vec3 glow;
    uniform float lit;
    uniform float across;
    uniform float open;
    uniform float flash;
    uniform float core;
    uniform vec2 middle;
    uniform vec2 extent;
    uniform float pitch;
    uniform float gap;
    uniform float dark;
    varying vec3 worldNormal;
    varying vec3 worldPosition;
    varying vec3 localPosition;

    void main() {
        vec3 normal = normalize(worldNormal);
        if (!gl_FrontFacing) {
            normal = -normal;
        }
        vec3 shaded = colour * mix(shade, vec3(1.0), step(litFrom, dot(normal, light)));
        vec2 from = abs(localPosition.xy - middle) / extent;
        float band = step(from.x, across) * step(from.y, open);
        vec2 cell = fract(worldPosition.xy / pitch);
        float pixel = step(gap, cell.x) * step(gap, cell.y);
        float centre = max(1.0 - length(from), 0.0);
        vec3 lit = glow * mix(dark, 1.0, pixel);
        vec3 screen = mix(lit + (vec3(1.0) - glow) * core * centre * centre * pixel, vec3(1.0), flash);
        gl_FragColor = vec4(mix(shaded * (1.0 - step(0.001, lit + flash) * 0.6), screen, band * max(lit, flash)), 1.0);
        #include <colorspace_fragment>
    }
`;

// the visor's material: a flat part's, which lights as a screen, its band measured from the visor's own middle out to its edges
function screenMaterial(mesh) {
    const material = flatMaterial(mesh);
    material.fragmentShader = SCREEN_FRAGMENT;
    const bounds = new THREE.Box3().setFromBufferAttribute(mesh.geometry.attributes.position);
    const middle = bounds.getCenter(new THREE.Vector3());
    const extent = bounds.getSize(new THREE.Vector3()).multiplyScalar(0.5);
    Object.assign(material.uniforms, {
        glow: {value: new THREE.Vector3()}, lit: {value: 0}, across: {value: 0}, open: {value: 0}, flash: {value: 0}, core: {value: VISOR.core},
        middle: {value: new THREE.Vector2(middle.x, middle.y)}, extent: {value: new THREE.Vector2(extent.x, extent.y)},
        pitch: {value: SCREEN.pitch}, gap: {value: SCREEN.gap}, dark: {value: SCREEN.dark},
    });
    return material;
}

const LINE = /* glsl */ `
    uniform vec3 colour;

    void main() {
        gl_FragColor = vec4(colour, 1.0);
        #include <colorspace_fragment>
    }
`;

function vertexUniforms(mesh, push) {
    const position = mesh.geometry.attributes.position;
    let middle = 0;
    let [low, high] = [Infinity, -Infinity];
    for (let i = 0; i < position.count; i++) {
        middle += position.getY(i) / position.count;
        [low, high] = [Math.min(low, position.getY(i)), Math.max(high, position.getY(i))];
    }
    // a quantized glb scales each mesh up from small units, so the outline is pushed in the mesh's own units
    return {
        push: {value: push / mesh.getWorldScale(new THREE.Vector3()).x},
        openness: {value: 1},
        eyeMiddle: {value: middle},
        eyeHeight: {value: high - low},
        eyeShift: {value: new THREE.Vector2()},
    };
}

function flatMaterial(mesh) {
    const {r, g, b} = mesh.material.color;
    return new THREE.ShaderMaterial({
        vertexShader: SKINNED,
        fragmentShader: FLAT,
        side: THREE.DoubleSide,
        uniforms: {
            ...vertexUniforms(mesh, 0),
            colour: {value: new THREE.Vector3(r, g, b)},
            light: {value: LIGHT_FROM.clone().normalize().applyMatrix4(TO_GLB)},
            shade: {value: SHADE},
            litFrom: {value: LIT_FROM},
            bulbAt: {value: new THREE.Vector3()},
            bulbGlow: {value: new THREE.Vector3()},
            bulbFalloff: {value: LIGHT_BULB.falloff},
        },
    });
}

function outlineMaterial(mesh) {
    return new THREE.ShaderMaterial({
        vertexShader: SKINNED,
        fragmentShader: LINE,
        side: THREE.BackSide,
        defines: {HULL: ""},
        uniforms: {...vertexUniforms(mesh, OUTLINE_WIDTH), colour: {value: OUTLINE_COLOUR}},
    });
}

// Solidify pushes each vertex along its smooth normal; a flat-shaded mesh arrives split, so its corners are averaged
// again, leaving out a corner facing the other way, which is the back layer of a two-sided piece at the same point
const SAME_VERTEX = -0.5;

function addHullNormals(geometry) {
    const position = geometry.attributes.position;
    const normals = Array.from({length: position.count}, (_, i) => new THREE.Vector3().fromBufferAttribute(geometry.attributes.normal, i));
    const corners = new Map();
    const key = (i) => `${position.getX(i).toFixed(5)},${position.getY(i).toFixed(5)},${position.getZ(i).toFixed(5)}`;
    for (let i = 0; i < position.count; i++) {
        const group = corners.get(key(i)) ?? [];
        group.push(i);
        corners.set(key(i), group);
    }
    const hull = new Float32Array(position.count * 3);
    for (let i = 0; i < position.count; i++) {
        const sum = new THREE.Vector3();
        for (const j of corners.get(key(i)).filter((j) => normals[i].dot(normals[j]) > SAME_VERTEX)) {
            sum.add(normals[j]);
        }
        sum.normalize().toArray(hull, i * 3);
    }
    geometry.setAttribute("hullNormal", new THREE.BufferAttribute(hull, 3));
}

function handsHolding(meshes, items) {
    const sides = new Set();
    for (const mesh of meshes.filter((mesh) => items.has(mesh.userData.item))) {
        sides.add(new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3()).x >= 0 ? "l" : "r");
    }
    return sides;
}

function rigOf(root) {
    const bones = [];
    root.traverse((node) => node.isBone && bones.push(node));
    const parents = new Map(bones.map((bone) => [bone.name, bone.parent.isBone ? bone.parent.name : ""]));
    const rest = new Map(bones.map((bone) => [bone.name, bone.matrixWorld.clone()]));
    const heads = new Map(bones.map((bone) => [bone.name, toBlender(new THREE.Vector3().setFromMatrixPosition(bone.matrixWorld))]));
    const along = new Map(
        bones.map((bone) => [bone.name, new THREE.Vector3().setFromMatrixColumn(bone.matrixWorld, 1).transformDirection(FROM_GLB)])
    );
    const eyes = [];
    root.traverse((mesh) => {
        if (!mesh.isSkinnedMesh || !mesh.name.startsWith("eye_") || !mesh.userData.hull) return;
        eyes.push(toBlender(new THREE.Box3().setFromBufferAttribute(mesh.geometry.attributes.position).getCenter(new THREE.Vector3()).applyMatrix4(mesh.matrixWorld)));
    });
    return {bones, order: bones.map((bone) => bone.name), parents, rest, heads, along, eyes};
}

// The glb's bytes; a host that serves no .glb, such as a claude.ai artifact, carries it as base64 in <url>.txt
async function glbBytes(url) {
    const glb = await fetch(url);
    if (glb.ok) {
        return glb.arrayBuffer();
    }
    const text = await fetch(`${url}.txt`).then((response) => response.text());
    return Uint8Array.from(atob(text), (character) => character.charCodeAt(0)).buffer;
}

// The figure of one voice from its glb, its worn pieces drawn and the body parts they cover left out (rig.assemble)
export async function loadFigure(url, wardrobe, voice) {
    const [bytes, manifest] = await Promise.all([glbBytes(url), fetch(wardrobe).then((response) => response.json())]);
    const bare = voice === "bare";
    const covered = new Set((bare ? [] : manifest.outfits[voice]).flatMap((item) => manifest.assets[item].hide_base_parts));
    return figureOf(bytes, voice, DECODER, (mesh) => !covered.has(mesh.name) && !(bare && mesh.userData.item));
}

// the voices dressed over their glb, each by what dresses it (butler.js)
const DRESSES = {butler: dressButler};

// The figure in a glb's bytes, posed by the clips: every mesh `shows` keeps is drawn, shaded and outlined; `decoder` is where Draco's decoder is served
export async function figureOf(bytes, voice, decoder, shows = () => true) {
    const gltf = await new GLTFLoader().setDRACOLoader(new DRACOLoader().setDecoderPath(decoder)).parseAsync(bytes, "");
    const scene = gltf.scene;
    scene.updateMatrixWorld(true);
    const found = [];
    scene.traverse((node) => node.isSkinnedMesh && found.push(node));
    const meshes = (DRESSES[voice] ?? ((each) => each))(found);
    const eyes = {materials: [], shapes: [], hearts: [], stars: [], squeezed: [], over: []};
    const screens = [];
    const visorHulls = [];
    for (const mesh of meshes) {
        mesh.visible = shows(mesh) && !LEFT_OUT.has(mesh.userData.item) && mesh.userData.item !== TABLET && mesh.userData.item !== CLOTH;
        addHullNormals(mesh.geometry);
        const hull = new THREE.SkinnedMesh(mesh.geometry, outlineMaterial(mesh));
        hull.bind(mesh.skeleton, mesh.bindMatrix);
        hull.visible = mesh.visible;
        mesh.userData.hull = hull;
        hull.userData.item = mesh.userData.item;
        hull.frustumCulled = mesh.frustumCulled = false;
        mesh.material = mesh.name === VISOR_MESH ? screenMaterial(mesh) : flatMaterial(mesh);
        if (mesh.name === VISOR_MESH) screens.push(mesh.material);
        if (mesh.name === VISOR_MESH) visorHulls.push(hull);
        mesh.parent.add(hull);
        hull.position.copy(mesh.position);
        hull.quaternion.copy(mesh.quaternion);
        hull.scale.copy(mesh.scale);
        if (mesh.name.startsWith("eye_")) {
            mesh.material.userData.colour = mesh.material.uniforms.colour.value.toArray();
            eyes.materials.push(mesh.material, hull.material);
            eyes.shapes.push(mesh, hull);
            eyes.hearts.push(shapeOver(mesh, HEART, HEART_COLOUR));
            eyes.stars.push(shapeOver(mesh, STAR, STAR_COLOUR));
            eyes.squeezed.push(Object.assign(shapeOver(mesh, SQUEEZE, SQUEEZE_COLOUR), {userData: {way: mesh.name === "eye_l" ? -1 : 1}}));
            const side = mesh.name === "eye_l" ? 1 : -1;
            for (const [name, {geometry, glows}] of Object.entries(EYE_SHAPES)) {
                eyes.over.push(Object.assign(shapeOver(mesh, geometry, SQUEEZE_COLOUR), {userData: {name, side, halo: false}}));
                if (glows) eyes.over.push(Object.assign(haloOver(mesh, geometry), {userData: {name, side, halo: true}}));
            }
        }
    }
    const carried = meshes.filter((mesh) => mesh.visible);
    const busy = handsHolding(carried, BUSY_ITEMS);
    const tablet = meshes.filter((mesh) => mesh.userData.item === TABLET && shows(mesh));
    const cloth = meshes.filter((mesh) => mesh.userData.item === CLOTH && shows(mesh));
    const stance = {
        voice,
        level: handsHolding(carried, LEVEL_ITEMS),
        busy,
        carried: handsHolding(carried, IN_HAND),
        free: new Set(Object.keys(SIDES).filter((side) => !busy.has(side))),
        tablet: handsHolding(tablet, new Set([TABLET])),
        cloth: handsHolding(cloth, new Set([CLOTH])),
        shield: handsHolding(carried, new Set(["squire_shield"])),
    };
    const laptop = laptopOf();
    const book = bookOf();
    const propByName = propsOf();
    scene.add(laptop, book, ...propByName.values());
    const bulbLight = {bulbAt: {value: new THREE.Vector3()}, bulbGlow: {value: new THREE.Vector3()}};
    scene.traverse((node) => node.material?.uniforms?.bulbGlow && Object.assign(node.material.uniforms, bulbLight));
    const hulls = (shown) => shown.flatMap((mesh) => [mesh, mesh.userData.hull]);
    const inHand = carried.filter((mesh) => IN_HAND.has(mesh.userData.item));
    const stowable = hulls(carried.filter((mesh) => mesh.userData.item));
    return {scene, rig: rigOf(scene), stance, eyes, screens, visorHulls, laptop, book, propByName, props: [...propByName.values()], stowable, tablet: hulls(tablet), cloth: hulls(cloth), inHand: hulls(inHand), bulbLight};
}

// A laptop drawn in the flat colours of the chat's own: its hinge at the origin, its keyboard toward the body (-z), its lid opened a little
// past upright with the screen toward the face and the mark on its back
const LAPTOP = {width: 1.7, depth: 0.62, thickness: 0.1, open: 105};
const LAPTOP_COLOURS = {base: 0x474a52, lid: 0x2b2e38, screen: 0x1b1d24, edge: 0xa9adb8, mark: 0x5e64c9};

// a mesh of one flat colour, seen from both sides and never culled, for the props the figure holds
const flat = (geometry, colour) => {
    const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({color: colour, side: THREE.DoubleSide}));
    mesh.frustumCulled = false;
    return mesh;
};

function laptopOf() {
    const {width, depth, thickness, open} = LAPTOP;
    const slab = (colour, w, h, d) => {
        const mesh = flat(new THREE.BoxGeometry(w, h, d), colour);
        mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry), new THREE.LineBasicMaterial({color: LAPTOP_COLOURS.edge})));
        return mesh;
    };
    const base = slab(LAPTOP_COLOURS.base, width, thickness, depth);
    base.position.set(0, thickness / 2, -depth / 2);
    const lid = slab(LAPTOP_COLOURS.lid, width, depth, thickness);
    lid.position.set(0, depth / 2, thickness / 2);
    const screen = flat(new THREE.PlaneGeometry(width * 0.88, depth * 0.82), LAPTOP_COLOURS.screen);
    screen.position.set(0, depth / 2, -0.002);
    const mark = flat(new THREE.CircleGeometry(depth * 0.12, 20), LAPTOP_COLOURS.mark);
    mark.position.set(0, depth / 2, thickness + 0.002);
    const hinge = new THREE.Group();
    hinge.position.y = thickness;
    hinge.rotation.x = radians(open - 90);
    hinge.add(lid, screen, mark);
    const laptop = new THREE.Group();
    laptop.matrixAutoUpdate = false;
    laptop.visible = false;
    laptop.add(base, hinge);
    return laptop;
}

// A block of 1U server units stacked (parcels.js PARCEL), in the same flat colours, for the parcels the figure builds: its front toward the
// viewer, tipped back by as much as shows the strip of its top, its front's bottom edge on the floor at the origin. Each unit's status
// lights run along the left of its front and its vent slits along the right, at these shares of the front's width, the lights' radius and
// the slits' width and height too, of its width and its unit's height
const UNIT_FRONT = {lights: [0.144, 0.267, 0.389, 0.511], light: 0.047, vents: [0.633, 0.711, 0.789, 0.867], vent: [0.033, 0.49]};
const UNIT_COLOURS = {front: 0x1c1e25, top: 0x2c2f39, side: 0x121318, vent: 0x050608, edge: 0x4a4e5c};

function serverBlockOf(perPixel) {
    const width = PARCEL.width * perPixel;
    const tilt = Math.asin(PARCEL.top / PARCEL.width);
    const unit = ((PARCEL.height - PARCEL.top) * perPixel) / Math.cos(tilt) / PARCEL.units;
    const [side, top, front] = [UNIT_COLOURS.side, UNIT_COLOURS.top, UNIT_COLOURS.front].map((colour) => new THREE.MeshBasicMaterial({color: colour}));
    const lights = [];
    const units = Array.from({length: PARCEL.units}, (_, index) => {
        const box = new THREE.Mesh(new THREE.BoxGeometry(width, unit, width), [side, side, top, side, front, side]);
        box.add(new THREE.LineSegments(new THREE.EdgesGeometry(box.geometry), new THREE.LineBasicMaterial({color: UNIT_COLOURS.edge})));
        box.position.set(0, unit * (index + 0.5), -width / 2);
        const onFront = (mesh, share) => {
            mesh.position.set(width * (share - 0.5), 0, width / 2 + 0.002);
            box.add(mesh);
            return mesh;
        };
        lights.push(...UNIT_FRONT.lights.map((share) => onFront(new THREE.Mesh(new THREE.CircleGeometry(width * UNIT_FRONT.light, 12), new THREE.MeshBasicMaterial()), share)));
        UNIT_FRONT.vents.forEach((share) => onFront(flat(new THREE.PlaneGeometry(width * UNIT_FRONT.vent[0], unit * UNIT_FRONT.vent[1]), UNIT_COLOURS.vent), share));
        return box;
    });
    const block = new THREE.Group();
    block.rotation.x = tilt;
    block.add(...units);
    const scene = new THREE.Scene();
    scene.add(block);
    scene.updateMatrixWorld(true);
    return {scene, lights, bounds: new THREE.Box3().setFromObject(block)};
}

// the block's lights as they shine at step `phase` of the blink (parcels.js brightness), lit `lit`
function lightBlock(block, lit, phase) {
    const dark = new THREE.Color(UNIT_COLOURS.front);
    block.lights.forEach((light, index) => {
        const shine = new THREE.Color().setRGB(...LIGHT_COLOURS[lit], THREE.SRGBColorSpace);
        light.material.color.copy(dark.clone().lerp(shine, brightness(lit, phase, index % UNIT_FRONT.lights.length)));
    });
}

// A magnifying glass in the same flat colours, comically large as the figure is drawn small: its handle up its y axis with the handle's
// middle, where the hand closes on it, at the origin, its lens in the plane of x and y above the handle
const GLASS = {radius: 0.52, rim: 0.08, handle: 0.5, grip: 0.07};
const GLASS_COLOURS = {rim: 0x2b2e38, lens: 0xcfe6ff, handle: 0x474a52, edge: 0xa9adb8};
// how far the handle leans forward of upright, held out in front of the body
const GLASS_LEAN = 40;

function glassOf(glass) {
    const {radius, rim, handle, grip} = GLASS;
    const flat = (geometry, colour, more = {}) => {
        const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({color: colour, side: THREE.DoubleSide, ...more}));
        mesh.frustumCulled = false;
        return mesh;
    };
    const ring = flat(new THREE.TorusGeometry(radius, rim, 12, 48), GLASS_COLOURS.rim);
    ring.position.y = handle / 2 + radius;
    ring.add(new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.CircleGeometry(radius + rim, 48)), new THREE.LineBasicMaterial({color: GLASS_COLOURS.edge})));
    const lens = flat(new THREE.CircleGeometry(radius, 48), GLASS_COLOURS.lens, {transparent: true, opacity: 0.35, depthWrite: false});
    lens.position.y = handle / 2 + radius;
    const shaft = flat(new THREE.CylinderGeometry(grip, grip * 1.2, handle, 16), GLASS_COLOURS.handle);
    glass.add(shaft, ring, lens);
}

export const BOOK = {
    width: 0.82,
    height: 1.2,
    cover: 0.055,
    pages: 0.06,
    spine: 0.18,
    inset: 0.035,
    open: 160,
    tilt: 8,
    gripHeight: 0.02,
    gripSide: 0.1,
    closedGrip: 0.2,
    gripBack: 0.6,
    leaf: 0.004,
    curl: 2,
    pageSegments: 12,
    pageBow: 0.24,
    lines: 5,
    lineWidth: 0.004,
};
const BOOK_COLOURS = {cover: 0x6366f1, spine: 0x35374b, pages: 0xf3eedf, paper: 0xfffbef, edge: 0x232532, rule: 0xc6beac};
const bookAngle = (open) => radians((180 - BOOK.open * open) / 2);

function bookContact(side, open) {
    const sign = SIDES[side];
    const reach = side === "l" ? 1 : open;
    return new THREE.Vector3(sign * BOOK.width * reach, BOOK.gripHeight, BOOK.cover / 2)
        .applyAxisAngle(new THREE.Vector3(0, 1, 0), sign * bookAngle(open))
        .add(new THREE.Vector3(sign * BOOK.spine / 2, 0, 0));
}

function bookBasis(open) {
    const across = bookContact("l", open).sub(bookContact("r", open)).normalize();
    const up = new THREE.Vector3(0, 1, 0);
    return new THREE.Matrix4().makeBasis(across, up, across.clone().cross(up));
}

function bookTurn(open) {
    return new THREE.Matrix4().makeRotationX(radians(BOOK.tilt)).multiply(bookBasis(open).invert());
}

function bookGrip(side, open) {
    const basis = bookBasis(open);
    const across = new THREE.Vector3().setFromMatrixColumn(basis, 0);
    const forward = new THREE.Vector3().setFromMatrixColumn(basis, 2);
    return bookContact(side, open).addScaledVector(across, SIDES[side] * (BOOK.gripSide + BOOK.closedGrip * (1 - open))).addScaledVector(forward, -BOOK.gripBack);
}

export const TOOLS = {
    pen: {radius: 0.027, length: 0.58, tip: 0.08, sides: 12, markerScale: 1.8, pencilSides: 6, bandScale: 1.05, bandAt: 1 / 3},
    feather: {at: 1 / 4, points: [[0, 0], [-0.12, 0.18], [-0.08, 0.42], [0.03, 0.6], [0.14, 0.34], [0.1, 0.12]]},
    paper: {width: 1.58, depth: 0.54, thickness: 0.012, count: 4, spread: 0.04, tabletLayers: 3, screenWidth: 0.91, screenDepth: 0.85, screenLift: 2},
    whistle: {body: [0.13, 0.1, 0.16], mouthpiece: [0.08, 0.04, 0.15], mouthAt: [0, 0.01, -0.12]},
    cloth: {width: 0.35, depth: 0.26, thickness: 0.02},
    // a hammer held a little up its handle, its head across the top, tipped outward so each blow lands downward
    hammer: {handleRadius: 0.06, handleLength: 1.2, gripFrom: 0.15, head: [0.55, 0.22, 0.22], sides: 10, tilt: 45},
    // a stalk of straw held in the corner of the mouth, its seed head at the far end
    straw: {radius: 0.03, length: 0.7, head: [0.045, 0.16]},
    colours: {ink: 0x272936, silver: 0xa9adb8, paper: 0xf3eedf, white: 0xf4f2ed, accent: 0x6366f1, pencil: 0xd6b06b, handle: 0x8a5a2b, straw: 0xe8c66a},
};

function propsOf() {
    const props = new Map();
    const group = (name) => {
        const root = new THREE.Group();
        root.name = name;
        root.visible = false;
        root.matrixAutoUpdate = false;
        props.set(name, root);
        return root;
    };
    const part = (root, name, geometry, colour, at = [0, 0, 0]) => {
        const mesh = flat(geometry, colour);
        mesh.name = `${root.name}_${name}`;
        mesh.position.set(...at);
        root.add(mesh);
        return mesh;
    };
    const {pen, paper, cloth, colours} = TOOLS;
    for (const name of Object.values(WRITING)) {
        const root = group(name);
        const marker = name === "writing_marker";
        const pencil = name === "writing_pencil";
        const radius = pen.radius * (marker ? pen.markerScale : 1);
        part(root, "barrel", new THREE.CylinderGeometry(radius, radius, pen.length, pencil ? pen.pencilSides : pen.sides), pencil ? colours.pencil : colours.ink);
        const tip = part(root, "nib", new THREE.ConeGeometry(radius, pen.tip, pen.sides), colours.silver, [0, -(pen.length + pen.tip) / 2, 0]);
        tip.rotation.z = Math.PI;
        part(root, "band", new THREE.CylinderGeometry(radius * pen.bandScale, radius * pen.bandScale, pen.tip / 2, pen.sides), colours.accent, [0, pen.length * pen.bandAt, 0]);
        if (name === "writing_quill") {
            const feather = new THREE.Shape();
            feather.moveTo(...TOOLS.feather.points[0]);
            for (const point of TOOLS.feather.points.slice(1)) feather.lineTo(...point);
            feather.closePath();
            part(root, "feather", new THREE.ShapeGeometry(feather), colours.white, [0, pen.length * TOOLS.feather.at, 0]);
        }
        const nib = new THREE.Object3D();
        nib.name = "tip";
        nib.position.y = -pen.length / 2 - pen.tip;
        root.add(nib);
        root.userData.tip = nib;
    }
    for (const name of ["papers", "writing_paper", "writing_tablet"]) {
        const root = group(name);
        const tablet = name === "writing_tablet";
        const count = name === "papers" ? paper.count : 1;
        root.userData.sheets = [];
        for (let index = 0; index < count; index++) {
            const sheet = part(root, `sheet_${index}`, new THREE.BoxGeometry(paper.width, paper.thickness * (tablet ? paper.tabletLayers : 1), paper.depth), tablet ? colours.ink : colours.paper, [0, index * paper.thickness, 0]);
            root.userData.sheets.push(sheet);
        }
        if (tablet) part(root, "screen", new THREE.BoxGeometry(paper.width * paper.screenWidth, paper.thickness, paper.depth * paper.screenDepth), colours.accent, [0, paper.thickness * paper.screenLift, 0]);
    }
    props.get("papers").userData.shape = ({phase}) => {
        const square = rise(phase, 0, 0.3) * (1 - rise(phase, 0.8, 1));
        props.get("papers").userData.sheets.forEach((sheet, index) => {
            sheet.position.x = paper.spread * index * (1 - square);
            sheet.rotation.y = paper.spread * index * (1 - square);
        });
    };
    const whistle = group("hand_whistle");
    part(whistle, "body", new THREE.BoxGeometry(...TOOLS.whistle.body), colours.accent);
    part(whistle, "mouthpiece", new THREE.BoxGeometry(...TOOLS.whistle.mouthpiece), colours.silver, TOOLS.whistle.mouthAt);
    const {hammer} = TOOLS;
    const mallet = group("work_hammer");
    part(mallet, "handle", new THREE.CylinderGeometry(hammer.handleRadius, hammer.handleRadius, hammer.handleLength, hammer.sides), colours.handle, [0, hammer.handleLength / 2 - hammer.gripFrom, 0]);
    part(mallet, "head", new THREE.BoxGeometry(...hammer.head), colours.silver, [0, hammer.handleLength - hammer.gripFrom, 0]);
    const {straw} = TOOLS;
    const stalk = group("straw");
    part(stalk, "stalk", new THREE.CylinderGeometry(straw.radius, straw.radius, straw.length, 6), colours.straw, [0, straw.length / 2, 0]);
    part(stalk, "seeds", new THREE.ConeGeometry(...straw.head, 6), colours.pencil, [0, straw.length + straw.head[1] / 2, 0]);
    glassOf(group("magnifying_glass"));
    const wipe = group("polishing_cloth");
    part(wipe, "fold", new THREE.BoxGeometry(cloth.width, cloth.thickness, cloth.depth), colours.white);
    reactionPropsOf(group, part);
    telephoneOf(group("telephone"), group("telephone_handset"), group("telephone_cord"), group("telephone_poof"));
    lightBulbOf(group("light_bulb"));
    reportScrollOf(group("report_scroll"));
    return props;
}

// The report scroll the figure reads (scroll), in the figure's own style: two wooden rollers `roller` round and `length` long, across, a
// knob `knob` round on each end, and on each a sleeve of the parchment wound round it, `wound` round while the scroll is rolled up and
// `unwound` once it is open, the rollers turning as it unrolls; between them the parchment `width` wide, its plain aged back to the
// viewer, bowed `bow` toward it in the middle and its side edges curled `curl` back, in `rows` by `columns` facets so it catches the
// light. Rolled up in one hand its rollers lie `rolled` apart. Every number of it is here, in the figure's units.
export const REPORT_SCROLL = {
    roller: 0.045, length: 1.25, knob: 0.075, wound: 0.11, unwound: 0.06, turns: 1.5, width: 1, bow: 0.06, curl: 0.08, rows: 10, columns: 16,
    rolled: 0.22,
    colours: {wood: 0x8a5a2b, knob: 0x6b4220, back: 0xdcc79c, wound: 0xe6d6ae},
};

// the scroll's parts in its own axes, its middle at the root; its `shape` puts its rollers at `top` and `bottom` (from its middle, in the
// figure's own axes, z up) and stretches the parchment between them, unrolled `open` of the way, 0 to 1
export function reportScrollOf(root) {
    const {roller, length, knob, wound, unwound, turns, width, bow, curl, rows, columns, colours} = REPORT_SCROLL;
    const rollers = ["top", "bottom"].map((which) => {
        const group = new THREE.Group();
        group.name = `${root.name}_${which}`;
        root.add(group);
        const rod = shadedPart(group, "roller", new THREE.CylinderGeometry(roller, roller, length, 14), colours.wood);
        rod.rotation.z = Math.PI / 2;
        for (const end of [-1, 1]) shadedPart(group, `knob_${end > 0 ? "l" : "r"}`, new THREE.SphereGeometry(knob, 14, 10), colours.knob, [(end * length) / 2, 0, 0]);
        const sleeve = shadedPart(group, "wound", new THREE.CylinderGeometry(1, 1, width, 18), colours.wound);
        sleeve.rotation.z = Math.PI / 2;
        return {group, sleeve, rod};
    });
    const sheet = new THREE.PlaneGeometry(width, 1, columns, rows);
    const parchment = shadedPart(root, "parchment", sheet, colours.back);
    const glb = (point) => new THREE.Vector3(point.x, point.z, -point.y);
    root.userData.shape = ({top, bottom, open}) => {
        const [upper, lower] = [glb(top), glb(bottom)];
        const radius = mix(wound, unwound, open);
        rollers.forEach(({group, sleeve, rod}, index) => {
            group.position.copy(index ? lower : upper);
            sleeve.scale.set(radius, 1, radius);
            rod.rotation.x = (index ? -1 : 1) * turns * 2 * Math.PI * open;
        });
        parchment.visible = open > 0.02;
        const position = sheet.attributes.position;
        for (let row = 0; row <= rows; row++) {
            const along = row / rows;
            const middle = upper.clone().lerp(lower, along);
            for (let column = 0; column <= columns; column++) {
                const across = column / columns - 0.5;
                const out = bow * Math.sin(Math.PI * along) * open - curl * (2 * across) ** 4;
                position.setXYZ(row * (columns + 1) + column, middle.x + across * width, middle.y, middle.z + radius + out);
            }
        }
        position.needsUpdate = true;
        sheet.computeVertexNormals();
        sheet.setAttribute("hullNormal", sheet.attributes.normal.clone());
    };
}

// The light bulb over the head at the end of the thinking act, in the figure's own style, standing `at` (across toward the hand raised
// under it, forward and up, in the figure's units), just above the head and inside the picture whatever the figure wears on it: a pear
// shaped glass globe `globe` round, narrowing into its neck, on a screw base `base` round and high with `threads` rings about it and a
// small contact under it; inside, a filament on two wires, drawn through the glass. Switched off its glass is clear and its filament
// dark; lit, both glow `warm`, a soft halo `halo` times its size about it, and it lights the parts of the figure turned to it (FLAT) as
// strongly as `strength`, weaker with the square of the distance by `falloff`. Every number of it is here.
export const LIGHT_BULB = {
    at: [0.95, -0.25, 4.05], globe: 0.36, neck: 0.15, base: [0.15, 0.22], threads: 3, filament: 0.14, wire: 0.014, halo: 1.7,
    strength: 1.4, falloff: 0.6,
    colours: {glass: 0xe3edf3, glassLit: 0xffe27a, base: 0xb7bcc6, contact: 0x3a3d47, filament: 0x5b5f6b, filamentLit: 0xfff4c2, warm: [1, 0.82, 0.42]},
};

// the light bulb's parts in its own axes, its middle at the root, the globe up and the base down; its `shape` grows it in by `size` and
// lights it by `lit`, both 0 to 1
export function lightBulbOf(root) {
    const {globe, neck, base, threads, filament, wire, halo, colours} = LIGHT_BULB;
    const bulb = new THREE.Group();
    bulb.name = root.name;
    root.add(bulb);
    const profile = [[0, globe * 1.95], [globe * 0.55, globe * 1.85], [globe * 0.92, globe * 1.45], [globe, globe], [globe * 0.88, globe * 0.55], [neck * 1.2, globe * 0.18], [neck, 0]].map(([x, y]) => new THREE.Vector2(x, y)).reverse();
    const glass = shadedPart(bulb, "glass", new THREE.LatheGeometry(profile, 28), colours.glass);
    glass.material.uniforms.shade = {value: SHADE.clone()};
    const [radius, height] = base;
    shadedPart(bulb, "base", new THREE.CylinderGeometry(radius, radius * 0.92, height, 20), colours.base, [0, -height / 2, 0]);
    for (let ring = 0; ring < threads; ring++) shadedPart(bulb, `thread_${ring}`, new THREE.TorusGeometry(radius * 1.02, height / (threads * 4), 6, 20), colours.base, [0, -height * ((ring + 0.6) / threads), 0]).rotation.x = Math.PI / 2;
    shadedPart(bulb, "contact", new THREE.SphereGeometry(radius * 0.45, 12, 8), colours.contact, [0, -height, 0]);
    const zigzag = new THREE.CatmullRomCurve3([[-filament, globe * 0.6], [-filament * 0.5, globe * 1.15], [0, globe * 0.95], [filament * 0.5, globe * 1.15], [filament, globe * 0.6]].map(([x, y]) => new THREE.Vector3(x, y, 0)));
    const lamp = new THREE.Group();
    bulb.add(lamp);
    const parts = [new THREE.TubeGeometry(zigzag, 24, wire * 1.4, 6), ...[-1, 1].map((side) => new THREE.TubeGeometry(new THREE.LineCurve3(new THREE.Vector3(side * filament, 0.02, 0), new THREE.Vector3(side * filament, globe * 0.6, 0)), 1, wire, 6))];
    const glowing = parts.map((geometry) => {
        const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({color: colours.filament, depthTest: false}));
        mesh.renderOrder = 2;
        mesh.frustumCulled = false;
        lamp.add(mesh);
        return mesh;
    });
    const aura = new THREE.Mesh(new THREE.CircleGeometry(globe * halo, 32), new THREE.MeshBasicMaterial({color: new THREE.Color(...colours.warm), transparent: true, depthWrite: false}));
    aura.position.set(0, globe, -globe * 1.2);
    aura.frustumCulled = false;
    bulb.add(aura);
    const off = new THREE.Color(colours.glass);
    const on = new THREE.Color(colours.glassLit);
    root.userData.shape = ({size, lit}) => {
        bulb.scale.setScalar(Math.max(size, 0.001));
        const colour = off.clone().lerp(on, lit);
        glass.material.uniforms.colour.value.set(colour.r, colour.g, colour.b);
        glass.material.uniforms.shade.value.copy(SHADE).lerp(new THREE.Vector3(1.25, 1.25, 1.25), lit);
        for (const mesh of glowing) mesh.material.color.set(colours.filament).lerp(new THREE.Color(colours.filamentLit), lit);
        aura.visible = lit > 0;
        aura.material.opacity = 0.35 * lit;
    };
}

// An old rotary desk telephone, drawn a size too large for the figure so it plainly reads as one: its place on the floor across and forward
// of the feet, tipped `tip` degrees toward the viewer, with a footprint near square. Its body, seen from the side, stands `height` high and
// `depth` deep: its front face slopes back from the floor at the front up to its brow, `brow` (forward of the middle and up), with the dial
// set in it, its top runs back from there and its back comes down to the floor, every edge rounded by `round` and its top domed `dome`
// higher in the middle; it is `width` across at the floor and `narrow` of that narrower at the top, nearly as tall as it is wide. The
// dial is a cream plate `plate` round filling most of the front face, `face` thick, with marks round its rim for the numbers `marks` from
// its middle, and on it a dark wheel `radius` round, its `holes` white finger holes `hole` round on a ring `ring` from the middle, the
// first `first` degrees round from the right and the rest `spread` degrees on, a small label in the middle and a finger stop past the
// last. On top, `at` back of the middle, two prongs `apart` from the middle and `height` high, each with a saddle for the handle. The
// handset is a curved horn `length` long, its handle `grip` thick bending down `drop` at its ends into round ends, an ear piece and a
// mouth piece, each a bulb `end` round and high with its grille underneath; it rests `rest` over the prongs, across the top with its
// ends hanging past the sides. The cord is `cord` thick in `coils` turns `coil` round. The poof it comes and goes in
// is `puffs` puffs of smoke `puff` round, bursting out from `from` to `to` of the figure's units about its middle. Each part is shaded and
// outlined as the figure is, never flat.
export const TELEPHONE = {
    at: [0, -0.92],
    tip: 10,
    base: {width: 1.2, narrow: 0.18, depth: 0.85, height: 0.88, brow: [0.08, 0.8], round: 0.16, dome: 0.06},
    dial: {plate: 0.42, face: 0.045, marks: 0.37, radius: 0.31, holes: 10, hole: 0.05, ring: 0.22, first: 60, spread: 290, label: 0.11},
    cradle: {at: -0.14, apart: 0.3, post: 0.055, height: 0.13},
    handset: {length: 1.4, grip: 0.085, drop: 0.15, end: [0.2, 0.15], rest: 0.06},
    cord: 0.022, coils: 14, coil: 0.05,
    poof: {puffs: 11, puff: 0.24, from: 0.5, to: 0.95},
    colours: {body: 0xa8322d, face: 0xf1e6cf, wheel: 0x2b2e38, hole: 0xf4f2ed, mark: 0x2b2e38, label: 0xf4f2ed, grille: 0x2b2e38, smoke: 0xe6e3ee},
};

// a part shaded and outlined as the figure's own are (flatMaterial, outlineMaterial), for a prop that should read as solid
function shadedPart(root, name, geometry, colour, at = [0, 0, 0]) {
    const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({color: colour}));
    addHullNormals(geometry);
    mesh.material = flatMaterial(mesh);
    const hull = new THREE.Mesh(geometry, outlineMaterial(mesh));
    hull.frustumCulled = mesh.frustumCulled = false;
    mesh.add(hull);
    mesh.name = `${root.name}_${name}`;
    mesh.position.set(...at);
    root.add(mesh);
    return mesh;
}

// the telephone's body as one solid in its own axes (TELEPHONE base): its side's outline, the front sloping back to the brow, round over
// the top and down the back, drawn out across its width with rounded sides, and narrowed toward the top
function bodyGeometry() {
    const {width, narrow, depth, height, brow, round, dome} = TELEPHONE.base;
    const side = new THREE.Shape();
    side.moveTo(-depth / 2 + round * 0.5, 0);
    side.lineTo(depth / 2 - round * 0.5, 0);
    side.quadraticCurveTo(depth / 2, 0, depth / 2 - round * 0.2, round * 0.5);
    side.lineTo(brow[0] + round * 0.3, brow[1] - round * 0.4);
    side.quadraticCurveTo(brow[0] - round * 0.2, height, brow[0] - round * 1.6, height);
    side.lineTo(-depth / 2 + round * 1.8, height);
    side.quadraticCurveTo(-depth / 2 + round * 0.1, height, -depth / 2 + round * 0.1, height - round * 1.6);
    side.lineTo(-depth / 2, round * 0.5);
    side.quadraticCurveTo(-depth / 2, 0, -depth / 2 + round * 0.5, 0);
    const across = width - 2 * round;
    const solid = new THREE.ExtrudeGeometry(side, {depth: across, bevelEnabled: true, bevelThickness: round, bevelSize: bulge(), bevelSegments: 6, curveSegments: 12});
    solid.rotateY(-Math.PI / 2).translate(across / 2, 0, 0);
    const position = solid.attributes.position;
    for (let index = 0; index < position.count; index++) {
        const [x, y] = [position.getX(index), Math.max(position.getY(index), 0)];
        position.setX(index, x * (1 - (narrow * y) / height));
        position.setY(index, position.getY(index) + dome * (y / height) ** 2 * Math.max(1 - (x / (width / 2)) ** 2, 0));
    }
    solid.computeVertexNormals();
    return solid;
}

// The telephone's base, dial and cradle in `set`, standing up its y axis with its front toward the viewer (+z), its handset in `handset`,
// its middle at the origin and its cups' mouths down, and its cord in `cord`, coiled from its shape's `from` to its `to` (in the figure's
// own axes, against the root), and the poof it comes and goes in in `poof`, bursting as its shape's `puff` goes from 0 to 1. The body
// squashes as its shape's `squash` says, flatter and wider for more, and the dial's wheel turns `dial` degrees
export function telephoneOf(set, handset, cord, poof) {
    const {base, dial, cradle, colours} = TELEPHONE;
    const body = new THREE.Group();
    body.name = set.name;
    set.add(body);
    shadedPart(body, "base", bodyGeometry(), colours.body);
    const face = new THREE.Group();
    face.name = set.name;
    face.matrixAutoUpdate = false;
    face.matrix.copy(dialFrame());
    body.add(face);
    shadedPart(face, "dial_plate", new THREE.CylinderGeometry(dial.plate, dial.plate, dial.face, 40), colours.face, [0, dial.face / 2, 0]);
    for (let index = 0; index < dial.holes; index++) {
        const angle = radians(dial.first + (dial.spread * index) / (dial.holes - 1));
        shadedPart(face, `number_${index}`, new THREE.BoxGeometry(0.03, dial.face * 0.6, 0.045), colours.mark, [Math.cos(angle) * dial.marks, dial.face, -Math.sin(angle) * dial.marks]);
    }
    const wheel = new THREE.Group();
    wheel.name = set.name;
    wheel.position.y = dial.face;
    face.add(wheel);
    shadedPart(wheel, "dial_wheel", new THREE.CylinderGeometry(dial.radius, dial.radius, dial.face * 0.6, 36), colours.wheel, [0, dial.face * 0.3, 0]);
    for (let index = 0; index < dial.holes; index++) {
        const angle = radians(dial.first + (dial.spread * index) / (dial.holes - 1));
        shadedPart(wheel, `hole_${index}`, new THREE.CylinderGeometry(dial.hole, dial.hole, dial.face * 0.7, 12), colours.hole, [Math.cos(angle) * dial.ring, dial.face * 0.4, -Math.sin(angle) * dial.ring]);
    }
    shadedPart(face, "dial_label", new THREE.CylinderGeometry(dial.label, dial.label, dial.face * 1.6, 24), colours.label, [0, dial.face, 0]);
    const stop = radians(dial.first + dial.spread + 22);
    shadedPart(face, "dial_stop", new THREE.BoxGeometry(0.04, dial.face * 2.2, 0.1), colours.label, [Math.cos(stop) * (dial.radius + 0.02), dial.face * 1.2, -Math.sin(stop) * (dial.radius + 0.02)]);
    for (const sign of [1, -1]) {
        const top = crownAt(cradle.apart) + cradle.height;
        shadedPart(body, `prong_${sign}`, new THREE.CylinderGeometry(cradle.post, cradle.post * 1.4, cradle.height + 0.04, 12), colours.body, [sign * cradle.apart, top - cradle.height / 2 - 0.02, cradle.at]);
        const saddle = shadedPart(body, `saddle_${sign}`, new THREE.TorusGeometry(TELEPHONE.handset.grip * 1.1, cradle.post * 0.45, 8, 14, Math.PI), colours.body, [sign * cradle.apart, top + TELEPHONE.handset.grip * 0.4, cradle.at]);
        saddle.rotation.set(0, Math.PI / 2, Math.PI);
    }
    const held = new THREE.Group();
    held.name = handset.name;
    handset.add(held);
    const {length, grip, drop, end} = TELEPHONE.handset;
    const horn = new THREE.CatmullRomCurve3([[-length / 2, -drop], [-length / 2 + 0.24, 0.02], [0, 0.06], [length / 2 - 0.24, 0.02], [length / 2, -drop]].map(([x, y]) => new THREE.Vector3(x, y, 0)));
    shadedPart(held, "handle", new THREE.TubeGeometry(horn, 32, grip, 12), colours.body);
    for (const [name, sign] of [["ear", 1], ["mouth", -1]]) {
        const piece = new THREE.Group();
        piece.name = handset.name;
        piece.position.set(sign * length / 2, -drop, 0);
        piece.rotation.z = sign * 0.22;
        held.add(piece);
        const bulb = shadedPart(piece, `${name}_piece`, new THREE.SphereGeometry(end[0], 24, 16), colours.body, [0, -end[1] * 0.45, 0]);
        bulb.scale.set(1, end[1] / end[0], 1);
        shadedPart(piece, `${name}_grille`, new THREE.CylinderGeometry(end[0] * 0.62, end[0] * 0.62, 0.025, 20), colours.grille, [0, -end[1] * 0.92, 0]);
    }
    set.userData.shape = ({squash, dial: turned}) => {
        body.scale.set(1 + squash / 2, 1 - squash, 1 + squash / 2);
        wheel.rotation.y = radians(turned);
    };
    const coiled = shadedPart(cord, "cord", cordGeometry(new THREE.Vector3(), new THREE.Vector3(1, 0, 0)), colours.body);
    cord.userData.shape = ({from, to}) => {
        coiled.geometry.dispose();
        coiled.geometry = coiled.children[0].geometry = cordGeometry(from, to);
        addHullNormals(coiled.geometry);
    };
    const {puffs, puff, from, to} = TELEPHONE.poof;
    const smoke = Array.from({length: puffs}, (_, index) => shadedPart(poof, `puff_${index}`, new THREE.IcosahedronGeometry(puff * (0.75 + 0.5 * ((index * 7) % 5) / 4), 1), colours.smoke));
    poof.userData.shape = ({puff: k}) => {
        smoke.forEach((each, index) => {
            const angle = (2 * Math.PI * index) / puffs;
            const out = from + (to - from) * Math.sqrt(k);
            each.position.set(Math.cos(angle) * out, Math.sin(angle * 2) * out * 0.35, Math.sin(angle) * out * 0.6);
            each.scale.setScalar(Math.max(Math.sin(Math.PI * k), 1e-3));
        });
    };
}

// the telephone's coiled cord from `from` to `to`, points in the figure's own axes, sagging between them and wound round its path, as the
// prop's own geometry (z up there is y)
function cordGeometry(from, to) {
    const {cord, coils, coil} = TELEPHONE;
    const glb = (point) => new THREE.Vector3(point.x, point.z, -point.y);
    const [a, b] = [glb(from), glb(to)];
    const sag = a.clone().lerp(b, 0.5).add(new THREE.Vector3(0, -0.35 * a.distanceTo(b), 0));
    const path = new THREE.QuadraticBezierCurve3(a, sag, b);
    const points = Array.from({length: coils * 8 + 1}, (_, index) => {
        const k = index / (coils * 8);
        const at = path.getPoint(k);
        const tangent = path.getTangent(k);
        const side = new THREE.Vector3(0, 1, 0).cross(tangent).normalize();
        const up = tangent.clone().cross(side).normalize();
        const angle = 2 * Math.PI * coils * k;
        return at.addScaledVector(side, Math.cos(angle) * coil).addScaledVector(up, Math.sin(angle) * coil);
    });
    return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), coils * 16, cord, 6);
}

// The things the voices bring out when the agent answers with one of their faces, sized against the figure, each standing up its y axis
// with its front toward the viewer (+z)
export const REACTION_PROPS = {
    monocle: {radius: 0.2, tube: 0.028, chain: 0.55, chainWidth: 0.012},
    flute: {base: 0.13, baseDepth: 0.025, stem: 0.022, stemLength: 0.35, rim: 0.12, bottom: 0.05, bowl: 0.4, fill: 0.27},
    shades: {lens: [0.56, 0.34, 0.05], apart: 0.37, bridge: [0.2, 0.05, 0.05], temple: [0.04, 0.04, 0.7], shine: [0.2, 0.035, 0.01]},
    flame: {outer: [0.17, 0.55], inner: [0.09, 0.32], sides: 12, flickers: 7},
    finger: {radius: 0.09, length: 0.22, splay: 0.6},
    popper: {mouth: 0.14, length: 0.45, sides: 12},
    confetti: {count: 18, size: 0.08, reach: 1.5, fall: 0.9, spin: 9},
    trophy: {base: [0.38, 0.12, 0.38], stem: [0.05, 0.08, 0.22], rim: 0.3, bottom: 0.12, cup: 0.38, handle: 0.12, handleTube: 0.03},
    sword: {grip: [0.035, 0.26], guard: [0.42, 0.06, 0.07], blade: [0.09, 1.3, 0.025], point: 0.15, pommel: 0.06},
    castle: {wall: [0.6, 0.3, 0.25], crenel: [0.1, 0.08, 0.25], tower: [0.11, 0.5], roof: [0.15, 0.24], gate: [0.14, 0.18], pole: 0.24, flag: 0.14},
    colours: {hat: 0x292a3b, band: 0xf4f2ed, gold: 0xe8b84a, glass: 0xdde6ee, champagne: 0xf1d27a, lens: 0x14161c, flame: 0xff7a1a,
        fire: 0xffd23f, hand: 0xf5ecdf, wood: 0x7a4a26, stone: 0xc9c2b4, confetti: [0x6366f1, 0xe8b84a, 0xef476f, 0x06d6a0, 0x118ab2]},
};

function reactionPropsOf(group, part) {
    const {monocle, flute, shades, flame, finger, popper, confetti, trophy, sword, castle, colours} = REACTION_PROPS;
    const ink = TOOLS.colours.ink, silver = TOOLS.colours.silver, accent = TOOLS.colours.accent;
    const topHat = group("top_hat");
    part(topHat, "crown", topHatGeometry(), colours.hat);
    part(topHat, "band", topHatBandGeometry(), new THREE.Color(...BUTLER.satin).getHex());
    const glass = group("monocle");
    part(glass, "ring", new THREE.TorusGeometry(monocle.radius, monocle.tube, 8, 24), colours.gold);
    part(glass, "lens", new THREE.CircleGeometry(monocle.radius, 24), colours.glass);
    part(glass, "chain", new THREE.CylinderGeometry(monocle.chainWidth, monocle.chainWidth, monocle.chain, 6), colours.gold, [monocle.radius * 0.7, -monocle.radius * 0.7 - monocle.chain / 2, 0]);
    const toast = group("champagne_flute");
    part(toast, "base", new THREE.CylinderGeometry(flute.base, flute.base, flute.baseDepth, 16), colours.glass, [0, -flute.stemLength / 2, 0]);
    part(toast, "stem", new THREE.CylinderGeometry(flute.stem, flute.stem, flute.stemLength, 8), colours.glass);
    part(toast, "bowl", new THREE.CylinderGeometry(flute.rim, flute.bottom, flute.bowl, 16, 1, true), colours.glass, [0, (flute.stemLength + flute.bowl) / 2, 0]);
    part(toast, "wine", new THREE.CylinderGeometry(flute.rim * 0.9, flute.bottom * 0.9, flute.fill, 16), colours.champagne, [0, flute.stemLength / 2 + flute.fill / 2 + 0.01, 0]);
    const cool = group("sunglasses");
    for (const sign of [1, -1]) {
        part(cool, `lens_${sign}`, new THREE.BoxGeometry(...shades.lens), colours.lens, [sign * shades.apart, 0, 0]);
        part(cool, `temple_${sign}`, new THREE.BoxGeometry(...shades.temple), ink, [sign * (shades.apart + shades.lens[0] / 2), shades.lens[1] / 4, -shades.temple[2] / 2]);
        part(cool, `shine_${sign}`, new THREE.BoxGeometry(...shades.shine), TOOLS.colours.white, [sign * shades.apart - shades.lens[0] / 5, shades.lens[1] / 4, shades.lens[2] / 2]).rotation.z = 0.5;
    }
    part(cool, "bridge", new THREE.BoxGeometry(...shades.bridge), ink, [0, shades.lens[1] / 4, 0]);
    const fire = group("flame");
    const outer = part(fire, "outer", new THREE.ConeGeometry(flame.outer[0], flame.outer[1], flame.sides), colours.flame, [0, flame.outer[1] / 2, 0]);
    const inner = part(fire, "inner", new THREE.ConeGeometry(flame.inner[0], flame.inner[1], flame.sides), colours.fire, [0, flame.inner[1] / 2, 0.03]);
    fire.userData.shape = ({phase, size}) => {
        const flicker = 1 + 0.18 * Math.sin(2 * Math.PI * flame.flickers * phase) + 0.08 * Math.sin(2 * Math.PI * 2.3 * flame.flickers * phase);
        fire.scale.set(size * (2 - flicker), size * flicker, size * (2 - flicker));
        outer.rotation.z = inner.rotation.z = 0.12 * Math.sin(2 * Math.PI * 1.7 * flame.flickers * phase);
    };
    const digit = () => new THREE.CapsuleGeometry(finger.radius, finger.length, 4, 8);
    part(group("thumb"), "thumb", digit(), colours.hand, [0, finger.length / 2 + finger.radius, 0]);
    const shaka = group("shaka");
    for (const sign of [1, -1]) part(shaka, `finger_${sign}`, digit(), colours.hand, [sign * finger.length * 0.6, finger.length / 2, 0]).rotation.z = -sign * finger.splay;
    const party = group("party_popper");
    part(party, "cone", new THREE.ConeGeometry(popper.mouth, popper.length, popper.sides, 1, true), accent, [0, popper.length / 2, 0]).rotation.x = Math.PI;
    part(party, "rim", new THREE.TorusGeometry(popper.mouth, 0.02, 6, popper.sides), colours.gold, [0, popper.length, 0]).rotation.x = Math.PI / 2;
    const pieces = Array.from({length: confetti.count}, (_, index) => {
        const piece = part(party, `confetti_${index}`, new THREE.PlaneGeometry(confetti.size, confetti.size), colours.confetti[index % colours.confetti.length]);
        const around = index * 2.39996;
        const lean = 0.25 + 0.5 * ((index * 7) % confetti.count) / confetti.count;
        piece.userData.way = new THREE.Vector3(Math.sin(lean) * Math.cos(around), Math.cos(lean), Math.sin(lean) * Math.sin(around));
        return piece;
    });
    party.userData.shape = ({burst}) => {
        for (const [index, piece] of pieces.entries()) {
            piece.visible = burst > 0 && burst < 1;
            const out = confetti.reach * Math.sqrt(burst);
            piece.position.set(piece.userData.way.x * out, popper.length + piece.userData.way.y * out - confetti.fall * burst * burst, piece.userData.way.z * out);
            piece.rotation.set(confetti.spin * burst + index, confetti.spin * burst * 0.7, index);
        }
    };
    const cup = group("trophy");
    part(cup, "base", new THREE.BoxGeometry(...trophy.base), colours.wood, [0, -trophy.stem[2] - trophy.base[1] / 2, 0]);
    part(cup, "stem", new THREE.CylinderGeometry(trophy.stem[0], trophy.stem[1], trophy.stem[2], 12), colours.gold, [0, -trophy.stem[2] / 2, 0]);
    part(cup, "cup", new THREE.CylinderGeometry(trophy.rim, trophy.bottom, trophy.cup, 16), colours.gold, [0, trophy.cup / 2, 0]);
    for (const sign of [1, -1]) part(cup, `handle_${sign}`, new THREE.TorusGeometry(trophy.handle, trophy.handleTube, 6, 12), colours.gold, [sign * trophy.rim, trophy.cup * 0.6, 0]);
    const blade = group("sword");
    part(blade, "grip", new THREE.CylinderGeometry(sword.grip[0], sword.grip[0], sword.grip[1], 8), colours.wood);
    part(blade, "pommel", new THREE.SphereGeometry(sword.pommel, 8, 6), colours.gold, [0, -sword.grip[1] / 2 - sword.pommel / 2, 0]);
    part(blade, "guard", new THREE.BoxGeometry(...sword.guard), colours.gold, [0, sword.grip[1] / 2 + sword.guard[1] / 2, 0]);
    part(blade, "blade", new THREE.BoxGeometry(...sword.blade), silver, [0, sword.grip[1] / 2 + sword.guard[1] + sword.blade[1] / 2, 0]);
    const point = part(blade, "point", new THREE.ConeGeometry(sword.blade[0] / Math.SQRT2, sword.point, 4), silver, [0, sword.grip[1] / 2 + sword.guard[1] + sword.blade[1] + sword.point / 2, 0]);
    point.rotation.y = Math.PI / 4;
    point.scale.z = sword.blade[2] / sword.blade[0];
    const keep = group("castle");
    part(keep, "wall", new THREE.BoxGeometry(...castle.wall), colours.stone, [0, castle.wall[1] / 2, 0]);
    for (const x of [-1, 0, 1]) part(keep, `crenel_${x}`, new THREE.BoxGeometry(...castle.crenel), colours.stone, [x * castle.wall[0] / 3, castle.wall[1] + castle.crenel[1] / 2, 0]);
    for (const sign of [1, -1]) {
        part(keep, `tower_${sign}`, new THREE.CylinderGeometry(castle.tower[0], castle.tower[0], castle.tower[1], 12), colours.stone, [sign * castle.wall[0] / 2, castle.tower[1] / 2, 0]);
        part(keep, `roof_${sign}`, new THREE.ConeGeometry(...castle.roof, 12), accent, [sign * castle.wall[0] / 2, castle.tower[1] + castle.roof[1] / 2, 0]);
    }
    part(keep, "gate", new THREE.PlaneGeometry(...castle.gate), ink, [0, castle.gate[1] / 2, castle.wall[2] / 2 + 0.005]);
    const top = castle.tower[1] + castle.roof[1];
    part(keep, "pole", new THREE.CylinderGeometry(0.01, 0.01, castle.pole, 4), ink, [castle.wall[0] / 2, top + castle.pole / 2, 0]);
    const pennant = new THREE.Shape();
    pennant.moveTo(0, 0);
    pennant.lineTo(castle.flag, -castle.flag / 3);
    pennant.lineTo(0, -castle.flag * 2 / 3);
    pennant.closePath();
    part(keep, "flag", new THREE.ShapeGeometry(pennant), colours.gold, [castle.wall[0] / 2, top + castle.pole, 0]);
}

// A prop's place: at its spot on the bone that carries it, turned as `frame` is turned
function heldPropOf(moves, {bone, frame, at, turn}) {
    const placed = at.clone().applyMatrix4(moves.get(bone));
    return TO_GLB.clone().multiply(translation(placed)).multiply(new THREE.Matrix4().extractRotation(moves.get(frame)))
        .multiply(euler(turn.x || 0, turn.y || 0, turn.z || 0)).multiply(FROM_GLB);
}

// the light bulb's light on the figure, where the bulb is and as warm as it is lit, none while it is out
export function lightFromBulb(figure, pose) {
    const {bulbAt, bulbGlow} = figure.bulbLight;
    bulbGlow.value.set(...LIGHT_BULB.colours.warm).multiplyScalar(LIGHT_BULB.strength * pose.bulbLit);
    if (pose.bulbLit) bulbAt.value.setFromMatrixPosition(figure.propByName.get("light_bulb").matrix).add(new THREE.Vector3(0, LIGHT_BULB.globe, 0));
}

// every prop placed where the pose holds it, and one whose shape moves, as the papers squared or the confetti flying, shaped as it says
function moveProps(figure, pose, moves) {
    for (const [name, prop] of figure.propByName) {
        const held = pose.props.get(name);
        prop.visible = Boolean(held);
        if (!held) continue;
        prop.matrix.copy(heldPropOf(moves, held));
        prop.matrixWorldNeedsUpdate = true;
        prop.userData.shape?.(held);
    }
}


function bookOf() {
    const slab = (name, colour, width, height, depth) => {
        const mesh = flat(new THREE.BoxGeometry(width, height, depth), colour);
        mesh.name = name;
        mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry), new THREE.LineBasicMaterial({color: BOOK_COLOURS.edge})));
        return mesh;
    };
    const book = new THREE.Group();
    book.name = "reading_book";
    book.matrixAutoUpdate = false;
    book.visible = false;
    const spine = slab("book_spine", BOOK_COLOURS.spine, BOOK.spine, BOOK.height, BOOK.cover);
    book.add(spine);
    const hinges = {}, covers = {}, pages = {}, grips = {};
    for (const [side, sign] of Object.entries(SIDES)) {
        const hinge = new THREE.Group();
        hinge.name = `book_hinge_${side}`;
        hinge.position.x = sign * BOOK.spine / 2;
        const cover = slab(`book_cover_${side}`, BOOK_COLOURS.cover, BOOK.width, BOOK.height, BOOK.cover);
        cover.position.set(sign * BOOK.width / 2, 0, BOOK.cover / 2);
        const block = slab(`book_pages_${side}`, BOOK_COLOURS.pages, BOOK.width - BOOK.inset, BOOK.height - BOOK.inset * 2, BOOK.pages);
        block.position.set(sign * (BOOK.width - BOOK.inset) / 2, 0, -BOOK.pages / 2);
        for (let line = 1; line <= BOOK.lines; line++) {
            const rule = flat(new THREE.BoxGeometry(BOOK.width - BOOK.inset, BOOK.lineWidth, BOOK.lineWidth), BOOK_COLOURS.rule);
            rule.position.set(block.position.x, -BOOK.height / 2 + BOOK.inset, -BOOK.pages * line / (BOOK.lines + 1));
            hinge.add(rule);
        }
        hinge.add(cover, block);
        book.add(hinge);
        hinges[side] = hinge;
        covers[side] = cover;
        pages[side] = block;
        const grip = new THREE.Object3D();
        grip.name = `book_grip_${side}`;
        book.add(grip);
        grips[side] = grip;
    }
    const leaf = flat(new THREE.PlaneGeometry(BOOK.width - BOOK.inset, BOOK.height - BOOK.inset * 2, BOOK.pageSegments, 1), BOOK_COLOURS.paper);
    leaf.geometry.translate(-(BOOK.width - BOOK.inset) / 2, 0, 0);
    leaf.name = "book_turning_page";
    const edge = new THREE.LineLoop(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({color: BOOK_COLOURS.rule}));
    edge.frustumCulled = false;
    leaf.add(edge);
    leaf.userData.edge = edge;
    book.add(leaf);
    book.userData = {hinges, covers, pages, grips, leaf};
    return book;
}

function heldBookOf(grips, open) {
    const left = grips.l.clone(), right = grips.r.clone();
    const across = left.clone().sub(right).normalize();
    const up = new THREE.Vector3(0, 1, 0).addScaledVector(across, -across.y).normalize();
    const forward = across.clone().cross(up).normalize();
    const turn = new THREE.Matrix4().makeBasis(across, up, forward).multiply(bookTurn(open));
    const scale = left.distanceTo(right) / bookGrip("l", open).distanceTo(bookGrip("r", open));
    const middle = bookGrip("l", open).add(bookGrip("r", open)).multiplyScalar(0.5).applyMatrix4(turn).multiplyScalar(scale);
    return turn.scale(new THREE.Vector3(scale, scale, scale)).setPosition(left.add(right).multiplyScalar(0.5).sub(middle));
}

function openBook(book, open, page) {
    const angle = bookAngle(open);
    for (const [side, sign] of Object.entries(SIDES)) {
        book.userData.hinges[side].rotation.y = sign * angle;
        book.userData.grips[side].position.copy(bookGrip(side, open));
    }
    const leaf = book.userData.leaf;
    const surface = BOOK.pages + BOOK.leaf;
    leaf.position.set(mix(-BOOK.spine / 2 + surface * Math.sin(angle), BOOK.spine / 2 - surface * Math.sin(angle), page), 0, -surface * Math.cos(angle));
    leaf.rotation.y = -angle - radians(BOOK.open * open) * page;
    leaf.visible = open > 0;
    const curl = BOOK.curl * Math.sin(Math.PI * page);
    const width = BOOK.width - BOOK.inset;
    const positions = leaf.geometry.attributes.position;
    for (let row = 0; row < 2; row++) {
        for (let column = 0; column <= BOOK.pageSegments; column++) {
            const fraction = 1 - column / BOOK.pageSegments;
            const at = row * (BOOK.pageSegments + 1) + column;
            const bow = BOOK.pageBow * Math.sin(Math.PI * page) * fraction * fraction;
            positions.setX(at, (curl ? -width * Math.sin(curl * fraction) / curl : -width * fraction) - Math.sin(leaf.rotation.y) * bow);
            positions.setZ(at, (curl ? width * (1 - Math.cos(curl * fraction)) / curl : 0) + Math.cos(leaf.rotation.y) * bow);
        }
    }
    positions.needsUpdate = true;
    const rim = [];
    for (let column = 0; column <= BOOK.pageSegments; column++) rim.push(new THREE.Vector3().fromBufferAttribute(positions, column));
    for (let column = BOOK.pageSegments; column >= 0; column--) rim.push(new THREE.Vector3().fromBufferAttribute(positions, BOOK.pageSegments + 1 + column));
    leaf.userData.edge.geometry.setFromPoints(rim);
}

// Where the laptop sits: level on the thighs with its hinge at the knees, its keyboard back over the thighs, turned the way the thighs
// point, so it turns with the figure
const LAP_REACH = 1.95;
const THIGH_TOP = 0.3;

function lapOf(world) {
    const at = (name) => new THREE.Vector3().setFromMatrixPosition(world.get(name));
    const hips = at("thigh_l").add(at("thigh_r")).multiplyScalar(0.5);
    const knees = at("shin_l").add(at("shin_r")).multiplyScalar(0.5);
    const forward = knees.clone().sub(hips).setY(0).normalize();
    const up = new THREE.Vector3(0, 1, 0);
    const hinge = hips.lerp(knees, LAP_REACH).addScaledVector(up, THIGH_TOP);
    return new THREE.Matrix4().makeBasis(up.clone().cross(forward), up, forward).setPosition(hinge);
}

// A heart the size of an eye, drawn flat toward the viewer, its point down
const HEART = (() => {
    const shape = new THREE.Shape();
    shape.moveTo(0, -0.5);
    shape.bezierCurveTo(-0.16, -0.3, -0.5, -0.16, -0.5, 0.12);
    shape.bezierCurveTo(-0.5, 0.4, -0.2, 0.5, 0, 0.26);
    shape.bezierCurveTo(0.2, 0.5, 0.5, 0.4, 0.5, 0.12);
    shape.bezierCurveTo(0.5, -0.16, 0.16, -0.3, 0, -0.5);
    return new THREE.ShapeGeometry(shape, 12);
})();
const HEART_SIZE = 0.42;
const HEART_COLOUR = new THREE.Color(1, 0.3, 0.5);

// A five-pointed star the size of an eye, drawn flat toward the viewer, a point up
const STAR = (() => {
    const shape = new THREE.Shape();
    for (let point = 0; point < 10; point++) {
        const reach = point % 2 ? 0.22 : 0.55;
        const way = Math.PI / 2 + (point * Math.PI) / 5;
        shape[point ? "lineTo" : "moveTo"](reach * Math.cos(way), reach * Math.sin(way));
    }
    return new THREE.ShapeGeometry(shape);
})();
const STAR_SIZE = 0.46;
const STAR_COLOUR = new THREE.Color(1, 0.86, 0.3);
// an eye squeezed shut laughing, as a cartoon's kawaii > <: a thick chevron pointing in toward the nose, in the eyes' own ivory, the
// figure's left eye drawn mirrored so the two point at each other
const SQUEEZE = (() => {
    const points = [[-0.4, 0.42], [0.42, 0], [-0.4, -0.42], [-0.4, -0.2], [0.04, 0], [-0.4, 0.2]];
    return new THREE.ShapeGeometry(new THREE.Shape(points.map(([x, y]) => new THREE.Vector2(x, y))));
})();
const SQUEEZE_SIZE = 0.5;
const SQUEEZE_COLOUR = new THREE.Color(1, 0.94, 0.81);
// the half of a round eye below its middle, its top flat as a lowered lid
const LIDDED = (() => {
    const shape = new THREE.Shape();
    shape.absarc(0, 0, 0.5, Math.PI, 2 * Math.PI, false);
    shape.closePath();
    return new THREE.ShapeGeometry(shape, 16);
})();

// The shapes the eyes take on in place of their smile, in the eyes' own ivory, each `size` across and moved `aside` and `up` on the visor,
// one that is `mirrored` drawn the other way round on the figure's right eye, so the two face each other: focused, narrowed to a flat oval at work; narrowed and serious, a bar sloping down toward the nose, at a failure; bright, a
// thick happy arch with a sparkle beside it, at a pass; calm, half-lidded, at rest; and eyeing, half-lidded and turned aside, at something that catches
// the eye
export const EYE_SHAPES = {
    focused: {geometry: (() => {
        const shape = new THREE.Shape();
        shape.absellipse(0, 0, 0.5, 0.2, 0, 2 * Math.PI, false, 0);
        return new THREE.ShapeGeometry(shape, 24);
    })(), size: 0.42, aside: 0, up: 0},
    narrowed: {geometry: new THREE.ShapeGeometry(new THREE.Shape([[-0.5, -0.12], [0.5, 0.14], [0.5, -0.06], [-0.5, -0.3]].map(([x, y]) => new THREE.Vector2(x, y)))), size: 0.44, aside: 0, up: 0, mirrored: true},
    bright: {geometry: (() => {
        const arch = new THREE.Shape();
        arch.absarc(0, -0.2, 0.5, 0, Math.PI, false);
        arch.absarc(0, -0.2, 0.26, Math.PI, 0, true);
        arch.closePath();
        const sparkle = new THREE.Shape();
        for (let point = 0; point < 8; point++) {
            const reach = point % 2 ? 0.05 : 0.17;
            const way = (point * Math.PI) / 4;
            sparkle[point ? "lineTo" : "moveTo"](0.62 + reach * Math.cos(way), 0.38 + reach * Math.sin(way));
        }
        return new THREE.ShapeGeometry([arch, sparkle], 16);
    })(), size: 0.46, aside: 0, up: 0, mirrored: true},
    calm: {geometry: LIDDED, size: 0.38, aside: 0, up: -0.02},
    eyeing: {geometry: LIDDED, size: 0.32, aside: 0.13, up: 0},
    // a run's end shown in the eyes (visor.js SIGN), each glowing in the visor's colour with a soft halo about it: a cross, and a tick
    cross: {geometry: new THREE.ShapeGeometry([[-1, 1], [1, -1]].map(([from, to]) => new THREE.Shape([[-0.5 * from, 0.5], [-0.5 * from + 0.18 * to, 0.5], [0.5 * from, -0.5], [0.5 * from - 0.18 * to, -0.5]].map(([x, y]) => new THREE.Vector2(x, y))))), size: 0.4, aside: 0, up: 0, glows: true},
    tick: {geometry: new THREE.ShapeGeometry(new THREE.Shape([[-0.5, 0.02], [-0.32, 0.18], [-0.12, -0.04], [0.36, 0.52], [0.52, 0.36], [-0.12, -0.36]].map(([x, y]) => new THREE.Vector2(x, y)))), size: 0.42, aside: 0, up: 0, glows: true},
};

// a shape over an eye, a heart or a star, carried by the head as the eye is, hidden until the eyes take it on
function shapeOver(eye, geometry, colour) {
    const bounds = new THREE.Box3().setFromBufferAttribute(eye.geometry.attributes.position).applyMatrix4(eye.matrixWorld);
    const centre = bounds.getCenter(new THREE.Vector3()).setZ(bounds.max.z + 0.01);
    const head = eye.skeleton.getBoneByName("head");
    const holder = new THREE.Group();
    holder.matrixAutoUpdate = false;
    holder.matrix.copy(head.matrixWorld).invert().multiply(translation(centre));
    const over = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({color: colour}));
    over.frustumCulled = false;
    over.visible = false;
    holder.add(over);
    head.add(holder);
    return over;
}

// the soft halo about a glowing shape over an eye: the shape again, larger, faint and just behind it
const HALO = {size: 1.45, opacity: 0.4, behind: 0.004};

function haloOver(eye, geometry) {
    const halo = shapeOver(eye, geometry, SQUEEZE_COLOUR);
    halo.material.transparent = true;
    halo.material.depthWrite = false;
    return halo;
}

// where each hand's closed fingers grip, in the figure's own space, for the pose's moves
function gripsOf(pose, moves) {
    return Object.fromEntries(Object.keys(SIDES).map((side) => [side, pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`)).applyMatrix4(TO_GLB)]));
}

// the figure's bones placed for the pose, turned `facing` degrees, eased from `blend.from` by `blend.k` while a blend is given; the moves
// placed are returned, so the next change can ease from them
function place(figure, pose, facing, blend) {
    const target = pose.moves(facing);
    const result = blend ? blendMoves(figure.rig, blend.from, target, blend.k, blend.previous) : {moves: target, settled: true};
    if (blend) blend.settled = result.settled;
    const moves = result.moves;
    const world = new Map();
    for (const bone of figure.rig.bones) {
        const placed = TO_GLB.clone().multiply(moves.get(bone.name)).multiply(FROM_GLB).multiply(figure.rig.rest.get(bone.name));
        world.set(bone.name, placed);
        const parentWorld = bone.parent.isBone ? world.get(bone.parent.name) : bone.parent.matrixWorld;
        parentWorld.clone().invert().multiply(placed).decompose(bone.position, bone.quaternion, bone.scale);
    }
    for (const material of figure.eyes.materials) {
        material.uniforms.openness.value = Math.max(pose.eyes * (1 - (pose.eyeShape?.strength ?? 0)), MIN_EYE_HEIGHT);
        material.uniforms.eyeShift.value.set(...pose.eyeShift);
        if (material.uniforms.light) material.uniforms.colour.value.set(...(pose.eyeTint ?? material.userData.colour));
    }
    figure.laptop.visible = pose.laptop;
    figure.book.visible = Boolean(pose.book?.visible);
    if (figure.book.visible) {
        openBook(figure.book, pose.book.open, pose.book.page);
        figure.book.matrix.copy(heldBookOf(gripsOf(pose, moves), pose.book.open));
        figure.book.matrixWorldNeedsUpdate = true;
    }
    for (const part of figure.tablet) part.visible = pose.tablet;
    const occupied = pose.laptop || pose.book || pose.props.size > 0;
    for (const part of figure.stowable) part.visible = !pose.stowed.has(part.userData.item);
    for (const part of figure.inHand) part.visible = !pose.stowed.has(part.userData.item) && (!occupied || pose.keep.has(part.userData.item));
    moveProps(figure, pose, moves);
    lightFromBulb(figure, pose);
    for (const part of figure.cloth) part.visible = pose.cloth;
    if (pose.laptop) {
        figure.laptop.matrix.copy(lapOf(world));
        figure.laptop.matrixWorldNeedsUpdate = true;
    }
    const crt = pose.screen ?? DARK_SCREEN;
    for (const material of figure.screens) {
        material.uniforms.lit.value = crt.glow;
        material.uniforms.across.value = crt.across;
        material.uniforms.open.value = crt.open;
        material.uniforms.flash.value = crt.flash;
        if (pose.screen) material.uniforms.glow.value.set(...pose.screen.colour);
    }
    // the visor's outline pokes through the middle of the curved visor, unseen on the dark screen and plain on a lit one
    for (const hull of figure.visorHulls) hull.visible = !pose.screen || Boolean(pose.screen.sign);
    // the eyes go out before a lit visor comes on, a display with nothing on it
    const eyed = crt.eyes > EYES_GONE;
    const shaped = pose.eyeShape && !pose.hearts && !pose.stars && !pose.squeezed ? pose.eyeShape : null;
    for (const shape of figure.eyes.shapes) shape.visible = eyed && !pose.hearts && !pose.stars && !pose.squeezed && !(shaped?.strength >= 1);
    for (const heart of figure.eyes.hearts) {
        heart.visible = eyed && pose.hearts > 0;
        heart.scale.setScalar(HEART_SIZE * pose.hearts);
    }
    for (const star of figure.eyes.stars) {
        star.visible = eyed && pose.stars > 0 && !pose.hearts;
        star.scale.setScalar(STAR_SIZE * pose.stars);
        star.rotation.z = 1.2 * (pose.stars - 1);
    }
    for (const squeeze of figure.eyes.squeezed) {
        squeeze.visible = eyed && pose.squeezed > 0 && !pose.hearts && !pose.stars;
        squeeze.scale.set(SQUEEZE_SIZE * pose.squeezed * squeeze.userData.way, SQUEEZE_SIZE * pose.squeezed, 1);
    }
    // a shape the eyes take on opens as their own smile closes, and closes again as the smile comes back
    // a sign glows in the visor's colour, as white as its flash and as bright as it is lit
    const sign = pose.screen?.sign;
    for (const over of figure.eyes.over) {
        const {name, side, halo} = over.userData;
        over.visible = eyed && shaped?.name === name;
        if (!over.visible) continue;
        const {size, aside, up, mirrored} = EYE_SHAPES[name];
        const grown = size * (halo ? HALO.size : 1);
        over.scale.set(grown * (mirrored ? side : 1), grown * Math.max(shaped.strength, MIN_EYE_HEIGHT), 1);
        over.position.set(aside * shaped.way, up, halo ? -HALO.behind : 0);
        if (sign) over.material.color.setRGB(...pose.screen.colour.map((part) => (part + (1 - part) * sign.white) * sign.lit));
        if (halo) over.material.opacity = HALO.opacity * (sign?.lit ?? 1);
    }
    return moves;
}

// A look the eyes take on over whatever the body does, `seconds` into a look that lasts `lasts` seconds: taken on at once and let go at the
// end, the head turned to the viewer meanwhile so the eyes are seen. Hearts beat as a heart does, a strong swell and a weaker one.
const BEAT_SECONDS = 0.8;

// how strongly a look holds, 0 to 1, `seconds` into one that lasts `lasts`: eased in over `into` seconds and back out over `out` at the end
export const LOOK_EASE = {into: 0.35, out: 0.45};
export const lookStrength = ({seconds, lasts}) => partOf(seconds, [0, LOOK_EASE.into]) * (1 - partOf(seconds, [lasts - LOOK_EASE.out, lasts]));

function lookAs(pose, {mood, seconds, lasts}) {
    const strength = lookStrength({seconds, lasts});
    if (EYES[mood].hearts) {
        const beat = (seconds % BEAT_SECONDS) / BEAT_SECONDS;
        pose.heartEyes(strength * (1 + 0.28 * swell(beat, 0, 0.3) + 0.14 * swell(beat, 0.3, 0.55)));
    } else {
        eyesAs(pose, mood, strength);
    }
}

// How far a figure turns toward the viewer so its face is seen, as while its eyes wear a look or its visor glows: its head `share` of the
// way round from the way the body faces, never quite head on and never further than HEAD_TURN from the body, and its chest leaning in by
// `lean` of it, so a figure facing sideways or away still turns or leans toward the viewer
export const TOWARD_VIEWER = {share: 0.8, lean: 0.12};

// the figure turned `facing` degrees turned toward the viewer, `strength` of the way, 0 to 1
export function turnToViewer(pose, facing, strength) {
    const sideways = ((((facing + 180) % 360) + 360) % 360) - 180;
    const lean = TOWARD_VIEWER.lean * sideways;
    const head = THREE.MathUtils.clamp(TOWARD_VIEWER.share * sideways - lean, -HEAD_TURN, HEAD_TURN);
    pose.bendAbove("chest", {z: -lean * strength});
    pose.turn("neck", {z: -0.3 * head * strength});
    pose.turn("head", {z: -0.7 * head * strength});
}

// the visor mesh every voice wears, the black screen its eyes are drawn on, and how lit it is before the eyes are gone from it
const VISOR_MESH = "face_screen";
const EYES_GONE = 0.05;
// the visor as it is unlit: its eyes shown and its band dark
const DARK_SCREEN = {eyes: 1, across: 0, open: 0, flash: 0, glow: 0};

// whether a figure in `posture` may turn to the viewer for a look or its lit visor, or turn its head to look at something: never lounging,
// its legs straight out, as it is only ever drawn side-on
export const turnsToViewer = (posture) => posture !== "lounge";

// One renderer for every picture on a page: it poses the figure, draws it and copies the result onto a canvas
export class Stage {
    constructor() {
        const half = FRAMED_HEIGHT / 2;
        this.camera = new THREE.OrthographicCamera(-half, half, half, -half, DISTANCE - DEPTH, DISTANCE + DEPTH);
        this.camera.position.set(0, FRAMED_MIDDLE, DISTANCE);
        this.camera.lookAt(0, FRAMED_MIDDLE, 0);
        this.renderer = new THREE.WebGLRenderer({antialias: true, alpha: true, preserveDrawingBuffer: true});
        this.renderer.setPixelRatio(1);
        this.renderer.setClearColor(0x000000, 0);
    }

    headAt(figure, moves) {
        if (!moves) return {x: 0.5, y: 0.3};
        const at = figure.rig.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(figure.rig.eyes.length);
        return this.pictured(at.applyMatrix4(moves.get("head")));
    }

    // where the free hand grips in the picture, which way across the picture its side is, 1 to the right, and where the other hand grips
    handAt(figure, moves) {
        const side = freeSide(figure.stance);
        const other = side === "l" ? "r" : "l";
        if (!moves) return {x: 0.5 + SIDES[side] * 0.25, y: 0.6, out: SIDES[side], other: {x: 0.5 - SIDES[side] * 0.25, y: 0.6}};
        return {...this.gripAt(figure, moves, side), out: SIDES[side], other: this.gripAt(figure, moves, other)};
    }

    // where the hand on `side` grips in the picture
    gripAt(figure, moves, side) {
        const grip = new THREE.Vector3(SIDES[side] * HAND.grip, HAND.forward, 0).add(figure.rig.heads.get(`hand_${side}`));
        return this.pictured(grip.applyMatrix4(moves.get(`hand_${side}`)));
    }

    // a point of the posed figure as shares of its picture's width from the left and height from the top
    pictured(point) {
        const at = point.applyMatrix4(TO_GLB).project(this.camera);
        return {x: (at.x + 1) / 2, y: (1 - at.y) / 2};
    }

    // The clip's pose at this frame in `posture`, the figure turned `facing` degrees, with the look `eyes` takes on, drawn to fill the canvas;
    // on the move, `stride` is how far through its step the walk is, `sky` is how a figure watching the sky stands (watch), `at` is where
    // in its picture it looks (lookToward), `open` how open a blink leaves the eyes (blink.js), `tilt` how many degrees the head leans at rest (headTilt.js), and during a change `blend` eases from
    // the moves drawn before it. It returns the moves it drew.
    draw(figure, clip, frame, facing, canvas, {posture = "stand", eyes = null, stride = 0, blend = null, sky = null, at = null, open = 1, screen = null, tilt = 0} = {}) {
        const pose = new Posing(figure.rig, posture, stride);
        pose.sky = sky;
        pose.screen = screen;
        pose.at = at;
        if (!clip.legs) LEGS[posture]?.under(pose);
        clip.pose(pose, figure.stance, frame / clip.frames);
        if (tilt) trunk(pose, {tilt});
        if (!clip.legs) LEGS[posture]?.over(pose);
        const sideOn = !turnsToViewer(posture);
        const turned = facing + (at && !sideOn ? lookToward(pose, at, facing) : 0);
        if (open < 1) pose.shutEyes(Math.min(pose.eyes, open));
        // the eyes go out as a lit visor comes on, closing to a line
        if (screen) pose.shutEyes(Math.min(pose.eyes, screen.eyes));
        // with a look in its eyes or its visor aglow, it turns toward the viewer so they are seen
        const toward = Math.max(eyes ? lookStrength(eyes) : 0, screen ? glowTurn(screen) : 0);
        if (toward && !pose.gaze && !sideOn && !clip.ownLook) turnToViewer(pose, turned, toward);
        if (eyes) lookAs(pose, eyes);
        if (screen?.sign) pose.shapeEyes(screen.sign.name, screen.sign.strength);
        const moves = place(figure, pose, turned, blend);
        const size = canvas.width * SUPERSAMPLE;
        if (this.renderer.domElement.width !== size) {
            this.renderer.setSize(size, size, false);
        }
        this.renderer.render(figure.scene, this.camera);
        const context = canvas.getContext("2d");
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.imageSmoothingQuality = "high";
        context.filter = `blur(${(SOFTEN * canvas.width) / CELL}px)`;
        context.drawImage(this.renderer.domElement, 0, 0, canvas.width, canvas.height);
        return moves;
    }

    // A parcel's block of server units (serverBlockOf) with its lights `lit` at step `phase` of their blink, drawn through the figure's own
    // camera at the scale of a figure whose picture is `picture` pixels high on the page, `ratio` canvas pixels to a page pixel: a canvas
    // just holding it, and how many page pixels of it lie below the floor
    drawBlock(lit, phase, picture, ratio) {
        if (this.blockFor !== picture) this.block = serverBlockOf(FRAMED_HEIGHT / picture);
        this.blockFor = picture;
        lightBlock(this.block, lit, phase);
        const size = Math.round(picture * ratio) * SUPERSAMPLE;
        if (this.renderer.domElement.width !== size) this.renderer.setSize(size, size, false);
        this.renderer.render(this.block.scene, this.camera);
        const {min, max} = this.block.bounds;
        const corners = [min.x, max.x].flatMap((x) => [min.y, max.y].flatMap((y) => [min.z, max.z].map((z) => new THREE.Vector3(x, y, z).project(this.camera))));
        const across = (k) => ((k + 1) / 2) * size;
        const left = Math.floor(Math.min(...corners.map((at) => across(at.x)))) - SUPERSAMPLE;
        const right = Math.ceil(Math.max(...corners.map((at) => across(at.x)))) + SUPERSAMPLE;
        const top = Math.floor(Math.min(...corners.map((at) => size - across(at.y)))) - SUPERSAMPLE;
        const bottom = Math.ceil(Math.max(...corners.map((at) => size - across(at.y)))) + SUPERSAMPLE;
        const canvas = document.createElement("canvas");
        canvas.width = Math.round((right - left) / SUPERSAMPLE);
        canvas.height = Math.round((bottom - top) / SUPERSAMPLE);
        const context = canvas.getContext("2d");
        context.imageSmoothingQuality = "high";
        context.drawImage(this.renderer.domElement, left, top, right - left, bottom - top, 0, 0, canvas.width, canvas.height);
        const floor = size - across(new THREE.Vector3(0, 0, 0).project(this.camera).y);
        return {canvas, below: (bottom - floor) / SUPERSAMPLE / ratio};
    }
}
