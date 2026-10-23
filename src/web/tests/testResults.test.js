import {expect, test} from "vitest";
import {testResultsAfter} from "../src/domain/figureState.js";

test("any chat mark titled with the word test that ends green is a passed test run, and only once", () => {
    const known = new Map();
    const agent = (cards) => ({data: {cards}});
    const check = {key: "c1", label: "Run the TESTS", process: true, active: false, tone: "good", time: 5};
    const watch = {key: "w1", label: "pytest", watch: {figure: "Running", ending: "failed"}, time: 6};
    const build = {key: "b1", label: "Build the viewer", process: true, active: false, tone: "good", time: 7};
    expect(testResultsAfter(agent([check, watch, build]), known).map((beat) => beat.beat)).toEqual(["tests_passed", "tests_failed"]);
    expect(testResultsAfter(agent([check, watch, build]), known)).toEqual([]);
});
