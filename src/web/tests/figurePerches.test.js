// @vitest-environment node
import {beforeEach, expect, test} from "vitest";

const {CLEARED_SECONDS, HANGS, LEDGE_ALONG, LEDGE_WIDTH, STANDS, climbOf, discoBall, ledgeSpot, perchOn, swingSpot, wayUp, perchSpot, roamNext, stayAtHome, stayForLook, stepAside, targetFor} =
    await import("../src/figure/perches.js");
const {PILE, SHOWPIECES, choicesFor} = await import("../src/figure/pile.js");
const {ACTS} = await import("../src/figure/acts.js");
const {JUMP, POGO, climbStops, heightOf, jumpMost, pogoClimb} = await import("../src/figure/climbs.js");
const {legAt} = await import("../src/domain/figureMotion.js");

// the pile's places to roam to, and its share of perches that are a hang
const ROAMS = PILE.filter((entry) => entry.when.moment === "roam");
const [HANG, STAND] = PILE.filter((entry) => entry.when.moment === "perch");
const HANG_SHARE = HANG.weight / (HANG.weight + STAND.weight);
const {FEET_INBOARD, SEAT_INBOARD, boxAt, overlaps, tripTo} = await import("../src/figure/places.js");
const {write} = await import("./figurePage.js");

// a page with nothing on it a perch could hide, until a test writes words onto it, and no chat, so the figure's world is the window
beforeEach(() => {
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.document = {querySelector: () => null, querySelectorAll: () => []};
    globalThis.CSS = {escape: (text) => text};
});

const FIGURE = {size: 112, below: 0.05};
const HANDS = ["l", "r"];
const THREAD = {
    left: 250,
    right: 700,
    top: 100,
    bottom: 660,
    getBoundingClientRect() {
        return this;
    },
};

// a bubble's floor, as figure/floors.js reads it, and the floors snapshot that holds the bubbles given, in the thread's view
let issued = 0;
const bubble = (rect) => ({id: `bubble-${++issued}`, kind: "bubble", element: {rect}, ...rect});
const floorsOf = (...bubbles) => ({view: THREAD, floors: bubbles});
const at = (top, left = 260, right = 500) => bubble({left, right, top, bottom: top + 60});
const fixed =
    (...values) =>
    () =>
        values.shift() ?? 0;

test("a figure perches on the newest bubble in view first, and never on one too high or too low for it to be seen from", () => {
    const high = at(110);
    const low = at(655);
    const older = at(300);
    const newest = at(500);
    expect(perchOn(floorsOf(high, older, newest, low), FIGURE, HANDS, () => 0).floor).toBe(newest.id);
    expect(perchOn(floorsOf(high, older, low), FIGURE, HANDS, () => 0).floor).toBe(older.id);
    expect(perchOn(floorsOf(high, low), FIGURE, HANDS, () => 0)).toBe(null);
});

test("a perch whose figure would hide words is not taken: it hangs beside the bubble instead, or takes an older bubble", () => {
    const older = at(300);
    const newest = at(500);
    // words just above the newest bubble's right corner, where a seated body rises and a hanging one does not reach
    write([{left: 470, right: 520, top: 440, bottom: 470}]);
    expect(perchOn(floorsOf(older, newest), FIGURE, HANDS, () => 0.99)).toMatchObject({floor: newest.id, kind: HANGS});
    expect(perchOn(floorsOf(older, newest), FIGURE, [], () => 0.99)).toMatchObject({floor: older.id, kind: STANDS});
    expect(perchSpot({floor: newest.id, kind: STANDS, side: "right", grip: ""}, floorsOf(older, newest), FIGURE)).toBe(null);
});

test("it perches on the side of a bubble with more room outside it, and hangs or stands on its corner as the roll says", () => {
    expect(perchOn(floorsOf(at(300, 260, 500)), FIGURE, HANDS, () => 0).side).toBe("right");
    expect(perchOn(floorsOf(at(300, 450, 690)), FIGURE, HANDS, () => 0).side).toBe("left");
    expect(perchOn(floorsOf(at(300)), FIGURE, HANDS, fixed(0)).kind).toBe(HANGS);
    expect(perchOn(floorsOf(at(300)), FIGURE, HANDS, fixed(HANG_SHARE)).kind).toBe(STANDS);
    expect(perchOn(floorsOf(at(300)), FIGURE, [], fixed(0)).kind).toBe(STANDS);
});

test("a hanging figure grips the roomy corner with the hand on its side, or turns to face the bubble to grip it with its one free hand", () => {
    const right = perchOn(floorsOf(at(300, 260, 500)), FIGURE, HANDS, fixed(0));
    expect([right.grip, right.side, right.face]).toEqual(["r", "right", 0]);
    const left = perchOn(floorsOf(at(300, 450, 690)), FIGURE, HANDS, fixed(0));
    expect([left.grip, left.side, left.face]).toEqual(["l", "left", 0]);
    const only = at(300, 260, 500);
    const one = perchOn(floorsOf(only), FIGURE, ["l"], fixed(0));
    expect([one.grip, one.side, one.face]).toEqual(["l", "right", 180]);
    expect(perchSpot(one, floorsOf(only), FIGURE)).toMatchObject({face: 180, posture: "hang"});
});

test("every place the figure roams to comes up by its odds and is stayed at between its shortest and longest stay", () => {
    const total = ROAMS.reduce((sum, each) => sum + each.weight, 0);
    let before = 0;
    for (const each of ROAMS) {
        const middle = (before + each.weight / 2) / total;
        expect(roamNext(fixed(middle, 0), {free: true, swings: true})).toEqual({where: each.name, stay: each.stay[0]});
        expect(roamNext(fixed(middle, 1), {free: true, swings: true}).stay).toBe(each.stay[1]);
        before += each.weight;
    }
    expect(new Set(ROAMS.map((each) => each.name))).toEqual(new Set(["rest", "seat", "edge", "bubble", "tab", "ledge", "composed", "rope_swing"]));
});

test("mostly the figure rests on a corner of the compose box or strolls along its edge, and no stay keeps it still for long", () => {
    // of its everyday stays, the showpieces like the rope swing coming only once their long cooldown is over
    const everyday = ROAMS.filter((each) => !each.cooldown);
    const total = everyday.reduce((sum, each) => sum + each.weight, 0);
    const odds = Object.fromEntries(everyday.map((each) => [each.name, each.weight / total]));
    // it rests more than it strolls, as it walked about too much to be seen doing anything (task 2652)
    expect(odds.rest).toBe(Math.max(...Object.values(odds)));
    expect(odds.edge + odds.rest).toBeGreaterThan(0.5);
    // now and then it sits on a corner, less often than it stands there
    expect(odds.seat).toBeGreaterThan(0);
    expect(odds.seat).toBeLessThan(odds.rest);
    // it rests a while and rides a bubble up, but no stay keeps it still for long
    expect(Math.max(...ROAMS.map((each) => each.stay[1]))).toBeLessThanOrEqual(80);
});

test("a figure standing on a corner or hanging stands where its bubble's corner is, and is let go when the bubble leaves the thread's view or the page", () => {
    const one = at(300, 260, 500);
    const sitting = {floor: one.id, kind: STANDS, side: "right", grip: ""};
    const hanging = {...sitting, kind: HANGS, grip: "r", face: 0};
    expect(perchSpot(sitting, floorsOf(one), FIGURE).face).toBe(60);
    expect(perchSpot(sitting, floorsOf(one), FIGURE).on).toBe(one.element);
    // standing on the corner it keeps both feet on the bubble, its middle half its body and a margin inside the end
    expect(500 - perchSpot(sitting, floorsOf(one), FIGURE).x).toBeCloseTo(FEET_INBOARD * FIGURE.size, 5);
    expect(perchSpot(hanging, floorsOf(one), FIGURE)).toMatchObject({face: 0});
    expect(perchSpot(hanging, floorsOf(one), FIGURE).x).toBeGreaterThan(500);
    expect(perchSpot(hanging, floorsOf(one), FIGURE)).toMatchObject({y: 300, posture: "hang", grip: "r"});
    const high = at(105);
    expect(perchSpot({...sitting, floor: high.id}, floorsOf(high), FIGURE)).toBe(null);
    expect(perchSpot(sitting, floorsOf(), FIGURE)).toBe(null);
});

test("when its ground goes the figure keeps a stay at home and gives up one away from it, and a look ends a stay hanging back to the viewer", () => {
    expect(stayAtHome({where: "edge", until: 50, along: {x: 1, y: 0}})).toEqual({where: "edge", until: 50, along: {x: 1, y: 0}});
    expect(stayAtHome({where: "rest", until: 50})).toEqual({where: "rest", until: 50});
    expect(stayAtHome({where: "bubble", until: 50, perch: {}})).toEqual({where: "rest", until: 0});
    const stay = {where: "bubble", until: 50, perch: {}};
    expect(stayForLook(stay, {posture: "hang", face: 180}).until).toBe(0);
    expect(stayForLook(stay, {posture: "hang", face: 0})).toBe(stay);
    expect(stayForLook(stay, {posture: "sit", face: 60})).toBe(stay);
});

test("the figure goes home to rest while its agent cannot act, keeps a stay until it is over, and then draws the next", () => {
    const counts = {question: 0, waiting: 0, suggestion: 0};
    const at = {state: "idle", counts, now: 100, near: {x: 640, y: 800}, figure: FIGURE, hands: HANDS};
    const resting = targetFor({...at, state: "asleep", stay: {where: "edge", until: 500, along: {x: 0, y: 0}}});
    expect(resting.spot).toMatchObject({posture: "stand", y: 800});
    const edge = {where: "edge", until: 500, along: {x: 0, y: 0}};
    expect(targetFor({...at, stay: edge})).toMatchObject({stay: edge, spot: {posture: "stand"}});
    const next = targetFor({...at, stay: {...edge, until: 50}, random: () => 0});
    expect(next.stay).toMatchObject({where: ROAMS[0].name, until: 100 + ROAMS[0].stay[0]});
});

test("a perch that would put any part of the figure past the edge of its world is refused", () => {
    const edge = at(300, 1000, 1270);
    expect(perchSpot({floor: edge.id, kind: STANDS, side: "right", grip: ""}, floorsOf(edge), FIGURE)).toBe(null);
    expect(perchSpot({floor: edge.id, kind: HANGS, side: "right", grip: "r", face: 0}, floorsOf(edge), FIGURE)).toBe(null);
    expect(perchSpot({floor: edge.id, kind: STANDS, side: "left", grip: ""}, floorsOf(edge), FIGURE)).toMatchObject({posture: "stand"});
});

test("with something waiting on the user the figure keeps its stay rather than go to a tab outside its world, and points from one inside", () => {
    const tab = {
        dataset: {tab: "question"},
        getAttribute: () => "false",
        getBoundingClientRect: () => ({left: 1250, right: 1280, width: 30, top: -40, bottom: -10}),
    };
    document.querySelector = (selector) => (selector === '[data-tab="question"]' ? tab : null);
    document.querySelectorAll = (selector) => (selector === "[data-tab]" ? [tab] : []);
    const edge = {where: "edge", until: 500, along: {x: 0, y: 0}};
    const at = {
        state: "idle",
        counts: {question: 2, waiting: 0, suggestion: 0},
        now: 100,
        near: {x: 640, y: 800},
        figure: FIGURE,
        hands: HANDS,
        stay: edge,
    };
    expect(targetFor(at)).toMatchObject({stay: edge, spot: {posture: "stand", view: null, y: 800}});
    // a tab inside it past its jump is one it points at from where it is, as the pogo stick goes only onto a bubble's top
    for (const top of [200, 400]) {
        tab.getBoundingClientRect = () => ({left: 600, right: 640, width: 40, top, bottom: top + 30});
        expect(targetFor(at)).toMatchObject({stay: edge, spot: {y: 800, view: null}});
    }
    tab.getBoundingClientRect = () => ({left: 600, right: 640, width: 40, top: 640, bottom: 670});
    expect(targetFor(at)).toMatchObject({stay: edge, spot: {y: 640, view: "question", on: tab}});
});

test("a click sends the figure out of the box it was in, to a spot at home clear of it, until the box has been clear a while", () => {
    const asleep = {state: "asleep", counts: {}, now: 100, near: {x: 1200, y: 800}, figure: FIGURE, hands: HANDS};
    const seat = targetFor({...asleep, stay: {where: "rest", until: 0}}).spot;
    const {stay, cleared} = stepAside({where: "edge", until: 500}, boxAt(seat, FIGURE), 100);
    expect(stay.until).toBe(0);
    // an agent that cannot act keeps its figure resting, on the other corner
    const away = targetFor({...asleep, stay, cleared}).spot;
    expect(away.posture).toBe("stand");
    expect(overlaps(boxAt(away, FIGURE), cleared.box)).toBe(false);
    expect(targetFor({...asleep, stay, cleared, now: 100 + CLEARED_SECONDS}).spot).toEqual(seat);
    // one that roams goes wherever its next stay takes it, but never back over the box it was clicked out of
    for (const roll of [0, 0.3, 0.6, 0.99]) {
        const roams = {...asleep, state: "idle", stay, cleared, random: () => roll};
        expect(overlaps(boxAt(targetFor(roams).spot, FIGURE), cleared.box), `roll ${roll}`).toBe(false);
    }
});

test("a hang whose feet would reach the ground at home is no perch, since the figure would let go the moment it landed and roll it again", () => {
    const low = at(560);
    const home = {id: "home", kind: "home", element: {}, left: 250, right: 700, top: 600, bottom: 660};
    expect(perchSpot({floor: low.id, kind: HANGS, side: "right", grip: "r", face: 0}, floorsOf(low, home), FIGURE)).toBe(null);
    expect(perchSpot({floor: low.id, kind: STANDS, side: "right", grip: ""}, floorsOf(low, home), FIGURE)).toMatchObject({posture: "stand"});
    expect(perchSpot({floor: low.id, kind: HANGS, side: "right", grip: "r", face: 0}, floorsOf(low), FIGURE)).toMatchObject({posture: "hang"});
});

test("while its agent runs a test suite or a build and the run was granted a unit, the figure goes down onto the compose box's top to build, under any bars docked over it, beside its parcel", () => {
    const box = (rect) => ({...rect, width: rect.right - rect.left, height: rect.bottom - rect.top});
    const bars = {getBoundingClientRect: () => box({left: 300, right: 900, top: 640, bottom: 700})};
    const thread = {querySelector: (selector) => (selector === "[data-figure-docked-bars]" ? bars : null), getBoundingClientRect: () => box({left: 250, right: 950, top: 0, bottom: 800})};
    const home = {getBoundingClientRect: () => box({left: 300, right: 900, top: 700, bottom: 780}), closest: () => thread};
    document.querySelector = (selector) => (selector === "[data-figure-home]" ? home : null);
    const running = {state: "testing", counts: {question: 1, waiting: 0, suggestion: 0}, now: 100, near: {x: 800, y: 640}, figure: FIGURE, hands: HANDS, stay: {where: "rest", until: 0}, work: {beside: 0}};
    const spot = targetFor(running).spot;
    // with no unit granted it does not go to build at all
    expect(targetFor({...running, work: null}).spot.stays).toBeUndefined();
    expect(spot).toMatchObject({y: 700, posture: "stand", on: home, stays: true, view: null});
    // a box the figure was clicked out of does not move it from where it builds
    const cleared = {box: boxAt(spot, FIGURE), until: 200};
    expect(targetFor({...running, cleared}).spot).toEqual(spot);
    expect(targetFor({...running, work: {x: 528, beside: -28}}).spot).toMatchObject({x: 528, y: 700, stays: true});
    // a parcel left to push takes the figure onto the compose box's top whatever its agent does
    expect(targetFor({...running, state: "thinking", work: {x: 610}}).spot).toMatchObject({x: 610, y: 700, stays: true});
    // a new parcel is built clear of the pile at the floor's right end
    const clear = targetFor({...running, work: {beside: 28, before: 700}}).spot;
    expect(clear.x + 28 + 24).toBeLessThan(700);
    expect(targetFor({...running, state: "thinking", work: null}).spot.stays).toBeUndefined();
});

test("now and then the figure lounges at a corner, back from the end, side-on with its legs along the floor away from the end, and lounges there at its laptop while its agent edits", () => {
    const box = (rect) => ({...rect, width: rect.right - rect.left, height: rect.bottom - rect.top});
    const thread = {querySelector: () => null, getBoundingClientRect: () => box({left: 236, right: 778, top: 0, bottom: 900})};
    const home = {getBoundingClientRect: () => box({left: 258, right: 754, top: 768, bottom: 888}), closest: () => thread};
    document.querySelector = (selector) => (selector === "[data-figure-home]" ? home : null);
    const at = {counts: {question: 0, waiting: 0, suggestion: 0}, now: 100, figure: FIGURE, hands: HANDS};
    // a stay sitting: on the corner nearest, back from its end on the top, side-on with its legs out along the floor away from the end
    const right = targetFor({...at, state: "idle", near: {x: 700, y: 768}, stay: {where: "seat", until: 500}}).spot;
    expect(right).toMatchObject({x: 754 - SEAT_INBOARD * FIGURE.size, y: 768, posture: "lounge", face: 270, on: home});
    const left = targetFor({...at, state: "idle", near: {x: 300, y: 768}, stay: {where: "seat", until: 500}}).spot;
    expect(left).toMatchObject({x: 258 + SEAT_INBOARD * FIGURE.size, posture: "lounge", face: 90});
    // far enough in that its whole picture is inside the chat, nothing over the end
    expect(boxAt(right, FIGURE).right).toBeLessThanOrEqual(778);
    expect(SEAT_INBOARD).toBeGreaterThan(FEET_INBOARD);
    // editing, it goes to lounge at its laptop on a corner
    expect(targetFor({...at, state: "writing", near: {x: 700, y: 768}, stay: {where: "edge", until: 500, along: {x: 400, y: 0}}}).spot).toMatchObject({posture: "lounge", x: 754 - SEAT_INBOARD * FIGURE.size});
});

test("resting by its parcel pile the figure stands beside it, never in front of the parcels, and may sit on the edge there", () => {
    const box = (rect) => ({...rect, width: rect.right - rect.left, height: rect.bottom - rect.top});
    const thread = {querySelector: () => null, getBoundingClientRect: () => box({left: 236, right: 778, top: 0, bottom: 900})};
    const home = {getBoundingClientRect: () => box({left: 258, right: 754, top: 768, bottom: 888}), closest: () => thread};
    document.querySelector = (selector) => (selector === "[data-figure-home]" ? home : null);
    const pile = {left: 691, right: 740, top: 768};
    const at = {state: "idle", counts: {question: 0, waiting: 0, suggestion: 0}, now: 100, figure: FIGURE, hands: HANDS, near: {x: 720, y: 768}, pile};
    const body = (spot) => [spot.x - 0.15 * FIGURE.size, spot.x + 0.15 * FIGURE.size];
    // the corner it rests on stands where the pile is: it stands beside the pile instead
    const plain = targetFor({...at, pile: null, stay: {where: "rest", until: 500}}).spot;
    expect(body(plain)[1]).toBeGreaterThan(pile.left);
    const beside = targetFor({...at, stay: {where: "rest", until: 500}}).spot;
    expect(beside).toMatchObject({posture: "stand", y: 768});
    expect(body(beside)[1]).toBeLessThanOrEqual(pile.left);
    // sitting on the edge by the pile is left as it is
    expect(targetFor({...at, stay: {where: "seat", until: 500}}).spot).toMatchObject({posture: "lounge", x: 754 - SEAT_INBOARD * FIGURE.size});
    // a figure standing on another floor is not moved
    expect(targetFor({...at, pile: {...pile, top: 600}, stay: {where: "rest", until: 500}}).spot.x).toBe(plain.x);
});

test("now and then the figure sits down halfway or a third or two thirds along a floor, never near an end, lounging side-on on the composer", () => {
    const box = (rect) => ({...rect, width: rect.right - rect.left, height: rect.bottom - rect.top});
    const thread = {querySelector: () => null, getBoundingClientRect: () => box({left: 236, right: 778, top: 0, bottom: 900})};
    const home = {getBoundingClientRect: () => box({left: 258, right: 754, top: 768, bottom: 888}), closest: () => thread};
    document.querySelector = (selector) => (selector === "[data-figure-home]" ? home : null);
    const width = 754 - 258;
    // the only places along are the middle, a third and two thirds, so it is always a third of the floor or more from either end
    expect([...LEDGE_ALONG].sort()).toEqual([1 / 3, 1 / 2, 2 / 3].sort());
    for (const along of LEDGE_ALONG) {
        const spot = ledgeSpot(along, FIGURE, {on: home});
        expect(spot).toMatchObject({x: 258 + width * along, y: 768, posture: "lounge", face: along <= 0.5 ? 90 : 270, leans: false, on: home});
        expect(Math.min(spot.x - 258, 754 - spot.x)).toBeGreaterThanOrEqual(width / 3 - 1e-9);
    }
    // a stay on the ledge takes the figure there
    const at = {state: "idle", counts: {question: 0, waiting: 0, suggestion: 0}, now: 100, figure: FIGURE, hands: HANDS, near: {x: 300, y: 768, on: home}};
    expect(targetFor({...at, stay: {where: "ledge", until: 500, along: 1 / 3}}).spot).toMatchObject({x: 258 + width * (1 / 3), posture: "lounge"});
    // where its body would hide words it takes another of the three places, never one nearer an end
    write([{left: 258 + width / 2 - 60, right: 258 + width / 2 + 60, top: 700, bottom: 760}]);
    expect(ledgeSpot(1 / 2, FIGURE, {on: home}).x).toBe(258 + width * (1 / 3));
    // a floor too short to sit a third along with room to spare is no ledge
    home.getBoundingClientRect = () => box({left: 258, right: 258 + LEDGE_WIDTH * FIGURE.size - 1, top: 768, bottom: 888});
    expect(ledgeSpot(1 / 2, FIGURE, {on: home})).toBe(null);
});

test("no jump goes higher than its one limit: a climb is as many hops as its height needs, each onto a bubble on the way, and a salto turns only on a jump up", () => {
    const most = jumpMost(FIGURE);
    expect(most).toBeCloseTo(JUMP.most * (1 - FIGURE.below - 0.15) * FIGURE.size);
    // footholds a bubble's height apart, as a thread's bubbles stand, from the ground at 800 up
    const holds = Array.from({length: 12}, (_, index) => ({x: 300 + (index % 2) * 120, y: 740 - index * 60}));
    const from = {x: 300, y: 800};
    const counts = [];
    for (const height of [100, 300, 520, 700]) {
        const stops = climbStops(from, from.y - height, holds, most);
        const feet = [from, ...stops, {y: from.y - height}];
        for (let hop = 1; hop < feet.length; hop++) {
            expect(feet[hop - 1].y - feet[hop].y, `${height}: hop ${hop}`).toBeLessThanOrEqual(most);
            expect(feet[hop].y).toBeLessThan(feet[hop - 1].y);
        }
        counts.push(feet.length - 1);
    }
    // the higher the climb the more hops, never a fixed count
    expect(counts).toEqual([...counts].sort((a, b) => a - b));
    expect(new Set(counts).size).toBe(counts.length);
    expect(counts[0]).toBe(1);
    // with no foothold in reach on the way a climb too high for one hop is refused, and one in reach is a single hop
    expect(climbStops(from, from.y - most - 1, [], most)).toBe(null);
    expect(climbStops(from, from.y - most + 1, [], most)).toEqual([]);
    // on the page the footholds are the bubbles' corners, and a trip up hops from each to the next, never higher than the limit
    const floors = floorsOf(at(560), at(400, 420, 660), at(240));
    const via = climbOf(floors, FIGURE, {x: 300, y: 660}, 240);
    expect(via.length).toBeGreaterThan(0);
    const top = perchSpot({floor: floors.floors[2].id, kind: STANDS, side: "right", grip: ""}, floors, FIGURE);
    const legs = tripTo({x: 300, y: 660, posture: "stand"}, top, FIGURE, {via}).legs;
    const hops = legs.filter((leg) => leg.hopping);
    expect(hops.length).toBe(via.length + 1);
    hops.reduce((y, hop) => (expect(y - hop.y).toBeLessThanOrEqual(most), hop.y), legs[0].y);
    expect(climbOf(floorsOf(at(240)), FIGURE, {x: 300, y: 660}, 240)).toBe(null);
    // the salto is no idle act any more: it only turns now and then on a high jump up onto a bubble
    expect(PILE.filter((entry) => entry.name === "salto")).toEqual([]);
    expect(PILE.filter((entry) => entry.name === "backflip").map((entry) => entry.when)).toEqual([{moment: "jump", high: true}]);
    expect(choicesFor({moment: "jump", high: false}).map((entry) => entry.name)).toEqual(["jump"]);
});

test("now and then the figure swings on a rope tied under a bubble near the middle of the chat, never under one too near its side", () => {
    // a bubble near the middle: the seat hangs a rope's length below the middle of its bottom edge, the figure on it facing the viewer
    const middle = bubble({left: 500, right: 780, top: 300, bottom: 360});
    const spot = swingSpot(middle, FIGURE, floorsOf(middle));
    expect(spot).toMatchObject({x: 640, y: 360 + ACTS.rope_swing.rope * FIGURE.size, posture: "sit", face: 0, swings: true, on: middle.element});
    // one whose bottom edge's middle sits too near the chat's left or right side has no room to swing
    for (const side of [bubble({left: 10, right: 150, top: 300, bottom: 360}), bubble({left: 1150, right: 1270, top: 300, bottom: 360})]) {
        expect((side.left + side.right) / 2 < ACTS.rope_swing.room * FIGURE.size || 1280 - (side.left + side.right) / 2 < ACTS.rope_swing.room * FIGURE.size).toBe(true);
        expect(swingSpot(side, FIGURE, floorsOf(side))).toBe(null);
    }
    // nor one so low that the figure's legs would hang below the ground at home
    const home = {id: "home", kind: "compose", left: 260, right: 1000, top: 440};
    expect(swingSpot(middle, FIGURE, floorsOf(middle, home))).toBe(null);
    // it is a showpiece of the pile, for the idle figure under a bubble it may swing from, waiting fifteen minutes before it swings again
    const entry = PILE.find((each) => each.name === "rope_swing");
    expect(entry).toMatchObject({when: {moment: "roam", free: true, swings: true}, cooldown: SHOWPIECES.rope_swing, shenanigan: true});
    expect(SHOWPIECES.rope_swing).toBe(15 * 60);
    const offers = (scene) => choicesFor({moment: "roam", free: true, ...scene}).some((each) => each.name === "rope_swing");
    expect(offers({swings: false})).toBe(false);
    const memory = new Map([["roam/rope_swing", 0]]);
    expect(offers({swings: true, memory, now: 600})).toBe(false);
    expect(offers({swings: true, memory, now: 900})).toBe(true);
});

test("a climb past three of its heights onto a bubble's top goes now and then on a pogo stick, the one jump that goes past the plain limit, and always when no bubble is on the way", () => {
    const tall = heightOf(FIGURE);
    const from = {x: 400, y: 700};
    // only a climb past three heights and within six is one for the stick; the plain jump stops at two and a half
    expect(pogoClimb(FIGURE, 2.9 * tall)).toBe(false);
    expect(pogoClimb(FIGURE, 3.1 * tall)).toBe(true);
    expect(pogoClimb(FIGURE, POGO.most * tall + 1)).toBe(false);
    expect(JUMP.most).toBeLessThan(POGO.over);
    // the bubble it climbs onto, its top `up` of its heights over the feet, and the spot standing on it
    const goal = (up) => at(700 - up * tall, 330, 470);
    const onTop = (floor) => ({x: 400, y: floor.top, posture: "stand", on: floor.element});
    // with no other bubble on the way: a climb within the plain jump is one hop, one past three heights is on the stick, one between can't be made
    const [low, mid, high] = [goal(2), goal(2.8), goal(4)];
    expect(wayUp(floorsOf(low), FIGURE, from, onTop(low), {}, () => 0)).toEqual({via: [], pogo: false});
    expect(wayUp(floorsOf(mid), FIGURE, from, onTop(mid), {}, () => 0)).toBe(null);
    expect(wayUp(floorsOf(high), FIGURE, from, onTop(high), {}, () => 0.99)).toEqual({via: [], pogo: true});
    // with bubbles to hop up on, the roll picks the stick or the hops
    const steps = floorsOf(at(700 - 1.6 * tall, 330, 470), at(700 - 3.2 * tall, 330, 470), high);
    expect(wayUp(steps, FIGURE, from, onTop(high), {}, () => 0).pogo).toBe(true);
    expect(wayUp(steps, FIGURE, from, onTop(high), {}, () => 0.99).pogo).toBe(false);
    // the stick waits its cooldown: inside it, the hops, or no way up with none to hop on
    const memory = new Map();
    expect(wayUp(floorsOf(high), FIGURE, from, onTop(high), {memory, now: 0}, () => 0).pogo).toBe(true);
    expect(wayUp(floorsOf(high), FIGURE, from, onTop(high), {memory, now: 60}, () => 0)).toBe(null);
    expect(wayUp(steps, FIGURE, from, onTop(high), {memory, now: 60}, () => 0).pogo).toBe(false);
    // on the stick it bounces on the spot, higher each time, then springs up the whole way in one, past the plain jump's limit
    const legs = tripTo({x: 400, y: 700, posture: "stand"}, {x: 400, y: 700 - 4 * tall, posture: "stand"}, FIGURE, {pogo: true}).legs;
    const leg = legs.find((each) => each.pogo);
    expect(leg).toMatchObject({hopping: true, clip: "pogo"});
    const start = {x: legs[0].x, y: legs[0].y};
    const heights = Array.from({length: 61}, (_, step) => start.y - legAt(leg, start, (leg.ms * step) / 60).y);
    expect(Math.max(...heights.slice(0, 36))).toBeGreaterThan(0);
    expect(Math.max(...heights.slice(0, 36))).toBeLessThan(jumpMost(FIGURE));
    expect(start.y - leg.y).toBeGreaterThan(jumpMost(FIGURE));
    expect(legAt(leg, start, leg.ms)).toEqual({x: leg.x, y: leg.y});
});

test("the pogo stick is only ever the way up onto a bubble's top, where the figure lands standing: never to a hang from a bubble, a seat on it or a tab", () => {
    const tall = heightOf(FIGURE);
    const from = {x: 400, y: 700};
    const high = at(700 - 4 * tall, 330, 470);
    const floors = floorsOf(high);
    const spot = {x: 400, y: high.top, on: high.element};
    // standing on its top, the stick; with every roll, as the pile has no footholds to offer instead
    for (const roll of [0, 0.5, 0.99]) expect(wayUp(floors, FIGURE, from, {...spot, posture: "stand"}, {}, () => roll)).toEqual({via: [], pogo: true});
    // a hang from its side, a seat on it or the composed sit there: no stick, and with nothing to hop on no way up at all
    for (const posture of ["hang", "lounge", "sit", "composed"]) {
        for (const roll of [0, 0.5, 0.99]) expect(wayUp(floors, FIGURE, from, {...spot, posture}, {}, () => roll), posture).toBe(null);
    }
    // nor standing anywhere that is not a bubble, as a tab
    expect(wayUp(floors, FIGURE, from, {...spot, posture: "stand", on: {rect: {}}}, {}, () => 0)).toBe(null);
    // and with bubbles to hop up on, a hang goes by the hops, every roll
    const steps = floorsOf(at(700 - 1.6 * tall, 330, 470), at(700 - 3.2 * tall, 330, 470), high);
    for (const roll of [0, 0.5, 0.99]) expect(wayUp(steps, FIGURE, from, {...spot, posture: "hang"}, {}, () => roll).pogo).toBe(false);
});

test("the disco dance plays only standing on a bubble with another above it to hang the ball from, and then only on a rare occasion", () => {
    const tall = heightOf(FIGURE);
    // standing on a bubble with another above it, near enough and with room between for the ball: the ball hangs from that one's bottom
    const under = bubble({left: 300, right: 600, top: 500, bottom: 560});
    const over = bubble({left: 280, right: 620, top: 300, bottom: 500 - tall - 60});
    const standing = {x: 450, y: 500, posture: "stand", on: under.element};
    const tied = discoBall(standing, FIGURE, floorsOf(under, over));
    expect(tied).toMatchObject({kind: "bubble", above: 500 - over.bottom});
    expect(tied.hangs).toBeGreaterThan(tall);
    expect(tied.above).toBeGreaterThan(tied.hangs);
    // the bubble above too near the hat for the ball: no room at all
    const low = bubble({left: 280, right: 620, top: 300, bottom: 500 - tall - 10});
    expect(discoBall(standing, FIGURE, floorsOf(under, low))).toBe(null);
    // nothing above to hang it from, or standing on the compose box under a bubble: no ball
    expect(discoBall(standing, FIGURE, floorsOf(under))).toBe(null);
    expect(discoBall({x: 450, y: 700, posture: "stand", on: {}}, FIGURE, floorsOf(over))).toBe(null);
    // the bubble above moved further up, as the chat lays out again: the string is tied to where it is now
    const higher = bubble({left: 280, right: 620, top: 260, bottom: 500 - tall - 90});
    expect(discoBall(standing, FIGURE, floorsOf(under, higher))).toMatchObject({kind: "bubble", above: 500 - higher.bottom});
    // no ball sitting or hanging
    expect(discoBall({...standing, posture: "sit"}, FIGURE, floorsOf(under, over))).toBe(null);
    // the pile has it only under a bubble, and rarely: under one draw in fifty of the idle acts
    const choices = (ball) => choicesFor({moment: "pastime", ball, free: true, lasted: 1000});
    const weight = (ball) => choices(ball).filter((each) => each.name === "disco").reduce((sum, each) => sum + each.weight, 0);
    expect(weight("")).toBe(0);
    expect(weight("bubble")).toBeGreaterThan(0);
    expect(weight("bubble") / choices("bubble").reduce((sum, each) => sum + each.weight, 0)).toBeLessThan(1 / 50);
    const memory = new Map([["pastime/disco", 0]]);
    expect(choicesFor({moment: "pastime", ball: "bubble", memory, now: 15 * 60 - 1}).some((each) => each.name === "disco")).toBe(false);
    expect(choicesFor({moment: "pastime", ball: "bubble", memory, now: SHOWPIECES.disco}).some((each) => each.name === "disco")).toBe(true);
    expect(SHOWPIECES.disco).toBe(15 * 60);
});

test("on a bubble the figure keeps 20 pixels inside the chat's sides, so a side never cuts its frame; a corner against a side is no perch", async () => {
    const {WALL_ROOM} = await import("../src/figure/places.js");
    const against = at(300, 900, 1270);
    const roomy = at(300, 900, 1180);
    const corner = (bubble) => perchSpot({floor: bubble.id, kind: STANDS, side: "right", grip: ""}, floorsOf(bubble), FIGURE);
    expect(corner(against)).toBe(null);
    expect(boxAt(corner(roomy), FIGURE).right).toBeLessThanOrEqual(1280 - WALL_ROOM);
});
