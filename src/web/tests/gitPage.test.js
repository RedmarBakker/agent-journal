import {expect, test} from "vitest";
import {distanceLine, checksLine, reviewLine, shortSha} from "../src/domain/gitPage.js";

test("the Git page words a branch's distance, a pull request's review and checks in ordinary terms", () => {
    expect(distanceLine({extra_commits: 0, missing_commits: 0})).toBe("level with the base");
    expect(distanceLine({extra_commits: 3, missing_commits: 0})).toBe("3 more than the base");
    expect(distanceLine({extra_commits: 2, missing_commits: 5})).toBe("2 more than the base, 5 fewer than the base");
    expect(checksLine({checks_passed: 0, checks_failed: 0, checks_pending: 0})).toBe("no checks");
    expect(checksLine({checks_passed: 4, checks_failed: 1, checks_pending: 2})).toBe("4 passed, 1 failed, 2 running");
    expect([{draft: true, review: ""}, {draft: false, review: "APPROVED"}, {draft: false, review: ""}].map(reviewLine)).toEqual(["draft", "approved", "not reviewed"]);
    expect(shortSha("0123456789abcdef")).toBe("0123456");
});
