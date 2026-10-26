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
