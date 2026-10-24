import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import FigureAct from "../src/chat/FigureAct.vue";
import {ACTS, SLUSH, bugShotScene, bugShotTimes, cameraDrops, slushAt, slushOf, sprayesCamera} from "../src/figure/acts.js";

const WORLD = {left: 0, top: 0, right: 800, bottom: 600};
const left = {wall: "left", along: 0.5, way: 0};
const top = {wall: "top", along: 0.3, way: 0};
const SPOT = {x: 8, y: 300};

async function drawn(extra) {
    const host = document.createElement("div");
    const bug = {pictures: ["data:a", "data:b"], width: 20, height: 12, at: {x: 10, y: 11}};
    createApp({render: () => h(FigureAct, {name: "bug_shot", u: 0.7, hand: {x: 0.6, y: 0.5, out: 1}, head: {x: 0.5, y: 0.3}, feet: 0.95, size: 112, room: {left: 0, right: 0}, bug, wallBugs: [], ...extra})}).mount(host);
    await nextTick();
    return host;
}

test("a shot bug bursts into slush thrown out from its wall that falls under gravity and lands on the floor or an edge of the window", () => {
    const particles = slushOf(left, WORLD, SPOT);
    expect(particles).toHaveLength(SLUSH.count);
    for (const p of particles) {
        expect(p.vx, "thrown out from the left wall").toBeGreaterThan(0);
        expect(p.t).toBeGreaterThan(0);
        expect(["floor", "left", "right", "top"]).toContain(p.on);
        expect(p.x).toBeGreaterThanOrEqual(WORLD.left);
        expect(p.x).toBeLessThanOrEqual(WORLD.right);
        expect(p.y).toBeLessThanOrEqual(WORLD.bottom);
        const [early, late] = [p.t / 3, (2 * p.t) / 3];
        const [a, b] = slushAt([p], early).concat(slushAt([p], late));
        const straight = (seconds) => p.y + p.vy * seconds;
        expect(b.y - straight(late), "it falls: lower than a straight flight by gravity").toBeCloseTo(0.5 * SLUSH.gravity * late * late, 5);
        expect(a.flying && b.flying).toBe(true);
    }
    expect(particles.some((p) => p.on === "floor"), "some land on the floor").toBe(true);
    expect(slushOf(top, WORLD, {x: 240, y: 8}).every((p) => p.vy > 0), "from the top wall they are thrown down").toBe(true);
    expect(slushOf(left, WORLD, SPOT), "the same bug bursts the same way each time").toEqual(particles);
});

test("a splash is left where each particle lands, grows, holds and fades away", () => {
    const [p] = slushOf(left, WORLD, SPOT);
    expect(slushAt([p], p.t - 0.01)[0].flying).toBe(true);
    const landed = slushAt([p], p.t + 0.001)[0];
    expect(landed).toMatchObject({flying: false, x: p.x, y: p.y, on: p.on, opacity: 1});
    const grown = slushAt([p], p.t + 0.5)[0];
    expect(grown.r).toBeGreaterThan(landed.r);
    const fading = slushAt([p], p.t + SLUSH.hold + SLUSH.fade / 2)[0];
    expect(fading.opacity).toBeGreaterThan(0);
    expect(fading.opacity).toBeLessThan(1);
    expect(slushAt([p], p.t + SLUSH.hold + SLUSH.fade + 0.01), "gone once faded").toEqual([]);
});

test("shooting a bug leaves nothing at its place: before its shot no slush, after it slush and splashes about, never a mark where it sat", () => {
    const bugs = [left];
    const {shot} = bugShotTimes(0);
    const before = bugShotScene(bugs, WORLD, (shot - 0.2) * ACTS.bug_shot.fps);
    expect(before.slush).toEqual([]);
    const after = bugShotScene(bugs, WORLD, (shot + 0.3) * ACTS.bug_shot.fps);
    expect(after.bugs[0].shot).toBe(true);
    expect(after.slush.length).toBeGreaterThan(0);
    const later = bugShotScene(bugs, WORLD, (shot + 2.5) * ACTS.bug_shot.fps);
    expect(later.slush.every((each) => !each.flying), "later only splashes").toBe(true);
    expect(bugShotScene(bugs, WORLD, (shot + SLUSH.longest + SLUSH.hold + SLUSH.fade + 1) * ACTS.bug_shot.fps).slush, "every splash faded").toEqual([]);
});

test("some bugs' slush is chosen to fly at the camera, and its drops land on the screen, then run down and fade", () => {
    const chosen = [0.01, 0.02, 0.5, 0.9].map((along) => ({...left, along}));
    expect(chosen.some(sprayesCamera) && chosen.some((bug) => !sprayesCamera(bug)), "now and then, not always").toBe(true);
    const bug = chosen.find(sprayesCamera);
    const {shot} = bugShotTimes(0);
    const scene = bugShotScene([bug], WORLD, (shot + 1) * ACTS.bug_shot.fps);
    expect(scene.camera).toHaveLength(1);
    expect(bugShotScene([chosen.find((each) => !sprayesCamera(each))], WORLD, (shot + 1) * ACTS.bug_shot.fps).camera).toEqual([]);
    const middle = {x: 56, y: 56};
    const flying = cameraDrops(0.1, 112, {x: -300, y: 40}, middle);
    const landed = cameraDrops(1, 112, {x: -300, y: 40}, middle);
    const gone = cameraDrops(10, 112, {x: -300, y: 40}, middle);
    expect(flying.every((drop) => !drop.landed)).toBe(true);
    expect(landed.every((drop) => drop.landed)).toBe(true);
    expect(landed[0].r, "bigger as it comes").toBeGreaterThan(flying[0].r);
    expect(cameraDrops(2, 112, {x: 0, y: 0}, middle)[0].run, "slides down").toBeGreaterThan(landed[0].run);
    expect(gone.every((drop) => drop.fade === 0), "faded away").toBe(true);
    expect(cameraDrops(-1, 112, {x: 0, y: 0}, middle)).toEqual([]);
});

test("the act draws the flying slush, the splashes and the camera drops, and none of them before there are any", async () => {
    const none = await drawn({});
    expect(none.querySelectorAll("[data-act-slush], [data-act-splash], [data-act-lens]").length).toBe(0);
    const host = await drawn({
        slush: [{x: 10, y: 20, r: 3, flying: true}, {x: 60, y: 100, r: 4, flying: false, on: "floor", opacity: 0.5}, {x: 5, y: 40, r: 3, flying: false, on: "left", opacity: 1}],
        camera: [{seconds: 1, from: {x: -300, y: 40}}],
    });
    expect(host.querySelectorAll("[data-act-slush]")).toHaveLength(1);
    const splashes = [...host.querySelectorAll("[data-act-splash]")];
    expect(splashes).toHaveLength(2);
    expect(splashes[0].getAttribute("opacity")).toBe("0.45");
    expect(host.querySelectorAll("[data-act-lens]").length, "one drop for each of the lens places").toBe(ACTS.bug_shot.lens.length);
    expect(host.querySelector(".figure-act-lens rect"), "landed drops run down").not.toBeNull();
});
