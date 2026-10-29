// @vitest-environment node
import {afterEach, expect, test, vi} from "vitest";

const {draw} = vi.hoisted(() => ({draw: vi.fn(() => new Map())}));
vi.mock("../src/figure/figure.js", () => ({SIDES: {l: 1, r: -1}, reachSide: () => "r", Stage: class {draw = draw;}}));
const {FigurePlayer} = await import("../src/figure/player.js");
const clip = {name: "idle", frames: 24};
const canvas = () => ({width: 224, height: 224, getContext: () => ({clearRect() {}, drawImage() {}})});

function player() {
    vi.stubGlobal("document", {createElement: canvas});
    return new FigurePlayer({}, canvas());
}

afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    draw.mockClear();
});

test("a bug approach's walking direction reaches the pose renderer", () => {
    player().show({...clip, name: "bug_smash"}, 20, 0, {posture: "stand", stride: 0.3, walkWay: -1});
    expect(draw.mock.calls[0][5]).toMatchObject({stride: 0.3, walkWay: -1});
});

test("a held animation frame redraws when its gaze, telephone side, grab or sky pose changes", () => {
    for (const [before, after] of [
        [{at: {x: 0.2, y: 0.3}}, {at: {x: 0.8, y: 0.3}}],
        [{phoneWay: 1}, {phoneWay: -1}],
        [{grabbed: false}, {grabbed: true}],
        [{sky: {back: 0, shade: 0}}, {sky: {back: 0.5, shade: 1}}],
    ]) {
        draw.mockClear();
        const shown = player();
        shown.show(clip, 4, 0, {posture: "stand", ...before});
        shown.show(clip, 4, 0, {posture: "stand", ...after});
        expect(draw).toHaveBeenCalledTimes(2);
    }
});

test("the walk's animation phase follows measured travel, while unchanged inputs reuse the picture", () => {
    const shown = player();
    const walk = {name: "walk", frames: 12};
    shown.show(walk, 8, 90, {posture: "stand", stride: 1.25});
    expect(draw.mock.calls[0][2]).toBeCloseTo(3);
    shown.show(walk, 9, 90, {posture: "stand", stride: 1.25});
    expect(draw).toHaveBeenCalledTimes(1);
    shown.show(walk, 9, 90, {posture: "stand", stride: 1.5});
    expect(draw.mock.calls[1][2]).toBeCloseTo(6);
});

test("the run's animation phase follows measured travel through an eased start and stop", () => {
    const shown = player();
    const run = {name: "run", frames: 16};
    shown.show(run, 8, 90, {posture: "stand", stride: 0.125});
    expect(draw.mock.calls[0][2]).toBeCloseTo(2);
    shown.show(run, 9, 90, {posture: "stand", stride: 0.125});
    expect(draw).toHaveBeenCalledTimes(1);
    shown.show(run, 10, 90, {posture: "stand", stride: 0.75});
    expect(draw.mock.calls[1][2]).toBeCloseTo(12);
});

test("a continuously moving facing eases without restarting the clip blend or freezing its first frame", () => {
    let clock = 1000;
    vi.spyOn(performance, "now").mockImplementation(() => clock);
    const shown = player();
    shown.show(clip, 0, 0, {posture: "stand"});
    const nod = {name: "nod", frames: 10};
    clock += 16;
    shown.show(nod, 0, 0, {posture: "stand"});
    const began = shown.blend.began;
    const facings = [];
    for (let index = 1; index <= 15; index++) {
        clock += 16;
        shown.show(nod, index / 10, index * 2, {posture: "stand"});
        expect(shown.blend.began).toBe(began);
        facings.push(draw.mock.calls.at(-1)[3]);
    }
    expect(facings.at(-1)).toBeGreaterThan(20);
    for (let index = 1; index < facings.length; index++) expect(facings[index]).toBeGreaterThan(facings[index - 1]);
});

test("a retiring prop keeps redrawing a held frame until its fade finishes", () => {
    const shown = player();
    shown.show(clip, 0, 0, {posture: "stand"});
    shown.figure.propTransitions = {present: true, active: true};
    shown.show(clip, 0, 0, {posture: "stand"});
    expect(draw).toHaveBeenCalledTimes(2);
    expect(draw.mock.calls[1][5].time).toBeGreaterThan(0);
    shown.figure.propTransitions = {present: false, active: false};
    shown.show(clip, 0, 0, {posture: "stand"});
    expect(draw).toHaveBeenCalledTimes(2);
    shown.show(clip, 1, 0, {posture: "stand"});
    expect(draw.mock.calls[2][5].time).toBeGreaterThan(0);
});
