// @vitest-environment node
import {readFileSync} from "node:fs";
import {beforeEach, expect, test, vi} from "vitest";
import {phoneSide} from "../src/figure/perches.js";
import {CHANGE_SECONDS, SEATED, poseAfter, posedFacing} from "../src/figure/places.js";
import {turnFrame} from "../src/figure/frame.js";

const source = readFileSync(new URL("../src/chat/VoiceFigure.vue", import.meta.url), "utf8");
// Execute the component's actual frame submission with a player spy, retaining its complete options object.
const start = source.indexOf("    const facing = posedOnSeat(shown, seconds);");
const end = source.indexOf("\n    });", start) + "\n    });".length;

beforeEach(() => {
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.document = {querySelector: () => null, querySelectorAll: () => []};
});

test("a seated call reserves the same once-sampled facing submitted to the renderer, rather than the seat's canonical facing", () => {
    expect(start).toBeGreaterThan(0);
    const floor = {element: {}, left: 311, right: 380};
    const spot = {x: 347, y: 600, face: 0, posture: "sit", on: floor.element};
    const playing = {}, show = vi.fn(), posedOnSeat = vi.fn(() => 70);
    const context = {
        posedOnSeat, shown: {clip: {name: "phone_call"}}, seconds: 12,
        player: {show}, drawnClip: {value: {name: "phone_call"}}, drawnFrame: {value: 12}, drawn: "sit",
        newestAside: null, look: {eyes: null}, stride: null, backing: {value: null}, watching: null,
        body: {place: spot}, newestGlance: () => null, lookingAt: () => null, aimAt: () => null,
        blinked: () => 1, lit: null, callTicker: () => null, SEATED, playing, phoneSide,
        figureSize: () => ({size: 112, below: 0.05}), latestFloors: () => ({floors: [floor]}), flight: null,
    };
    new Function(...Object.keys(context), source.slice(start, end))(...Object.values(context));
    expect(posedOnSeat).toHaveBeenCalledTimes(1);
    expect(show).toHaveBeenCalledTimes(1);
    expect(show.mock.calls[0][2]).toBe(70);
    expect(show.mock.calls[0][3]).toMatchObject({posture: "sit", phoneWay: 1});
    expect(phoneSide(spot, context.figureSize(), [floor])).toBe(-1);
    expect(spot.face).toBe(0);
    // The hand stays selected for the call, even after another page frame is submitted.
    new Function(...Object.keys(context), source.slice(start, end))(...Object.values(context));
    expect(playing.phoneWay).toBe(1);
    delete playing.phoneWay;
    context.drawnClip.value = {name: "idle"};
    new Function(...Object.keys(context), source.slice(start, end))(...Object.values(context));
    expect(playing.phoneWay).toBeUndefined();
});

test("a call holds its displayed entry heading while the seat's idle yaw timer passes, then resumes from that heading", () => {
    const from = source.indexOf("function posedOnSeat(shown, now) {");
    const to = source.indexOf("\n}", from) + "\n}".length;
    const playing = {}, player = {facing: 23.5, turn: {speed: 48}};
    const context = {
        newestAside: null, SEATED, playing, player, posed: {posture: "sit", facing: 70, turning: false},
        seatPose: {face: 70, from: 70, to: 0, since: 1, next: 9},
        poseAfter: vi.fn(poseAfter), posedFacing,
    };
    const pose = new Function(...Object.keys(context), `${source.slice(from, to)}\nreturn posedOnSeat;`)(...Object.values(context));
    const call = {clip: {name: "phone_call"}};
    context.posed.turning = true;
    expect(pose(call, 1.4)).toBe(70);
    expect(playing.phoneFacing).toBeUndefined();
    expect(player.turn.speed).toBe(48);
    context.posed.turning = false;
    expect(pose(call, 1.5)).toBe(23.5);
    const rendered = turnFrame({facing: player.facing, speed: player.turn?.speed ?? 0}, playing.phoneFacing, 1 / 60, CHANGE_SECONDS);
    expect(rendered.facing).toBe(23.5);
    expect(rendered.settled).toBe(true);
    expect(player.facing).toBe(23.5);
    player.facing = 31;
    for (const time of [2, 5, 9, 10.4]) expect(pose(call, time)).toBe(23.5);
    expect(context.poseAfter).not.toHaveBeenCalled();
    const resumed = pose({clip: {name: "idle"}}, 10.5);
    expect(resumed).toBeCloseTo(23.5, 8);
    expect(context.poseAfter).toHaveBeenCalledTimes(1);
    expect(context.poseAfter.mock.calls[0][0]).toMatchObject({face: 70, from: 23.5, to: 23.5});
});
