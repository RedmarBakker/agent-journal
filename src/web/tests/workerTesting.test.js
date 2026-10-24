import {expect, test} from "vitest";
import {DEFAULT_TESTING, TESTINGS} from "../src/domain/modes.js";

test("the workers list offers the two ways workers test, by the words the journal keeps, handing the tests over first", () => {
    expect(TESTINGS.map((one) => one.key)).toEqual(["Hand the tests over", "Run the tests it wrote"]);
    expect(DEFAULT_TESTING).toBe("Hand the tests over");
});
