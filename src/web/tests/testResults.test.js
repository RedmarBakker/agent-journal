import {expect, test} from "vitest";
import {testResultsAfter} from "../src/domain/figureState.js";

test("any chat mark titled with the word test that ends green is a passed test run, and only once", () => {
    const known = new Map();
    const agent = (cards) => ({data: {cards}});
    const check = {key: "c1", label: "Run the TESTS", guesses: {test: true}, process: true, active: false, tone: "good", time: 5};
    const watch = {key: "w1", label: "pytest", guesses: {test: true}, watch: {figure: "Running", ending: "failed"}, time: 6};
    const build = {key: "b1", label: "Build the viewer", process: true, active: false, tone: "good", time: 7};
    expect(testResultsAfter(agent([check, watch, build]), known).map((beat) => beat.beat)).toEqual(["tests_passed", "tests_failed"]);
    expect(testResultsAfter(agent([check, watch, build]), known)).toEqual([]);
});

test("a pass soon after a failed test run is the failure fixed and has its chance at the bug shot; a pass after a pass, or long after, is a plain pass", async () => {
    const {FIX_SECONDS} = await import("../src/domain/figureState.js");
    const {PILE} = await import("../src/figure/pile.js");
    const of = (moment) => PILE.filter((each) => each.when.moment === moment);
    const run = (key, time, ending) => ({key, label: "Running tests", guesses: {test: true}, time, watch: {figure: "", ending}});
    const beats = (cards) => testResultsAfter({data: {cards}}, new Map()).map((beat) => beat.beat);
    expect(beats([run("a", 10, "failed with code 1"), run("b", 20, "finished")])).toEqual(["tests_failed", "tests_fixed"]);
    expect(beats([run("a", 10, "finished"), run("b", 20, "finished")])).toEqual(["tests_passed", "tests_passed"]);
    expect(beats([run("a", 10, "failed with code 1"), run("b", 20 + FIX_SECONDS, "finished")])).toEqual(["tests_failed", "tests_passed"]);
    expect(of("tests_fixed").map((each) => each.name)).toContain("bug_shot");
    expect(of("tests_passed").map((each) => each.name)).not.toContain("bug_shot");
});

test("one failed run gives one failure beat, however many looks see it and whatever comes and goes around it", () => {
    const known = new Map();
    const failed = {key: "f", label: "Running tests", guesses: {test: true}, time: 10, watch: {figure: "", ending: "failed with code 1"}};
    const other = (n) => ({key: `o${n}`, label: "Build the viewer", process: true, active: n % 2 === 0, tone: "good", time: 10 + n});
    const looks = Array.from({length: 12}, (_, n) => testResultsAfter({data: {cards: n % 3 ? [other(n), failed] : [failed]}}, known));
    expect(looks.flat().filter((beat) => beat.beat === "tests_failed")).toHaveLength(1);
});
