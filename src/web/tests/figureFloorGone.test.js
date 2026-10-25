// @vitest-environment node
import {expect, test} from "vitest";
import {page} from "./support/figurePage.js";

const {floorOf, footingOn, footingUnder, groundUnder, readFloors} = await import("../src/figure/floors.js");
const {stayingAt} = await import("../src/figure/perches.js");
const {airborneFrame, fallingFrom} = await import("../src/domain/figureMotion.js");

const FIGURE = {size: 112, below: 0.05};
const FRAME_MS = 1000 / 60;

// a bubble of the chat the test moves, shrinks or takes off the page, whose box is then empty, as a removed element's is
function bubbleAt(top) {
    const bubble = {top, left: 260, right: 600, gone: false};
    bubble.getBoundingClientRect = () => (bubble.gone ? {left: 0, right: 0, top: 0, bottom: 0, width: 0, height: 0} : {left: bubble.left, right: bubble.right, top: bubble.top, bottom: bubble.top + 60, width: bubble.right - bubble.left, height: 60});
    page(bubble);
    return bubble;
}

// the figure standing on the bubble's right edge, where it perches, and the footing it keeps there
function standingOn(bubble) {
    const stay = {where: "bubble", perch: {floor: floorOf(bubble), kind: "stand", side: "right", grip: "", face: 0}, until: 1e9};
    const spot = stayingAt(stay, FIGURE, {x: 600, y: 600});
    return {spot, footing: footingOn(spot)};
}

// a fall from `spot` stepped frame by frame over the floors as they are now, until it lands
function fallen(spot) {
    let step = {airborne: fallingFrom(spot, null, readFloors().floors, 0), landed: null};
    for (let frame = 1; frame < 600 && !step.landed; frame++) step = airborneFrame(step.airborne, readFloors().floors, frame * FRAME_MS);
    return step.landed;
}

// whether the figure landed on the top of a floor the page has now
const onAFloorThere = (landed) => readFloors().floors.some((floor) => floor.top === landed.spot.y && floor.left <= landed.spot.x && landed.spot.x <= floor.right);

test("a figure standing on a bubble's edge falls when the bubble moves down from under its feet, and lands on a floor that is there", () => {
    const bubble = bubbleAt(400);
    const {spot, footing} = standingOn(bubble);
    expect(spot.y, "it stands on the bubble's top").toBe(400);
    bubble.top = 460;
    const ground = groundUnder(footing, spot, FIGURE, readFloors().floors);
    expect(ground.motion, "the floor it stood on went down from under it").toBe("dropping");
    const landed = fallen(spot);
    expect(landed, "it lands").not.toBe(null);
    expect(onAFloorThere(landed), `on a floor the page has now, not in mid-air at ${landed.spot.y}`).toBe(true);
});

test("a figure standing on a bubble's edge falls when the bubble leaves the page, and lands on a floor that is there", () => {
    const bubble = bubbleAt(400);
    const {spot, footing} = standingOn(bubble);
    bubble.gone = true;
    expect(readFloors().floors.some((floor) => floor.id === footing.id), "the floor reading keeps no floor whose element left the page").toBe(false);
    expect(groundUnder(footing, spot, FIGURE, readFloors().floors), "its ground went from under it").toBe(null);
    const landed = fallen(spot);
    expect(landed).not.toBe(null);
    expect(onAFloorThere(landed), `on a floor the page has now, not in mid-air at ${landed.spot.y}`).toBe(true);
});

test("a figure standing on a bubble's edge falls when the bubble narrows from under its feet", () => {
    const bubble = bubbleAt(400);
    const {spot, footing} = standingOn(bubble);
    bubble.right = spot.x - 40;
    expect(groundUnder(footing, spot, FIGURE, readFloors().floors), "its feet are past the bubble's end").toBe(null);
});

test("a bubble rising under the figure still carries it, and one moved a pixel or two keeps it standing on its top", () => {
    const bubble = bubbleAt(400);
    const {spot, footing} = standingOn(bubble);
    bubble.top = 397;
    const nudged = groundUnder(footing, spot, FIGURE, readFloors().floors);
    expect(nudged.motion).toBe("carried");
    expect(nudged.spot.y).toBe(397);
    bubble.top = 380;
    expect(groundUnder(footing, nudged.spot, FIGURE, readFloors().floors).spot.y, "carried up with it").toBe(380);
});

test("a figure standing where it keeps no footing takes the floor at its feet as it is now, and with none there it has none and falls", () => {
    const bubble = bubbleAt(400);
    const {spot} = standingOn(bubble);
    const found = footingUnder({...spot, on: null});
    expect(found && found.id, "the bubble's top at its feet").toBe(floorOf(bubble));
    bubble.top = 470;
    expect(footingUnder({...spot, on: null}), "the bubble went down: nothing at its feet").toBe(null);
    expect(onAFloorThere(fallen(spot))).toBe(true);
    expect(footingUnder({...spot, posture: "hang"}), "a hanging figure is never stood on a floor").toBe(null);
});
